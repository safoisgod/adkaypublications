"""
Core admin customizations applied globally.
"""
from django.contrib import admin
from django.utils.html import format_html


class PublishableAdmin(admin.ModelAdmin):
    """
    Base admin class for publishable content.
    Provides publish/unpublish actions.
    """
    actions = ['publish_selected', 'unpublish_selected']

    def publish_selected(self, request, queryset):
        updated = 0
        for obj in queryset:
            obj.publish()
            updated += 1
        self.message_user(request, f'{updated} item(s) published.')
    publish_selected.short_description = 'Publish selected items'

    def unpublish_selected(self, request, queryset):
        updated = 0
        for obj in queryset:
            obj.unpublish()
            updated += 1
        self.message_user(request, f'{updated} item(s) unpublished.')
    unpublish_selected.short_description = 'Unpublish selected items'

    def published_badge(self, obj):
        if obj.is_published:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:2px 8px;'
                'border-radius:12px;font-size:11px;">Published</span>'
            )
        return format_html(
            '<span style="background:#dc3545;color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px;">Draft</span>'
        )
    published_badge.short_description = 'Status'

    def image_preview(self, obj, field_name='cover_image'):
        image = getattr(obj, field_name, None)
        if image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;'
                'object-fit:cover;" />',
                image.url
            )
        return '—'
    image_preview.short_description = 'Preview'
