"""
Custom admin for user management.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'email', 'full_name', 'avatar_preview',
        'is_author', 'is_verified', 'is_staff', 'created_at',
    ]
    list_filter = ['is_author', 'is_verified', 'is_staff', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['avatar_preview', 'created_at', 'updated_at']

    fieldsets = (
        ('Credentials', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': (
            'username', 'first_name', 'last_name', 'bio',
            'avatar', 'avatar_preview',
        )}),
        ('Roles & Status', {'fields': (
            'is_author', 'is_verified', 'is_active', 'is_staff', 'is_superuser',
        )}),
        ('Permissions', {'fields': ('groups', 'user_permissions'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'last_login'), 'classes': ('collapse',)}),
    )

    add_fieldsets = (
        ('Create User', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;border-radius:50%;object-fit:cover;" />',
                obj.avatar.url
            )
        return '—'
    avatar_preview.short_description = 'Avatar'

    actions = ['verify_users', 'revoke_verification']

    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} user(s) verified.')
    verify_users.short_description = 'Verify selected users'

    def revoke_verification(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} user(s) unverified.')
    revoke_verification.short_description = 'Revoke verification'
