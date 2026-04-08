"""
Celery tasks for the Contact app.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger('apps.contact')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_contact_notification(self, message_id):
    """
    Send email notification to admin when a new contact message arrives.
    Retries up to 3 times on failure.
    """
    try:
        from .models import ContactMessage
        msg = ContactMessage.objects.get(pk=message_id)

        subject = f"[Contact] {msg.get_subject_display()} — {msg.name}"
        body = (
            f"New contact message received:\n\n"
            f"Name:    {msg.name}\n"
            f"Email:   {msg.email}\n"
            f"Phone:   {msg.phone or 'N/A'}\n"
            f"Subject: {msg.get_subject_display()}\n\n"
            f"Message:\n{msg.message}\n\n"
            f"---\n"
            f"Received: {msg.created_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"Admin URL: {settings.SITE_URL}/admin/contact/contactmessage/{msg.pk}/change/"
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        # Also send auto-reply to sender
        send_contact_autoreply.delay(message_id)

        logger.info(f"Contact notification sent for message #{message_id}")

    except Exception as exc:
        logger.error(f"Failed to send contact notification: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_contact_autoreply(self, message_id):
    """
    Send a polite auto-reply to the person who submitted the form.
    """
    try:
        from .models import ContactMessage
        msg = ContactMessage.objects.get(pk=message_id)

        subject = f"Thank you for reaching out — {settings.SITE_NAME}"
        body = (
            f"Dear {msg.name},\n\n"
            f"Thank you for contacting us. We have received your message "
            f"and will get back to you within 2–3 business days.\n\n"
            f"Your reference: #{msg.pk}\n"
            f"Subject: {msg.get_subject_display()}\n\n"
            f"Best regards,\n"
            f"The {settings.SITE_NAME} Team\n"
            f"{settings.FRONTEND_URL}"
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[msg.email],
            fail_silently=False,
        )

        logger.info(f"Auto-reply sent to {msg.email} for message #{message_id}")

    except Exception as exc:
        logger.error(f"Failed to send auto-reply: {exc}")
        raise self.retry(exc=exc)
