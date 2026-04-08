"""
Admin configuration for the Books app.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin import PublishableAdmin
from .models import Book, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'book_count', 'display_order']
    list_editable = ['display_order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['display_order', 'name']

    def book_count(self, obj):
        return obj.books.filter(is_published=True).count()
    book_count.short_description = 'Published Books'


class AuthorInline(admin.TabularInline):
    from apps.authors.models import Author
    model = Book.authors.through
    extra = 1
    verbose_name = 'Author'
    verbose_name_plural = 'Authors'


@admin.register(Book)
class BookAdmin(PublishableAdmin):
    list_display = [
        'cover_preview', 'title', 'author_names_display',
        'genre', 'published_date', 'price',
        'published_badge', 'is_featured', 'is_bestseller',
    ]
    list_display_links = ['title']
    list_filter = [
        'is_published', 'is_featured', 'is_bestseller',
        'is_new_release', 'genre', 'language', 'published_date',
    ]
    list_editable = ['is_featured', 'is_bestseller']
    search_fields = ['title', 'subtitle', 'isbn', 'authors__full_name', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['cover_preview', 'author_names', 'created_at', 'updated_at']
    filter_horizontal = ['authors']
    date_hierarchy = 'published_date'

    fieldsets = (
        ('Core Info', {
            'fields': (
                'title', 'slug', 'subtitle',
                'authors', 'genre',
            ),
        }),
        ('Cover Image', {
            'fields': ('cover_image', 'cover_preview'),
        }),
        ('Content', {
            'fields': ('description', 'excerpt'),
        }),
        ('Publication Details', {
            'fields': (
                'isbn', 'publisher', 'published_date',
                'pages', 'language', 'edition',
            ),
            'classes': ('collapse',),
        }),
        ('Commerce', {
            'fields': ('price', 'buy_link'),
        }),
        ('Flags & Visibility', {
            'fields': (
                'is_published', 'is_featured',
                'is_bestseller', 'is_new_release',
            ),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:70px;width:50px;'
                'object-fit:cover;border-radius:4px;" />',
                obj.cover_image.url
            )
        return '—'
    cover_preview.short_description = 'Cover'

    def author_names_display(self, obj):
        names = obj.author_names
        return names if names else '—'
    author_names_display.short_description = 'Authors'
