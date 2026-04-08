"""
Admin configuration for the Newsletter app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'status_badge',
        'source', 'confirmed_at', 'created_at',
    ]
    list_filter = ['is_active', 'source', 'created_at']
    search_fields = ['email', 'first_name']
    readonly_fields = ['unsubscribe_token', 'confirmed_at', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Subscriber Info', {
            'fields': ('email', 'first_name', 'source'),
        }),
        ('Status', {
            'fields': ('is_active', 'confirmed_at'),
        }),
        ('System', {
            'fields': ('unsubscribe_token', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#198754;color:#fff;padding:2px 8px;'
                'border-radius:12px;font-size:11px;">Active</span>'
            )
        return format_html(
            '<span style="background:#dc3545;color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px;">Unsubscribed</span>'
        )
    status_badge.short_description = 'Status'

    actions = ['activate_subscribers', 'deactivate_subscribers', 'export_active_csv']

    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriber(s) activated.')
    activate_subscribers.short_description = 'Activate selected subscribers'

    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriber(s) deactivated.')
    deactivate_subscribers.short_description = 'Deactivate selected subscribers'

    def export_active_csv(self, request, queryset):
        """Export active subscribers to CSV for email tools."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'First Name', 'Source', 'Subscribed At'])
        for sub in queryset.filter(is_active=True):
            writer.writerow([
                sub.email,
                sub.first_name,
                sub.source,
                sub.created_at.strftime('%Y-%m-%d'),
            ])
        return response
    export_active_csv.short_description = 'Export active subscribers (CSV)'
