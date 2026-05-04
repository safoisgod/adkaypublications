"""
Blog app models — Category, Tag, Post, PostContent.
"""
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from apps.core.models import TimeStampedModel, PublishableModel, SEOModel
from apps.core.utils import blog_cover_path, calculate_reading_time
from cloudinary.models import CloudinaryField
from apps.core.image_utils import CloudinaryImageMixin


class Category(TimeStampedModel):
    """Blog post category."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default='#2563EB',
        help_text='Hex colour for UI badge (e.g. #2563EB).'
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    """Blog post tag."""
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
    """Returns only published posts."""
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Post(CloudinaryImageMixin, PublishableModel, SEOModel):
    CLOUDINARY_IMAGE_FIELDS = ['cover_image']

    """
    Blog post.
    """

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

    cover_image = CloudinaryField(
        'cover_image',
        null=True,
        blank=True,
    )

    excerpt = models.TextField(
        blank=True,
        help_text='Short summary shown on list/card views.',
    )

    # ⚠️ KEEP THIS for now (backward compatibility)
    # body = models.TextField(
    #     help_text='Full post content (HTML allowed).',
    # )

    reading_time = models.PositiveIntegerField(
        default=1,
        help_text='Auto-calculated in minutes.',
        editable=False,
    )

    views = models.PositiveIntegerField(default=0, editable=False)

    is_featured = models.BooleanField(default=False, db_index=True)
    allow_comments = models.BooleanField(default=True)

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set manually or auto-filled when publishing."
    )

    # Managers
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = [
            models.F('published_at').desc(nulls_last=True),
            '-created_at'
        ]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Slug generation
        if not self.slug:
            self.slug = self._generate_unique_slug()

        # Auto-set published date
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        # Reading time calculation (still based on body for now)
        if self.body:
            import re
            plain = re.sub(r'<[^>]+>', ' ', self.body)
            self.reading_time = calculate_reading_time(plain)

            from apps.core.utils import sanitize_html
            self.body = sanitize_html(self.body)

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
        if self.author:
            return self.author.full_name
        return 'Editorial Team'

    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(
            views=models.F('views') + 1
        )


# Future enhancement: Flexible content blocks (text, image, video) for richer posts.
class PostContent(models.Model):
    """Flexible content blocks for a blog post."""

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

    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPES
    )

    text = models.TextField(blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    video_url = models.URLField(blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Post Content'
        verbose_name_plural = 'Post Contents'

    def __str__(self):
        return f"{self.post.title} - {self.content_type} ({self.order})"