"""
Admin configuration for the Services app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview', 'title', 'short_description_truncated',
        'is_featured', 'is_active', 'display_order',
    ]
    list_display_links = ['title']
    list_filter = ['is_active', 'is_featured']
    list_editable = ['is_featured', 'is_active', 'display_order']
    search_fields = ['title', 'short_description', 'full_description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    ordering = ['display_order', 'title']

    fieldsets = (
        ('Core Info', {
            'fields': ('title', 'slug', 'icon'),
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
        }),
        ('Content', {
            'fields': ('short_description', 'full_description', 'features'),
        }),
        ('Call To Action', {
            'fields': ('cta_text', 'cta_link'),
        }),
        ('Display Settings', {
            'fields': ('is_active', 'is_featured', 'display_order'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:100px;'
                'object-fit:cover;border-radius:4px;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Image'

    def short_description_truncated(self, obj):
        text = obj.short_description
        return text[:80] + '…' if len(text) > 80 else text
    short_description_truncated.short_description = 'Description'
