"""
Abstract base models shared across all apps.
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at fields.
    All models in this project inherit from this.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class PublishableModel(TimeStampedModel):
    """
    Abstract model for content that can be published/unpublished.
    """
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def publish(self):
        self.is_published = True

        # ✅ Only set if NOT manually provided
        if not self.published_at:
            self.published_at = timezone.now()

        self.save(update_fields=['is_published', 'published_at', 'updated_at'])

    def unpublish(self):
        self.is_published = False
        self.save(update_fields=['is_published', 'updated_at'])


class SEOModel(models.Model):
    """
    Abstract model for SEO metadata.
    """
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True
