"""
Views for the Contact app.
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from .serializers import ContactMessageSerializer
from .tasks import send_contact_notification

logger = logging.getLogger('apps.contact')


class ContactRateThrottle(AnonRateThrottle):
    scope = 'contact'
    rate = '5/hour'


class ContactMessageView(APIView):
    """
    POST /api/v1/contact/
    Submit a contact form message.
    Rate-limited to 5/hour per IP.
    Triggers async email notification via Celery.
    """
    permission_classes = [AllowAny]
    throttle_classes = [ContactRateThrottle]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        # Fire async email notification
        try:
            send_contact_notification.delay(message.pk)
        except Exception as e:
            # Don't fail the request if Celery is unavailable
            logger.warning(f"Celery unavailable, contact notification skipped: {e}")

        logger.info(
            f"Contact form submitted by {message.email} "
            f"[subject={message.subject}, id={message.pk}]"
        )

        return Response(
            {
                'message': 'Your message has been received. We will be in touch shortly.',
                'reference': f'#{message.pk}',
            },
            status=status.HTTP_201_CREATED,
        )
