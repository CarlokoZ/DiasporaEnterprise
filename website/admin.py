from django.contrib import admin
from django.utils.html import format_html
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Contact messages.
    Provides filtering, searching, and bulk actions for managing contact submissions.
    """

    # List display configuration
    list_display = ['name', 'email', 'subject', 'created_at_formatted', 'read_status']
    list_filter = ['read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'name', 'email', 'phone', 'subject', 'message']

    # Fields to display in the detail view
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'phone', 'subject', 'message', 'created_at')
        }),
        ('Status', {
            'fields': ('read',)
        }),
        ('Internal Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
            'description': 'Add internal notes about this message (not visible to the sender)'
        }),
    )

    # Ordering
    ordering = ['-created_at']

    # Actions
    actions = ['mark_as_read', 'mark_as_unread']

    def created_at_formatted(self, obj):
        """Format the created_at timestamp for display"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = 'Received At'
    created_at_formatted.admin_order_field = 'created_at'

    def read_status(self, obj):
        """Display read status with color coding"""
        if obj.read:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Read</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Unread</span>'
            )
    read_status.short_description = 'Status'
    read_status.admin_order_field = 'read'

    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        """Bulk action to mark messages as read"""
        updated = queryset.update(read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')

    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        """Bulk action to mark messages as unread"""
        updated = queryset.update(read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')

    def has_add_permission(self, request):
        """Disable manual addition of contact messages through admin"""
        return False
