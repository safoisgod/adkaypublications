"""
Celery tasks for the Newsletter app.
"""
import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger('apps.newsletter')


# ─────────────────────────────────────────
# EMAIL SIGNATURE (SHARED STYLE)
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
# WELCOME EMAIL
# ─────────────────────────────────────────
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, subscriber_id):
    """Send a welcome email to a new newsletter subscriber."""
    try:
        from .models import Subscriber
        sub = Subscriber.objects.get(pk=subscriber_id)

        name = sub.first_name or 'Reader'
        subject = f"Welcome to {settings.SITE_NAME} — You're in!"

        html_body = f"""
        <div style="font-family:Arial,sans-serif;font-size:15px;color:#333;">

            <p>Hi {name},</p>

            <p>
                Thank you for subscribing to the <strong>{settings.SITE_NAME}</strong> newsletter.
            </p>

            <p>
                You'll now receive updates on our latest books, author interviews,
                industry news, and exclusive offers.
            </p>

            <p>
                To manage or unsubscribe anytime, click below:<br>
                <a href="{settings.FRONTEND_URL}/unsubscribe/?token={sub.unsubscribe_token}" 
                   style="color:#1e4fa1;">
                    Manage Subscription
                </a>
            </p>

            <p>We’re glad to have you with us.</p>

            <p>
                Best regards,<br>
                The {settings.SITE_NAME} Team
            </p>

            {EMAIL_SIGNATURE_HTML}
        </div>
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_body),  # fallback plain text
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sub.email],
            reply_to=[getattr(settings, "ADMIN_EMAIL", settings.DEFAULT_FROM_EMAIL)],
        )

        email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Welcome email sent to {sub.email}")

    except Exception as exc:
        logger.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc)