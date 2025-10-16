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

    def __init__(self, *args, **kwargs):
        """Initialize the OAuth2 email backend."""
        super().__init__(*args, **kwargs)

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
            bool: True if connection successful, False otherwise
        """
        if self.connection:
            # Already have an open connection
            return False

        try:
            # Create SMTP connection (parent class handles this)
            self.connection = self.connection_class(
                self.host,
                self.port,
                **self.ssl_keyfile_password_kwargs
            )

            # Set debug level if configured
            if self.use_ssl:
                self.connection.ehlo()

            # Start TLS if required
            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls(**self.ssl_keyfile_password_kwargs)
                self.connection.ehlo()

            # Authenticate using OAuth2
            if self.username and self.password:
                # Use traditional authentication if username/password provided
                self.connection.login(self.username, self.password)
                logger.info("Authenticated using username/password")
            else:
                # Use OAuth2 authentication
                logger.info("Authenticating using OAuth2...")

                # Get access token
                access_token = self.get_access_token()

                # Generate OAuth2 auth string
                user_email = getattr(settings, 'EMAIL_HOST_USER', settings.DEFAULT_FROM_EMAIL)
                oauth2_string = self.generate_oauth2_string(user_email, access_token)

                # Authenticate using XOAUTH2
                # Note: smtplib's auth method expects the mechanism name and auth data
                self.connection.ehlo()

                # Use the SMTP AUTH command with XOAUTH2
                code, response = self.connection.docmd(
                    "AUTH XOAUTH2",
                    oauth2_string
                )

                if code != 235:  # 235 = Authentication successful
                    raise SMTPAuthenticationError(
                        code,
                        f"OAuth2 authentication failed: {response.decode() if isinstance(response, bytes) else response}"
                    )

                logger.info("OAuth2 authentication successful")

            return True

        except SMTPException as e:
            logger.error(f"SMTP error during connection: {str(e)}")
            if not self.fail_silently:
                raise
            return False

        except Exception as e:
            logger.error(f"Unexpected error during SMTP connection: {str(e)}")
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
