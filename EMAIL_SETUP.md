# Email Setup Guide - Microsoft 365 OAuth2

This document provides comprehensive instructions for setting up email notifications for the Diaspora Enterprise contact form using **Microsoft 365 with OAuth2 authentication** (recommended) or traditional SMTP authentication (legacy).

## Table of Contents

1. [Overview](#overview)
2. [OAuth2 Setup (Recommended)](#oauth2-setup-recommended)
3. [Traditional SMTP Setup (Legacy)](#traditional-smtp-setup-legacy)
4. [Testing Email Configuration](#testing-email-configuration)
5. [Troubleshooting](#troubleshooting)
6. [Security Best Practices](#security-best-practices)

---

## Overview

The contact form system includes:
- ✅ Contact form submissions saved to database
- ✅ Django admin interface for viewing and managing messages
- ✅ Email notifications sent to admin@diasporaenterprise.com
- ✅ Professional HTML email templates
- ✅ OAuth2 or traditional SMTP authentication
- ✅ Graceful error handling (form still saves if email fails)

### Authentication Methods

| Method | Security | Setup Complexity | Recommended |
|--------|----------|------------------|-------------|
| **OAuth2** | ⭐⭐⭐⭐⭐ Modern, no password exposure | ⭐⭐⭐ Moderate (Azure setup) | ✅ **Yes** |
| **Traditional SMTP** | ⭐⭐⭐ Requires app password | ⭐⭐ Simple (2FA + app password) | ❌ Legacy |

---

## OAuth2 Setup (Recommended)

OAuth2 is the modern, secure way to authenticate with Microsoft 365. No passwords are stored or transmitted.

### Prerequisites

- Azure subscription (free tier works)
- Access to Azure Portal
- Microsoft 365 account (admin@diasporaenterprise.com)

### Step 1: Register Application in Azure

1. **Go to Azure Portal**
   - Navigate to https://portal.azure.com
   - Sign in with your Microsoft 365 account

2. **Navigate to App Registrations**
   - Search for "App registrations" in the top search bar
   - Click on "App registrations"
   - Click "New registration"

3. **Register the Application**
   - **Name**: `Diaspora Enterprise - Email Service`
   - **Supported account types**: "Accounts in this organizational directory only (Single tenant)"
   - **Redirect URI**: Leave empty (not needed for app-only flow)
   - Click **Register**

4. **Note Your Application Details**
   After registration, you'll see the Overview page. **Copy these values:**
   - **Application (client) ID**: e.g., `12345678-1234-1234-1234-123456789abc`
   - **Directory (tenant) ID**: e.g., `87654321-4321-4321-4321-987654321def`

   ```bash
   # Save these for later
   MICROSOFT_CLIENT_ID=your_application_client_id
   MICROSOFT_TENANT_ID=your_directory_tenant_id
   ```

### Step 2: Create Client Secret

1. **Navigate to Certificates & secrets**
   - In your app registration, click "Certificates & secrets" in the left menu

2. **Create New Client Secret**
   - Click "New client secret"
   - **Description**: `Django Email Backend Secret`
   - **Expires**: Choose expiration (6 months, 1 year, or 2 years recommended)
   - Click **Add**

3. **Copy the Secret Value**
   - **IMPORTANT**: Copy the **Value** (not the Secret ID!) immediately
   - You'll only see this once!
   - If you miss it, you'll need to create a new secret

   ```bash
   # Save this immediately - you won't see it again!
   MICROSOFT_CLIENT_SECRET=your_secret_value_here
   ```

   ⚠️ **Warning**: Set a calendar reminder before the secret expires to renew it!

### Step 3: Configure API Permissions

1. **Navigate to API permissions**
   - Click "API permissions" in the left menu

2. **Add Permission**
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Choose **"Application permissions"** (NOT Delegated)
   - Search for and select: `Mail.Send`
   - Click "Add permissions"

3. **Grant Admin Consent** ⚠️ **CRITICAL STEP**
   - Click "Grant admin consent for [Your Organization]"
   - Confirm by clicking "Yes"
   - You should see a green checkmark next to Mail.Send

   **Verification**: The status column should show:
   ```
   Mail.Send | Granted for [Your Organization]
   ```

### Step 4: Configure Environment Variables

#### Option A: Using .env File (Recommended for Development)

1. **Install python-decouple** (if not already installed):
   ```bash
   pip install python-decouple
   ```

2. **Create .env file** in your project root:
   ```bash
   cp .env.example .env
   ```

3. **Edit .env file** with your values:
   ```env
   # Microsoft 365 OAuth2 Configuration
   MICROSOFT_CLIENT_ID=12345678-1234-1234-1234-123456789abc
   MICROSOFT_CLIENT_SECRET=your_secret_value_here
   MICROSOFT_TENANT_ID=87654321-4321-4321-4321-987654321def
   ```

4. **Verify .env is in .gitignore**:
   ```bash
   # Check that .env is listed in .gitignore
   grep "\.env" .gitignore
   ```

#### Option B: Using Environment Variables (Production)

**macOS/Linux:**
```bash
# Add to ~/.zshrc or ~/.bashrc
export MICROSOFT_CLIENT_ID="12345678-1234-1234-1234-123456789abc"
export MICROSOFT_CLIENT_SECRET="your_secret_value_here"
export MICROSOFT_TENANT_ID="87654321-4321-4321-4321-987654321def"

# Reload shell
source ~/.zshrc  # or ~/.bashrc
```

**Windows PowerShell:**
```powershell
$env:MICROSOFT_CLIENT_ID = "12345678-1234-1234-1234-123456789abc"
$env:MICROSOFT_CLIENT_SECRET = "your_secret_value_here"
$env:MICROSOFT_TENANT_ID = "87654321-4321-4321-4321-987654321def"
```

**Production Servers:**
- **Heroku**: `heroku config:set MICROSOFT_CLIENT_ID=xxx ...`
- **AWS EB**: Add to environment configuration
- **Docker**: Add to docker-compose.yml environment section
- **Systemd**: Add to service file

### Step 5: Verify Configuration

Check that your settings.py is using the OAuth2 backend:

```python
# In diaspora_enterprise/settings.py
EMAIL_BACKEND = 'website.email_backend.OAuth2EmailBackend'
```

If you see `django.core.mail.backends.smtp.EmailBackend`, change it to the line above.

### Step 6: Test OAuth2 Email

```bash
# Test email sending
python manage.py test_email

# Or send to a specific email
python manage.py test_email your@email.com
```

**Expected Output:**
```
============================================================
Testing Email Configuration
============================================================

Configuration:
  Email Backend: website.email_backend.OAuth2EmailBackend
  From: admin@diasporaenterprise.com
  To: admin@diasporaenterprise.com
  SMTP Host: smtp.office365.com
  SMTP Port: 587
  TLS: True

Using OAuth2 Authentication

OAuth2 Credentials Status:
  MICROSOFT_CLIENT_ID: ✓ Set (12345678...9abc)
  MICROSOFT_CLIENT_SECRET: ✓ Set (***hidden***)
  MICROSOFT_TENANT_ID: ✓ Set (87654321...1def)

All OAuth2 credentials are configured

------------------------------------------------------------

Step 1: Acquiring OAuth2 access token...
Step 2: Connecting to SMTP server...
Step 3: Sending test email...

============================================================
✓ SUCCESS: Test email sent successfully!
============================================================

Check your inbox at admin@diasporaenterprise.com

OAuth2 authentication is working correctly!
```

---

## Traditional SMTP Setup (Legacy)

If you prefer traditional SMTP with app passwords instead of OAuth2.

### Step 1: Enable Two-Factor Authentication (2FA)

1. Go to https://account.microsoft.com/security
2. Sign in with admin@diasporaenterprise.com
3. Enable Two-Step Verification
4. Complete the 2FA setup process

### Step 2: Create App Password

1. Go back to https://account.microsoft.com/security
2. Click "Advanced security options"
3. Scroll to "App passwords"
4. Click "Create a new app password"
5. Name it "Django Contact Form"
6. Copy the generated password (16 characters, no spaces)

### Step 3: Configure Environment Variable

```bash
# Set EMAIL_PASSWORD environment variable
export EMAIL_PASSWORD='your-16-char-app-password'
```

### Step 4: Update settings.py

```python
# In diaspora_enterprise/settings.py

# Comment out OAuth2 backend
# EMAIL_BACKEND = 'website.email_backend.OAuth2EmailBackend'

# Use traditional SMTP backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'admin@diasporaenterprise.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
```

### Step 5: Test Traditional SMTP

```bash
python manage.py test_email
```

---

## Testing Email Configuration

### Test Command

```bash
# Test with default recipient (ADMIN_EMAIL)
python manage.py test_email

# Test with specific recipient
python manage.py test_email recipient@example.com
```

### Test from Contact Form

1. Start development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to contact form:
   ```
   http://localhost:8000/contact/
   ```

3. Fill out and submit the form

4. Check admin@diasporaenterprise.com inbox

### Test from Django Shell

```python
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Test Email',
    message='This is a test.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[settings.ADMIN_EMAIL],
    fail_silently=False,
)
```

### Development Testing (Console Backend)

For testing without sending real emails:

1. **Temporarily use console backend**:
   ```python
   # In settings.py, comment out current backend and use:
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```

2. **Emails will print to console** instead of sending

3. **Don't forget to switch back** to OAuth2 backend for production!

---

## Troubleshooting

### OAuth2 Issues

#### Error: "OAuth2 credentials not fully configured"

**Solution:**
```bash
# Check if environment variables are set
echo $MICROSOFT_CLIENT_ID
echo $MICROSOFT_CLIENT_SECRET
echo $MICROSOFT_TENANT_ID

# If empty, set them:
export MICROSOFT_CLIENT_ID="your_value"
export MICROSOFT_CLIENT_SECRET="your_value"
export MICROSOFT_TENANT_ID="your_value"
```

#### Error: "invalid_client" or "unauthorized_client"

**Possible causes:**
1. Client secret is incorrect or expired
2. Client ID is incorrect
3. Tenant ID is incorrect

**Solution:**
- Verify all three values from Azure Portal
- Check for extra spaces or quotes
- Create a new client secret if expired

#### Error: "insufficient_permissions" or "Mail.Send not granted"

**Solution:**
1. Go to Azure Portal > App Registrations > Your App
2. Click "API permissions"
3. Verify Mail.Send permission is listed
4. **Click "Grant admin consent"** (this is often missed!)
5. Confirm you see green checkmark

#### Error: "AADSTS700016: Application not found in directory"

**Cause**: Wrong tenant ID

**Solution:**
- Verify MICROSOFT_TENANT_ID matches your organization's tenant
- Get correct tenant ID from Azure Portal > App Registration > Overview

#### Error: "AADSTS7000215: Invalid client secret"

**Cause**: Client secret is wrong or expired

**Solution:**
- Go to Azure Portal > Certificates & secrets
- Check if secret is expired
- Create new secret and update MICROSOFT_CLIENT_SECRET

### Traditional SMTP Issues

#### Error: "SMTPAuthenticationError"

**Solutions:**
1. Verify EMAIL_PASSWORD is set correctly
2. Ensure using app password (not regular password)
3. Confirm 2FA is enabled on Microsoft account
4. Check that app password hasn't been revoked

#### Error: "Connection refused" or "Connection timed out"

**Solutions:**
1. Check firewall settings
2. Verify SMTP port 587 is not blocked
3. Confirm TLS is enabled
4. Try from different network

### General Issues

#### Emails not received

**Check:**
1. Spam/junk folder
2. Email quotas not exceeded
3. Recipient email is valid
4. Check Django logs for errors

#### Form saves but email doesn't send

This is **expected behavior**! The form is designed to save messages even if email fails.

**Check:**
- Django console/logs for error messages
- Run `python manage.py test_email` to diagnose
- Verify credentials are set correctly

---

## Security Best Practices

### ✅ DO

1. **Use OAuth2** instead of passwords when possible
2. **Use environment variables** for all credentials
3. **Never commit** secrets to Git
4. **Use .env file** for development
5. **Set secret expiration reminders** (for client secrets)
6. **Rotate secrets** regularly (every 6-12 months)
7. **Use least privilege** (only Mail.Send permission)
8. **Monitor usage** in Azure Portal
9. **Keep dependencies updated**:
   ```bash
   pip install --upgrade msal requests django
   ```

### ❌ DON'T

1. **Don't hardcode** credentials in code
2. **Don't commit** .env files to Git
3. **Don't share** client secrets
4. **Don't use** personal accounts in production
5. **Don't ignore** expiration warnings
6. **Don't use** the same secret across environments

### Security Checklist

- [ ] .env file is in .gitignore
- [ ] No secrets hardcoded in settings.py
- [ ] OAuth2 credentials are environment variables
- [ ] Client secret expiration is tracked
- [ ] Admin consent granted for Mail.Send
- [ ] Application permission (not delegated) used
- [ ] Regular security audits scheduled
- [ ] Logs monitored for unauthorized access

---

## Production Deployment Checklist

Before deploying to production:

- [ ] OAuth2 credentials set on production server
- [ ] Test email sending from production environment
- [ ] Verify Django admin is accessible and secure
- [ ] Check contact form at /contact/
- [ ] Test form submission and email notification
- [ ] Review email content and formatting
- [ ] Set up monitoring for failed emails
- [ ] Configure proper logging for production
- [ ] Review Microsoft 365 sending limits
- [ ] Document who has access to Azure app registration
- [ ] Set up alerts for client secret expiration
- [ ] Backup OAuth2 credentials securely
- [ ] Test failover if email service is down

---

## Microsoft 365 Email Limits

Be aware of sending limits:

- **Office 365**: 10,000 recipients per day
- **Rate limiting**: 30 messages per minute
- **Attachment size**: 150 MB total per message

For high-volume sending, consider:
- Using a transactional email service (SendGrid, Mailgun)
- Implementing queuing and throttling
- Monitoring quota usage

---

## Support and Resources

### Documentation
- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- [Microsoft Graph Mail API](https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [Azure App Registrations Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

### Getting Help
- Check Django logs: `python manage.py runserver` output
- Run diagnostic: `python manage.py test_email`
- Review this documentation
- Check Azure Portal for app status
- Contact your system administrator

### Useful Commands

```bash
# Test email
python manage.py test_email

# Check environment variables
env | grep MICROSOFT

# Clear OAuth2 token cache (if needed)
python manage.py shell
>>> from website.email_backend import OAuth2EmailBackend
>>> OAuth2EmailBackend.clear_token_cache()

# View Django logs
python manage.py runserver  # watch console output

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip install --upgrade msal requests
```

---

## Appendix: Switching Between Methods

### From Traditional SMTP to OAuth2

1. Complete OAuth2 setup (Steps 1-4 above)
2. In settings.py:
   ```python
   # Comment out:
   # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   # EMAIL_HOST_USER = '...'
   # EMAIL_HOST_PASSWORD = '...'

   # Use:
   EMAIL_BACKEND = 'website.email_backend.OAuth2EmailBackend'
   ```
3. Test: `python manage.py test_email`

### From OAuth2 to Traditional SMTP

1. Complete traditional SMTP setup
2. In settings.py:
   ```python
   # Comment out:
   # EMAIL_BACKEND = 'website.email_backend.OAuth2EmailBackend'

   # Use:
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST_USER = 'admin@diasporaenterprise.com'
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
   ```
3. Test: `python manage.py test_email`

---

**Last Updated**: October 2025
**Django Version**: 5.1+
**Python Version**: 3.9+
