"""
Blog app models — Category, Tag, Post.
"""
from django.db import models
from django.utils.text import slugify
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


class Post(CloudinaryImageMixin, PublishableModel, SEOModel):
    CLOUDINARY_IMAGE_FIELDS = ['cover_image']
    """
    Blog post.
    Author linked to CustomUser.
    Reading time auto-calculated on save.
    Views tracked via dedicated endpoint.
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

    cover_image = CloudinaryField(  # ✅ updated
        'cover_image',
        null=True,
        blank=True,
    )
    excerpt = models.TextField(
        blank=True,
        help_text='Short summary shown on list/card views.',
    )
    body = models.TextField(
        help_text='Full post content (HTML allowed).',
    )

    reading_time = models.PositiveIntegerField(
        default=1,
        help_text='Auto-calculated in minutes.',
        editable=False,
    )
    views = models.PositiveIntegerField(default=0, editable=False)
    is_featured = models.BooleanField(default=False, db_index=True)
    allow_comments = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        # Auto-calculate reading time from body
        if self.body:
            # Strip basic HTML tags for word count
            import re
            plain = re.sub(r'<[^>]+>', ' ', self.body)
            self.reading_time = calculate_reading_time(plain)
            # Sanitize HTML
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
        """Thread-safe view increment."""
        Post.objects.filter(pk=self.pk).update(views=models.F('views') + 1)