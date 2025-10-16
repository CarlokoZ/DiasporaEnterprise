from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    """
    Contact form for clients to reach out to Diaspora Enterprise.
    Includes validation and custom error messages.
    """

    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your Full Name *',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your Email Address *',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your Phone Number (Optional)',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Subject *',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Your Message *',
                'rows': 6,
                'required': True,
            }),
        }
        error_messages = {
            'name': {
                'required': 'Please enter your name.',
                'max_length': 'Name is too long. Maximum 200 characters.',
            },
            'email': {
                'required': 'Please enter your email address.',
                'invalid': 'Please enter a valid email address.',
            },
            'subject': {
                'required': 'Please enter a subject.',
                'max_length': 'Subject is too long. Maximum 300 characters.',
            },
            'message': {
                'required': 'Please enter your message.',
            },
        }

    def clean_name(self):
        """Validate and clean the name field"""
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Name cannot be empty.')
        if len(name) < 2:
            raise forms.ValidationError('Name must be at least 2 characters long.')
        return name

    def clean_email(self):
        """Validate and clean the email field"""
        email = self.cleaned_data.get('email', '').strip().lower()
        return email

    def clean_subject(self):
        """Validate and clean the subject field"""
        subject = self.cleaned_data.get('subject', '').strip()
        if not subject:
            raise forms.ValidationError('Subject cannot be empty.')
        if len(subject) < 5:
            raise forms.ValidationError('Subject must be at least 5 characters long.')
        return subject

    def clean_message(self):
        """Validate and clean the message field"""
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise forms.ValidationError('Message cannot be empty.')
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message

    def clean_phone(self):
        """Validate and clean the phone field (optional)"""
        phone = self.cleaned_data.get('phone', '').strip()
        return phone
