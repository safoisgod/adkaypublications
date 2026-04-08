"""
Books app models — Genre and Book.
"""
from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel, PublishableModel, SEOModel
from apps.core.utils import book_cover_path
from cloudinary.models import CloudinaryField  # ✅ added


class Genre(TimeStampedModel):
    """Book genre/category (e.g. Fiction, Non-Fiction, Science)."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Book(PublishableModel, SEOModel):
    """
    Core Book model.
    Linked M2M to Author; single Genre FK.
    """
    title = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)

    authors = models.ManyToManyField(
        'authors.Author',
        related_name='books',
        blank=True,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='books',
    )

    cover_image = CloudinaryField(  # ✅ updated
        'cover_image',
        null=True,
        blank=True,
    )
    description = models.TextField(
        help_text='Full book description (HTML allowed).'
    )
    excerpt = models.TextField(
        blank=True,
        help_text='Short excerpt shown on list/card view.',
    )

    # Publication details
    isbn = models.CharField(max_length=20, blank=True, db_index=True)
    publisher = models.CharField(max_length=200, blank=True)
    published_date = models.DateField(null=True, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default='English')
    edition = models.CharField(max_length=50, blank=True)

    # Commerce
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    buy_link = models.URLField(blank=True)

    # Flags
    is_featured = models.BooleanField(default=False, db_index=True)
    is_bestseller = models.BooleanField(default=False, db_index=True)
    is_new_release = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        # Sanitize HTML description
        if self.description:
            from apps.core.utils import sanitize_html
            self.description = sanitize_html(self.description)
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    @property
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        return None

    @property
    def author_names(self):
        return ', '.join(a.full_name for a in self.authors.all())