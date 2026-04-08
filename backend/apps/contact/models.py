"""
Contact app model — stores contact form submissions.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class ContactMessage(TimeStampedModel):
    """
    A message submitted through the contact form.
    Stored in DB and triggers an email notification to admin.
    """

    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('submission', 'Manuscript Submission'),
        ('rights', 'Rights & Licensing'),
        ('press', 'Press & Media'),
        ('partnership', 'Partnership'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(
        max_length=50,
        choices=SUBJECT_CHOICES,
        default='general',
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    is_replied = models.BooleanField(default=False)
    replied_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(
        blank=True,
        help_text='Internal notes — not visible to sender.',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"[{self.get_subject_display()}] {self.name} <{self.email}>"

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def mark_replied(self):
        from django.utils import timezone
        self.is_replied = True
        self.replied_at = timezone.now()
        self.save(update_fields=['is_replied', 'replied_at'])