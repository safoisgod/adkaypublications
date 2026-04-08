"""
Authors / Team members model.
"""
from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel
from apps.core.utils import author_photo_path
from cloudinary.models import CloudinaryField  # ✅ added


class Author(TimeStampedModel):
    """
    Represents an author or team member displayed on the site.
    Can optionally be linked to a CustomUser account.
    """
    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='author_profile',
    )
    full_name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    photo = CloudinaryField(  # ✅ updated
        'photo',
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=100,
        help_text='e.g. Senior Editor, Fiction Author, Art Director',
    )
    bio = models.TextField(blank=True)
    short_bio = models.CharField(max_length=300, blank=True)

    # Social links
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    website = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first.',
    )

    class Meta:
        ordering = ['display_order', 'full_name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.full_name)
        slug = base_slug
        counter = 1
        while Author.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None

    @property
    def book_count(self):
        return self.books.filter(is_published=True).count()