from django.db import models
from django.utils import timezone


class Contact(models.Model):
    """
    Model to store contact form submissions.
    All messages are stored in the database and can be viewed in Django admin.
    """
    name = models.CharField(max_length=200, help_text="Full name of the person contacting us")
    email = models.EmailField(help_text="Email address for response")
    phone = models.CharField(max_length=20, blank=True, help_text="Optional phone number")
    subject = models.CharField(max_length=300, help_text="Subject of the inquiry")
    message = models.TextField(help_text="Detailed message")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when message was received")
    read = models.BooleanField(default=False, help_text="Mark as read/unread")
    notes = models.TextField(blank=True, help_text="Internal notes (visible only to admin)")

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']  # Newest first

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def mark_as_read(self):
        """Mark this message as read"""
        self.read = True
        self.save()

    def mark_as_unread(self):
        """Mark this message as unread"""
        self.read = False
        self.save()
