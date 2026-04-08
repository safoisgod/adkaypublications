"""
Custom User model — email is the primary identifier.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.utils import user_avatar_path
from cloudinary.models import CloudinaryField  # ✅ added


class CustomUserManager(BaseUserManager):
    """
    Manager where email (not username) is the unique identifier.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email address is required.'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Extended user model.
    - Email is the login field (not username)
    - Avatar, bio, author flag, verification status
    """
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        help_text='Optional display name.',
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
    )
    avatar = CloudinaryField(  # ✅ updated
        'avatar',
        null=True,
        blank=True,
    )
    bio = models.TextField(blank=True)
    is_author = models.BooleanField(
        default=False,
        help_text='Designates whether this user is a content author.',
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Email address has been verified.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.username or self.email

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None