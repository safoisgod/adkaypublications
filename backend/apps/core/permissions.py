"""
Custom permission classes.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Allow safe methods (GET, HEAD, OPTIONS) for everyone.
    Restrict write methods to admin users only.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Allow full access to the object owner or admin users.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        # Check if object has 'user' or 'author' attribute
        owner = getattr(obj, 'user', None) or getattr(obj, 'author', None)
        return owner == request.user


class IsVerifiedUser(BasePermission):
    """
    Only verified (email-confirmed) users can access.
    """
    message = 'Your account must be verified to perform this action.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_verified', False)
        )


class IsPublicReadOnly(BasePermission):
    """
    Completely public read-only access (no auth required).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
