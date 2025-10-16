"""
Management command to test email configuration with OAuth2 support.
Usage: python manage.py test_email [recipient@email.com]
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email (supports OAuth2 and traditional auth)'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            nargs='?',
            type=str,
            default=None,
            help='Email recipient (defaults to ADMIN_EMAIL)'
        )

    def handle(self, *args, **options):
        recipient = options['recipient'] or settings.ADMIN_EMAIL

        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('Testing Email Configuration'))
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write('')

        # Display configuration
        self.stdout.write('Configuration:')
        self.stdout.write(f'  Email Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  From: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'  To: {recipient}')
        self.stdout.write(f'  SMTP Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'  SMTP Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'  TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write('')

        # Check authentication method
        using_oauth2 = 'oauth2' in settings.EMAIL_BACKEND.lower()

        if using_oauth2:
            self.stdout.write(self.style.WARNING('Using OAuth2 Authentication'))
            self.stdout.write('')

            # Check OAuth2 credentials
            client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', '')
            client_secret = getattr(settings, 'MICROSOFT_CLIENT_SECRET', '')
            tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', '')

            credentials_set = {
                'MICROSOFT_CLIENT_ID': bool(client_id),
                'MICROSOFT_CLIENT_SECRET': bool(client_secret),
                'MICROSOFT_TENANT_ID': bool(tenant_id),
            }

            self.stdout.write('OAuth2 Credentials Status:')
            for cred_name, is_set in credentials_set.items():
                status = self.style.SUCCESS('✓ Set') if is_set else self.style.ERROR('✗ Not Set')
                value_preview = ''
                if is_set:
                    # Show first/last 4 chars for verification
                    if cred_name == 'MICROSOFT_CLIENT_ID':
                        value_preview = f' ({client_id[:8]}...{client_id[-4:]})' if len(client_id) > 12 else ''
                    elif cred_name == 'MICROSOFT_TENANT_ID':
                        value_preview = f' ({tenant_id[:8]}...{tenant_id[-4:]})' if len(tenant_id) > 12 else ''
                    elif cred_name == 'MICROSOFT_CLIENT_SECRET':
                        value_preview = ' (***hidden***)'
                self.stdout.write(f'  {cred_name}: {status}{value_preview}')

            if not all(credentials_set.values()):
                self.stdout.write('')
                self.stdout.write(
                    self.style.ERROR('ERROR: OAuth2 credentials not fully configured!')
                )
                self.stdout.write('Please set the following environment variables:')
                for cred_name, is_set in credentials_set.items():
                    if not is_set:
                        self.stdout.write(f'  export {cred_name}="your_value_here"')
                self.stdout.write('')
                self.stdout.write('See EMAIL_SETUP.md for detailed instructions.')
                return

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('All OAuth2 credentials are configured'))

        else:
            self.stdout.write(self.style.WARNING('Using Traditional SMTP Authentication'))
            self.stdout.write('')

            # Check for email password
            email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
            if not email_password:
                self.stdout.write(
                    self.style.ERROR('ERROR: EMAIL_HOST_PASSWORD is not set!')
                )
                self.stdout.write('Please set EMAIL_PASSWORD environment variable.')
                self.stdout.write('Example: export EMAIL_PASSWORD="your_app_password"')
                self.stdout.write('')
                self.stdout.write('Or switch to OAuth2 by updating EMAIL_BACKEND in settings.py')
                return

            self.stdout.write(self.style.SUCCESS('✓ EMAIL_HOST_PASSWORD is set'))

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('-' * 60))
        self.stdout.write('')

        try:
            if using_oauth2:
                self.stdout.write('Step 1: Acquiring OAuth2 access token...')

            # Send test email
            self.stdout.write('Step 2: Connecting to SMTP server...')
            self.stdout.write('Step 3: Sending test email...')

            send_mail(
                subject='Test Email from Diaspora Enterprise',
                message='This is a test email to verify the email configuration is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=f'''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #2BA0D8; border-bottom: 3px solid #2BA0D8; padding-bottom: 10px;">
                            Email Configuration Test
                        </h2>

                        <p>This is a test email to verify that your email configuration is working correctly.</p>

                        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p style="margin: 0;"><strong>Configuration Details:</strong></p>
                            <ul style="margin: 10px 0;">
                                <li>SMTP Host: {settings.EMAIL_HOST}</li>
                                <li>Port: {settings.EMAIL_PORT}</li>
                                <li>TLS: {'Enabled' if settings.EMAIL_USE_TLS else 'Disabled'}</li>
                                <li>Authentication: {'OAuth2' if using_oauth2 else 'Traditional SMTP'}</li>
                                <li>From: {settings.DEFAULT_FROM_EMAIL}</li>
                            </ul>
                        </div>

                        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p style="margin: 0; font-size: 18px;"><strong>✓ Email sent successfully!</strong></p>
                            <p style="margin: 10px 0 0 0;">Your email configuration is working correctly.</p>
                        </div>

                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

                        <p style="color: #757575; font-size: 12px; text-align: center;">
                            Diaspora Enterprise - Contact Form System<br>
                            Powered by {'Microsoft 365 OAuth2' if using_oauth2 else 'Microsoft 365 SMTP'}
                        </p>
                    </div>
                </body>
                </html>
                ''',
                fail_silently=False,
            )

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS('✓ SUCCESS: Test email sent successfully!'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write('')
            self.stdout.write(f'Check your inbox at {recipient}')
            self.stdout.write('')

            if using_oauth2:
                self.stdout.write(self.style.SUCCESS('OAuth2 authentication is working correctly!'))
            else:
                self.stdout.write(self.style.SUCCESS('Traditional SMTP authentication is working correctly!'))

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('=' * 60))
            self.stdout.write(self.style.ERROR('✗ FAILED: Could not send test email'))
            self.stdout.write(self.style.ERROR('=' * 60))
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            self.stdout.write('')

            # Provide troubleshooting tips
            self.stdout.write(self.style.WARNING('Troubleshooting Tips:'))
            self.stdout.write('')

            if using_oauth2:
                self.stdout.write('OAuth2 Authentication Issues:')
                self.stdout.write('  1. Verify all three OAuth2 credentials are set correctly')
                self.stdout.write('  2. Check your Azure App Registration:')
                self.stdout.write('     - Go to Azure Portal > App Registrations')
                self.stdout.write('     - Verify API Permissions: Mail.Send is granted')
                self.stdout.write('     - Confirm Admin Consent has been granted')
                self.stdout.write('  3. Ensure Client Secret is not expired')
                self.stdout.write('  4. Verify Tenant ID matches your organization')
                self.stdout.write('  5. Check that the app has Application permission (not Delegated)')
            else:
                self.stdout.write('Traditional SMTP Issues:')
                self.stdout.write('  1. Verify EMAIL_HOST_PASSWORD is set correctly')
                self.stdout.write('  2. Ensure you\'re using a Microsoft 365 App Password')
                self.stdout.write('  3. Check that 2FA is enabled on your Microsoft account')
                self.stdout.write('  4. Verify the email address is valid')

            self.stdout.write('')
            self.stdout.write('For detailed instructions, see EMAIL_SETUP.md')
            self.stdout.write('')
