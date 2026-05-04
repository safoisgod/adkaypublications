"""
Admin configuration for the Blog app.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin import PublishableAdmin
from .models import Post, Category, Tag, PostContent


# ✅ NEW: Inline for PostContent
class PostContentInline(admin.StackedInline):  # can switch to TabularInline later
    model = PostContent
    extra = 1
    ordering = ['order']
    fields = ('content_type', 'text', 'image', 'video_url', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_badge', 'slug', 'post_count', 'display_order']
    list_editable = ['display_order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['display_order', 'name']

    def color_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;">{}</span>',
            obj.color, obj.color
        )
    color_badge.short_description = 'Color'

    def post_count(self, obj):
        return obj.posts.filter(is_published=True).count()
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def post_count(self, obj):
        return obj.posts.filter(is_published=True).count()
    post_count.short_description = 'Posts'


@admin.register(Post)
class PostAdmin(PublishableAdmin):
    inlines = [PostContentInline]  # ✅ ADD THIS

    list_display = [
        'cover_preview', 'title', 'author',
        'category', 'reading_time', 'views',
        'published_badge', 'is_featured', 'published_at',
    ]
    list_display_links = ['title']
    list_filter = [
        'is_published', 'is_featured', 'category',
        'tags', 'published_at',
    ]
    list_editable = ['is_featured']
    search_fields = ['title', 'subtitle', 'excerpt', 'body', 'author__email']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'cover_preview', 'reading_time', 'views',
        'created_at', 'updated_at',
    ]
    filter_horizontal = ['tags']
    date_hierarchy = 'published_at'
    raw_id_fields = ['author']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'subtitle', 'author', 'category', 'tags'),
        }),
        ('Cover Image', {
            'fields': ('cover_image', 'cover_preview'),
        }),
        ('Post Body (Legacy)', {  # ✅ renamed for clarity
            'fields': ('excerpt', 'body'),
            'classes': ('collapse',),  # optional: hide it
        }),
        ('Visibility & Flags', {
            'fields': ('is_published', 'is_featured', 'allow_comments'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Stats & Timestamps', {
            'fields': ('reading_time', 'views', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:50px;width:80px;'
                'object-fit:cover;border-radius:4px;" />',
                obj.cover_image.url
            )
        return '—'
    cover_preview.short_description = 'Cover'