"""
Custom OAuth2 Email Backend for Microsoft 365.

This backend uses OAuth2 authentication with Microsoft's MSAL library
to send emails via Office 365 SMTP server using the XOAUTH2 mechanism.

Features:
- OAuth2 token acquisition using client credentials flow
- Automatic token caching and refresh
- Thread-safe token management
- Comprehensive error handling and logging
- SMTP AUTH XOAUTH2 support

Security:
- Uses environment variables for credentials
- No secrets stored in code
- Proper token lifecycle management
"""

import base64
import logging
import smtplib
import threading
from smtplib import SMTPAuthenticationError, SMTPException
from typing import Optional

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)


class OAuth2EmailBackend(EmailBackend):
    """
    Custom email backend that uses OAuth2 for Microsoft 365 authentication.

    This backend extends Django's SMTP EmailBackend to support OAuth2
    authentication using the XOAUTH2 SMTP authentication mechanism.
    """

    # Class-level token cache (thread-safe)
    _token_cache = {}
    _token_lock = threading.Lock()

    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        """
        Initialize the OAuth2 email backend.

        IMPORTANT: We must call super().__init__() with all parameters to ensure
        Django's SMTP backend is properly initialized with all required attributes.
        """
        # Call parent __init__ to properly initialize all SMTP attributes
        # This sets up: host, port, username, password, use_tls, use_ssl,
        # timeout, ssl_keyfile, ssl_certfile, ssl_keyfile_password_kwargs, etc.
        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            fail_silently=fail_silently,
            use_ssl=use_ssl,
            timeout=timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            **kwargs
        )

        # Get OAuth2 credentials from settings
        self.client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'MICROSOFT_CLIENT_SECRET', '')
        self.tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', '')

        # Validate credentials are set
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            logger.warning(
                "OAuth2 credentials not fully configured. "
                "Set MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, and MICROSOFT_TENANT_ID."
            )

        # MSAL application instance (lazy initialization)
        self._msal_app: Optional[ConfidentialClientApplication] = None

    @property
    def msal_app(self) -> ConfidentialClientApplication:
        """
        Get or create MSAL application instance.
        Lazy initialization to avoid creating app when not needed.
        """
        if self._msal_app is None:
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            self._msal_app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=authority
            )
        return self._msal_app

    def get_access_token(self) -> str:
        """
        Acquire OAuth2 access token for Office 365 SMTP.

        Uses client credentials flow (app-only authentication).
        Tokens are cached and reused until expiration.

        Returns:
            str: Access token for authenticating to SMTP server

        Raises:
            SMTPAuthenticationError: If token acquisition fails
        """
        # Check if we have valid credentials
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise SMTPAuthenticationError(
                0,
                "OAuth2 credentials not configured. Please set MICROSOFT_CLIENT_ID, "
                "MICROSOFT_CLIENT_SECRET, and MICROSOFT_TENANT_ID environment variables."
            )

        # Thread-safe token acquisition
        with self._token_lock:
            cache_key = f"{self.client_id}:{self.tenant_id}"

            # Check cache first
            if cache_key in self._token_cache:
                cached_token = self._token_cache[cache_key]
                logger.debug("Using cached OAuth2 token")
                return cached_token

            try:
                # Scopes for Office 365 SMTP access
                scopes = ["https://outlook.office365.com/.default"]

                logger.info("Acquiring OAuth2 access token from Microsoft...")

                # Acquire token using client credentials flow
                result = self.msal_app.acquire_token_for_client(scopes=scopes)

                if "access_token" in result:
                    access_token = result["access_token"]

                    # Cache the token (MSAL handles expiration internally)
                    self._token_cache[cache_key] = access_token

                    logger.info("OAuth2 access token acquired successfully")
                    return access_token
                else:
                    # Token acquisition failed
                    error = result.get("error", "unknown_error")
                    error_description = result.get("error_description", "No description provided")

                    logger.error(
                        f"Failed to acquire OAuth2 token: {error} - {error_description}"
                    )

                    raise SMTPAuthenticationError(
                        0,
                        f"OAuth2 token acquisition failed: {error}. "
                        f"Check your Azure app registration and credentials. "
                        f"Details: {error_description}"
                    )

            except SMTPAuthenticationError:
                # Re-raise authentication errors
                raise
            except Exception as e:
                logger.error(f"Exception during OAuth2 token acquisition: {str(e)}")
                raise SMTPAuthenticationError(
                    0,
                    f"Failed to acquire OAuth2 token: {str(e)}"
                )

    def generate_oauth2_string(self, user: str, access_token: str) -> str:
        """
        Generate the OAuth2 authentication string for SMTP XOAUTH2.

        Format: user=USER\x01auth=Bearer TOKEN\x01\x01
        Encoded in base64.

        Args:
            user: Email address (e.g., admin@diasporaenterprise.com)
            access_token: OAuth2 access token

        Returns:
            str: Base64-encoded OAuth2 authentication string
        """
        auth_string = f"user={user}\x01auth=Bearer {access_token}\x01\x01"
        return base64.b64encode(auth_string.encode()).decode()

    def open(self):
        """
        Open connection to SMTP server and authenticate using OAuth2.

        This method overrides the parent class's open() method to use
        OAuth2 authentication instead of username/password.

        Returns:
            bool: True if connection opened, False if already open
        """
        if self.connection:
            # Already have an open connection
            return False

        try:
            # Create SMTP connection
            connection_params = {
                'timeout': self.timeout,
                'local_hostname': None,
            }

            try:
                if self.use_ssl:
                    # Use SMTP_SSL for SSL connections
                    self.connection = smtplib.SMTP_SSL(
                        self.host,
                        self.port,
                        **connection_params
                    )
                else:
                    # Use regular SMTP
                    self.connection = smtplib.SMTP(
                        self.host,
                        self.port,
                        **connection_params
                    )
            except Exception as e:
                logger.error(f"Failed to connect to SMTP server: {str(e)}")
                raise

            # Send EHLO
            self.connection.ehlo()

            # Start TLS if required (and not already using SSL)
            if self.use_tls and not self.use_ssl:
                self.connection.starttls()
                self.connection.ehlo()

            # Authenticate using OAuth2
            logger.info("Authenticating using OAuth2...")

            # Get access token
            access_token = self.get_access_token()

            # Get the email address to authenticate as
            # Use EMAIL_HOST_USER from settings, or fall back to DEFAULT_FROM_EMAIL
            user_email = getattr(settings, 'EMAIL_HOST_USER', None)
            if not user_email:
                user_email = settings.DEFAULT_FROM_EMAIL

            # Generate OAuth2 auth string
            oauth2_string = self.generate_oauth2_string(user_email, access_token)

            # Authenticate using XOAUTH2
            self.connection.ehlo()

            # Use the SMTP AUTH command with XOAUTH2
            # The AUTH XOAUTH2 command expects the base64-encoded auth string
            code, response = self.connection.docmd(
                "AUTH XOAUTH2",
                oauth2_string
            )

            if code != 235:  # 235 = Authentication successful
                error_msg = response.decode() if isinstance(response, bytes) else str(response)
                logger.error(f"OAuth2 authentication failed with code {code}: {error_msg}")
                raise SMTPAuthenticationError(
                    code,
                    f"OAuth2 authentication failed: {error_msg}"
                )

            logger.info("OAuth2 authentication successful")
            return True

        except SMTPException as e:
            logger.error(f"SMTP error during connection: {str(e)}")
            # Close any partial connection
            if self.connection:
                try:
                    self.connection.quit()
                except:
                    pass
                self.connection = None
            if not self.fail_silently:
                raise
            return False

        except Exception as e:
            logger.error(f"Unexpected error during SMTP connection: {str(e)}")
            # Close any partial connection
            if self.connection:
                try:
                    self.connection.quit()
                except:
                    pass
                self.connection = None
            if not self.fail_silently:
                raise
            return False

    @classmethod
    def clear_token_cache(cls):
        """
        Clear the OAuth2 token cache.
        Useful for testing or forcing token refresh.
        """
        with cls._token_lock:
            cls._token_cache.clear()
            logger.info("OAuth2 token cache cleared")
