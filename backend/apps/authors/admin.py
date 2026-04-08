"""
Admin configuration for the Authors app.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin import PublishableAdmin
from .models import Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        'photo_preview', 'full_name', 'role',
        'is_featured', 'is_active', 'display_order', 'book_count',
    ]
    list_display_links = ['full_name']
    list_filter = ['is_featured', 'is_active', 'created_at']
    list_editable = ['is_featured', 'is_active', 'display_order']
    search_fields = ['full_name', 'role', 'bio']
    prepopulated_fields = {'slug': ('full_name',)}
    readonly_fields = ['photo_preview', 'book_count', 'created_at', 'updated_at']
    ordering = ['display_order', 'full_name']

    fieldsets = (
        ('Identity', {
            'fields': ('full_name', 'slug', 'role', 'user'),
        }),
        ('Photo', {
            'fields': ('photo', 'photo_preview'),
        }),
        ('Biography', {
            'fields': ('short_bio', 'bio'),
        }),
        ('Social Links', {
            'fields': ('twitter', 'linkedin', 'instagram', 'website'),
            'classes': ('collapse',),
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_active', 'display_order'),
        }),
        ('Stats & Timestamps', {
            'fields': ('book_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;'
                'border-radius:50%;object-fit:cover;" />',
                obj.photo.url
            )
        return '—'
    photo_preview.short_description = 'Photo'

    def book_count(self, obj):
        count = obj.books.filter(is_published=True).count()
        return count
    book_count.short_description = 'Published Books'

    actions = ['feature_authors', 'unfeature_authors']

    def feature_authors(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} author(s) marked as featured.')
    feature_authors.short_description = 'Mark as featured'

    def unfeature_authors(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} author(s) removed from featured.')
    unfeature_authors.short_description = 'Remove from featured'
