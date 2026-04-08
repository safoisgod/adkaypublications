"""
Celery tasks for the Newsletter app.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger('apps.newsletter')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, subscriber_id):
    """Send a welcome email to a new newsletter subscriber."""
    try:
        from .models import Subscriber
        sub = Subscriber.objects.get(pk=subscriber_id)

        name = sub.first_name or 'Reader'
        subject = f"Welcome to {settings.SITE_NAME} — You're in!"
        body = (
            f"Hi {name},\n\n"
            f"Thank you for subscribing to the {settings.SITE_NAME} newsletter.\n\n"
            f"You'll receive updates on our latest books, author interviews, "
            f"industry news, and exclusive offers.\n\n"
            f"To manage your subscription or unsubscribe at any time, visit:\n"
            f"{settings.FRONTEND_URL}/unsubscribe/?token={sub.unsubscribe_token}\n\n"
            f"Best regards,\n"
            f"The {settings.SITE_NAME} Team"
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.email],
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {sub.email}")

    except Exception as exc:
        logger.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc)
