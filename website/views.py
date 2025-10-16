from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

from .forms import ContactForm

# Configure logger
logger = logging.getLogger(__name__)


def home(request):
    """Homepage view"""
    context = {
        'company_name': 'Diaspora Enterprise',
        'tagline': 'Your partner in real estate investments and short-term rentals',
    }
    return render(request, 'website/home.html', context)


def team(request):
    """Team page view"""
    team_members = [
        {
            'name': 'Marvens King',
            'title': 'CEO',
            'initials': 'MK'
        },
        {
            'name': 'Carlos Rado',
            'title': 'President',
            'initials': 'CR'
        },
        {
            'name': 'Sherifa Siddeeq',
            'title': 'COO',
            'initials': 'SS'
        },
        {
            'name': 'Alicia Ramdhan',
            'title': 'CFO',
            'initials': 'AR'
        },
    ]
    context = {
        'team_members': team_members,
    }
    return render(request, 'website/team.html', context)


def story(request):
    """Our Story page view"""
    context = {}
    return render(request, 'website/story.html', context)


def contact(request):
    """
    Contact form view.
    Handles form submission, saves to database, and sends email notification.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact message to database
            contact_message = form.save()

            # Prepare email notification
            try:
                # Email subject
                email_subject = f"New Contact Form Submission: {contact_message.subject}"

                # Email body (HTML version)
                email_body_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #2BA0D8; border-bottom: 3px solid #2BA0D8; padding-bottom: 10px;">
                            New Contact Form Submission
                        </h2>

                        <div style="margin: 20px 0;">
                            <p><strong style="color: #1E5A8E;">From:</strong> {contact_message.name}</p>
                            <p><strong style="color: #1E5A8E;">Email:</strong>
                                <a href="mailto:{contact_message.email}">{contact_message.email}</a>
                            </p>
                            <p><strong style="color: #1E5A8E;">Phone:</strong> {contact_message.phone or 'Not provided'}</p>
                            <p><strong style="color: #1E5A8E;">Subject:</strong> {contact_message.subject}</p>
                            <p><strong style="color: #1E5A8E;">Received:</strong> {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                        </div>

                        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p style="margin: 0;"><strong style="color: #1E5A8E;">Message:</strong></p>
                            <p style="margin: 10px 0 0 0; white-space: pre-wrap;">{contact_message.message}</p>
                        </div>

                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #757575; font-size: 12px;">
                            <p>This message was sent via the Diaspora Enterprise contact form.</p>
                            <p>You can view and manage all contact messages in the
                                <a href="{request.scheme}://{request.get_host()}/admin/website/contact/" style="color: #2BA0D8;">Django Admin</a>.
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """

                # Email body (plain text version)
                email_body_text = f"""
New Contact Form Submission

From: {contact_message.name}
Email: {contact_message.email}
Phone: {contact_message.phone or 'Not provided'}
Subject: {contact_message.subject}
Received: {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}

Message:
{contact_message.message}

---
This message was sent via the Diaspora Enterprise contact form.
You can view all messages in the Django Admin panel.
                """

                # Send email notification
                send_mail(
                    subject=email_subject,
                    message=email_body_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    html_message=email_body_html,
                    fail_silently=False,
                )

                logger.info(f"Contact form submitted by {contact_message.email} - Email sent successfully")

            except Exception as e:
                # Log the error but don't fail the form submission
                logger.error(f"Failed to send email notification: {str(e)}")
                # Still show success to user since the message was saved

            # Show success message
            messages.success(
                request,
                'Thank you for contacting us! We have received your message and will get back to you shortly.'
            )

            # Redirect to contact page to prevent form resubmission
            return redirect('website:contact')
        else:
            # Form is invalid
            messages.error(
                request,
                'There was an error with your submission. Please check the form and try again.'
            )
    else:
        form = ContactForm()

    context = {
        'form': form,
    }
    return render(request, 'website/contact.html', context)
