"""
Services app model.
"""
from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel
from apps.core.utils import service_image_path
from cloudinary.models import CloudinaryField  # ✅ added


class Service(TimeStampedModel):
    """
    A service offered by the publishing company
    (e.g. Editing, Design, Distribution, PR).
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    icon = models.CharField(
        max_length=2200, blank=True,
        help_text='Icon name or SVG string for frontend rendering.',
    )
    short_description = models.CharField(
        max_length=300,
        help_text='Shown on service cards.',
    )
    full_description = models.TextField(
        blank=True,
        help_text='Detailed description for the service detail page.',
    )
    image = CloudinaryField(  # ✅ updated
        'image',
        null=True,
        blank=True,
    )
    features = models.TextField(
        blank=True,
        help_text='JSON list of feature bullet points.',
    )
    cta_text = models.CharField(
        max_length=100, default='Learn More',
        help_text='Call-to-action button label.',
    )
    cta_link = models.URLField(blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'title']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.full_description:
            from apps.core.utils import sanitize_html
            self.full_description = sanitize_html(self.full_description)
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        return self.image.url if self.image else None

    @property
    def features_list(self):
        import json
        if self.features:
            try:
                return json.loads(self.features)
            except (json.JSONDecodeError, ValueError):
                return [f.strip() for f in self.features.split('\n') if f.strip()]
        return []