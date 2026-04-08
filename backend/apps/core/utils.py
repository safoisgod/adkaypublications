"""
Shared utility functions and helpers.
"""
import os
import uuid
import bleach
import logging
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('apps.core')


# ─────────────────────────────────────────
# FILE UPLOAD HELPERS
# ─────────────────────────────────────────

def generate_upload_path(instance, filename, subfolder='misc'):
    """
    Generate a unique, organised upload path.
    Pattern: media/<subfolder>/<uuid>.<ext>
    """
    ext = filename.rsplit('.', 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join(subfolder, unique_name)


def book_cover_path(instance, filename):
    return generate_upload_path(instance, filename, 'books/covers')


def author_photo_path(instance, filename):
    return generate_upload_path(instance, filename, 'authors/photos')


def blog_cover_path(instance, filename):
    return generate_upload_path(instance, filename, 'blog/covers')


def service_image_path(instance, filename):
    return generate_upload_path(instance, filename, 'services/images')


def user_avatar_path(instance, filename):
    return generate_upload_path(instance, filename, 'users/avatars')


def validate_image(image):
    """Validate image size and type."""
    if image.size > settings.MAX_UPLOAD_SIZE:
        from rest_framework.exceptions import ValidationError
        raise ValidationError(
            f"Image size must be under {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB."
        )
    content_type = getattr(image, 'content_type', '')
    if content_type and content_type not in settings.ALLOWED_IMAGE_TYPES:
        from rest_framework.exceptions import ValidationError
        raise ValidationError(
            f"Unsupported image type '{content_type}'. "
            f"Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    return image


# ─────────────────────────────────────────
# TEXT HELPERS
# ─────────────────────────────────────────

def sanitize_html(content):
    """
    Sanitize HTML content — allow only safe tags.
    Used for blog post bodies and book descriptions.
    """
    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'cite',
        'code', 'dd', 'del', 'dfn', 'dl', 'dt', 'em', 'h1', 'h2',
        'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins', 'kbd',
        'li', 'ol', 'p', 'pre', 'q', 's', 'samp', 'small', 'span',
        'strike', 'strong', 'sub', 'sup', 'table', 'tbody', 'td',
        'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var',
    ]
    allowed_attrs = {
        '*': ['class', 'id'],
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'blockquote': ['cite'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan', 'scope'],
    }
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def calculate_reading_time(text, wpm=200):
    """Estimate reading time in minutes based on word count."""
    word_count = len(text.split())
    minutes = max(1, round(word_count / wpm))
    return minutes


def build_absolute_uri(path):
    """Build absolute URL from relative path using SITE_URL."""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    return f"{site_url.rstrip('/')}/{path.lstrip('/')}"


# ─────────────────────────────────────────
# CUSTOM EXCEPTION HANDLER
# ─────────────────────────────────────────

def custom_exception_handler(exc, context):
    """
    Custom exception handler that wraps DRF errors in our
    standard envelope format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'status': 'error',
            'message': _extract_error_message(response.data),
            'errors': response.data,
        }
        response.data = error_data

    return response


def _extract_error_message(data):
    """Extract a human-readable top-level message from error data."""
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        first_key = next(iter(data), None)
        if first_key:
            val = data[first_key]
            if isinstance(val, list) and val:
                return f"{first_key}: {val[0]}"
            return str(val)
    if isinstance(data, list) and data:
        return str(data[0])
    return 'An error occurred.'


# ─────────────────────────────────────────
# SLUG HELPERS
# ─────────────────────────────────────────

def unique_slug(model_class, title, slug_field='slug'):
    """Generate a unique slug for a model, appending counter if needed."""
    from django.utils.text import slugify
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
