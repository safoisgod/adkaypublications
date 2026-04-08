"""
Admin configuration for the Contact app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'subject_badge',
        'read_badge', 'replied_badge', 'created_at',
    ]
    list_filter = ['subject', 'is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at', 'replied_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Sender Info', {
            'fields': ('name', 'email', 'phone'),
        }),
        ('Message', {
            'fields': ('subject', 'message', 'created_at'),
        }),
        ('Status', {
            'fields': ('is_read', 'is_replied', 'replied_at'),
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',),
        }),
    )

    def subject_badge(self, obj):
        colors = {
            'general': '#6c757d',
            'submission': '#0d6efd',
            'rights': '#198754',
            'press': '#fd7e14',
            'partnership': '#6f42c1',
            'other': '#adb5bd',
        }
        color = colors.get(obj.subject, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_subject_display()
        )
    subject_badge.short_description = 'Subject'

    def read_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="color:#198754;font-weight:bold;">✓ Read</span>'
            )
        return format_html(
            '<span style="color:#dc3545;font-weight:bold;">● New</span>'
        )
    read_badge.short_description = 'Read'

    def replied_badge(self, obj):
        if obj.is_replied:
            return format_html(
                '<span style="color:#198754;">✓ Replied</span>'
            )
        return format_html('<span style="color:#adb5bd;">Pending</span>')
    replied_badge.short_description = 'Reply'

    def get_queryset(self, request):
        return super().get_queryset(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Auto-mark as read when admin opens the message."""
        try:
            obj = ContactMessage.objects.get(pk=object_id)
            obj.mark_read()
        except ContactMessage.DoesNotExist:
            pass
        return super().change_view(request, object_id, form_url, extra_context)

    actions = ['mark_as_read', 'mark_as_replied']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_replied(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(is_replied=True, replied_at=now)
        self.message_user(request, f'{updated} message(s) marked as replied.')
    mark_as_replied.short_description = 'Mark selected as replied'
