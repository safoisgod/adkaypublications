"""
Celery tasks for the Contact app.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger('apps.contact')


# ─────────────────────────────────────────
# EMAIL SIGNATURE (REUSABLE)
# ─────────────────────────────────────────
EMAIL_SIGNATURE_HTML = """
<br><br>
<hr style="border:0;border-top:1px solid #eaeaea;margin:20px 0;">

<div style="font-family:Arial,sans-serif;font-size:14px;color:#333;">

    <p style="margin:0;font-size:16px;font-weight:bold;color:#1e4fa1;">
        A-D Kay Publications
    </p>

    <p style="margin:5px 0;font-style:italic;color:#555;">
        Rewriting history, one story at a time.
    </p>

    <p style="margin:10px 0;">
        📞 +233 500 119 0463<br>
        🌐 <a href="https://adkaypublications.com" style="color:#1e4fa1;">
            adkaypublications.com
        </a>
    </p>

    <p style="margin:10px 0;">
        <strong>Follow us:</strong><br>
        X: @adkay_gh<br>
        Instagram: @adkay_gh<br>
        Facebook: adkaygh<br>
        LinkedIn: adkaygh
    </p>
</div>
"""


# ─────────────────────────────────────────
# ADMIN NOTIFICATION EMAIL
# ─────────────────────────────────────────
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_contact_notification(self, message_id):
    """
    Send email notification to admin when a new contact message arrives.
    """
    try:
        from .models import ContactMessage
        msg = ContactMessage.objects.get(pk=message_id)

        subject = f"[Contact] {msg.get_subject_display()} — {msg.name}"

        html_body = f"""
        <h3>New Contact Message</h3>

        <p><strong>Name:</strong> {msg.name}<br>
        <strong>Email:</strong> {msg.email}<br>
        <strong>Phone:</strong> {msg.phone or 'N/A'}<br>
        <strong>Subject:</strong> {msg.get_subject_display()}</p>

        <p><strong>Message:</strong><br>{msg.message}</p>

        <hr>
        <p style="font-size:12px;color:#777;">
            Received: {msg.created_at.strftime('%Y-%m-%d %H:%M UTC')}<br>
            Admin URL: {settings.SITE_URL}/admin/contact/contactmessage/{msg.pk}/change/
        </p>

        {EMAIL_SIGNATURE_HTML}
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_body),  # fallback plain text
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[getattr(settings, "ADMIN_EMAIL", "admin@adkaypublications.com")],
            reply_to=[msg.email],
        )

        email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=False)

        # Trigger auto-reply
        send_contact_autoreply.delay(message_id)

        logger.info(f"Contact notification sent for message #{message_id}")

    except Exception as exc:
        logger.error(f"Failed to send contact notification: {exc}")
        raise self.retry(exc=exc)


# ─────────────────────────────────────────
# AUTO REPLY EMAIL
# ─────────────────────────────────────────
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_contact_autoreply(self, message_id):
    """
    Send a polite auto-reply to the person who submitted the form.
    """
    try:
        from .models import ContactMessage
        msg = ContactMessage.objects.get(pk=message_id)

        subject = f"Thank you for reaching out — {settings.SITE_NAME}"

        html_body = f"""
        <p>Dear {msg.name},</p>

        <p>
            Thank you for contacting us. We have received your message
            and will get back to you within 2–3 business days.
        </p>

        <p>
            <strong>Reference:</strong> #{msg.pk}<br>
            <strong>Subject:</strong> {msg.get_subject_display()}
        </p>

        <p>
            Best regards,<br>
            The {settings.SITE_NAME} Team
        </p>

        {EMAIL_SIGNATURE_HTML}
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_body),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[msg.email],
        )

        email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Auto-reply sent to {msg.email} for message #{message_id}")

    except Exception as exc:
        logger.error(f"Failed to send auto-reply: {exc}")
        raise self.retry(exc=exc)