"""
Newsletter app model.
"""
import uuid
from django.db import models
from apps.core.models import TimeStampedModel


class Subscriber(TimeStampedModel):
    """
    Newsletter subscriber.
    Uses a UUID token for unsubscribe links (no auth required).
    """
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribe_token = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True,
        help_text='Used in unsubscribe links — never expose to unauthorized users.',
    )
    source = models.CharField(
        max_length=100, blank=True,
        help_text='Where the user subscribed (e.g. homepage, book-detail).',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return self.email

    def unsubscribe(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def confirm(self):
        from django.utils import timezone
        self.confirmed_at = timezone.now()
        self.is_active = True
        self.save(update_fields=['confirmed_at', 'is_active'])