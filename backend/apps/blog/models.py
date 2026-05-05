"""
Blog app models — Category, Tag, Post, PostContent.
"""
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from apps.core.models import TimeStampedModel, PublishableModel, SEOModel
from apps.core.utils import calculate_reading_time
from cloudinary.models import CloudinaryField
from apps.core.image_utils import CloudinaryImageMixin


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#2563EB')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Post(CloudinaryImageMixin, PublishableModel, SEOModel):
    CLOUDINARY_IMAGE_FIELDS = ['cover_image']

    title = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)

    author = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='posts',
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='posts',
    )

    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)

    cover_image = CloudinaryField('cover_image', null=True, blank=True)

    excerpt = models.TextField(blank=True)

    reading_time = models.PositiveIntegerField(
        default=1,
        editable=False,
        help_text='Auto-calculated in minutes.'
    )

    views = models.PositiveIntegerField(default=0, editable=False)

    is_featured = models.BooleanField(default=False, db_index=True)
    allow_comments = models.BooleanField(default=True)

    published_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()

        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1

        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    @property
    def cover_url(self):
        return self.cover_image.url if self.cover_image else None

    @property
    def author_name(self):
        return self.author.full_name if self.author else 'Editorial Team'

    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(
            views=models.F('views') + 1
        )

    # 🔥 CORE FIX: centralized reading time updater
    def update_reading_time(self):
        reading_time = self.calculate_reading_time_from_blocks()
        Post.objects.filter(pk=self.pk).update(reading_time=reading_time)

    def calculate_reading_time_from_blocks(self):
        import re

        text_parts = []

        for content in self.contents.all():
            if content.content_type == 'text' and content.text:
                text_parts.append(content.text)

            # Optional weighting for non-text content
            elif content.content_type == 'image':
                text_parts.append('image')  # small weight

            elif content.content_type == 'video':
                text_parts.append('video')  # small weight

        combined_text = " ".join(text_parts)

        # Strip HTML
        plain = re.sub(r'<[^>]+>', ' ', combined_text)

        return calculate_reading_time(plain)


class PostContent(models.Model):
    TEXT = 'text'
    IMAGE = 'image'
    VIDEO = 'video'

    CONTENT_TYPES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='contents'
    )

    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)

    text = models.TextField(blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    video_url = models.URLField(blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 🔥 Always update after save
        self.post.update_reading_time()

    def delete(self, *args, **kwargs):
        post = self.post
        super().delete(*args, **kwargs)

        # 🔥 Always update after delete
        post.update_reading_time()

    def __str__(self):
        return f"{self.post.title} - {self.content_type} ({self.order})"