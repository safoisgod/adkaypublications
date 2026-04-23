"""
Views for the Newsletter app.
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from .models import Subscriber
from .serializers import SubscribeSerializer, UnsubscribeSerializer
from .tasks import send_welcome_email

logger = logging.getLogger('apps.newsletter')


class NewsletterRateThrottle(AnonRateThrottle):
    scope = 'anon'
    rate = '20/hour'


class SubscribeView(APIView):
    """
    POST /api/v1/newsletter/subscribe/
    Subscribe an email to the newsletter.
    """
    permission_classes = [AllowAny]
    throttle_classes = [NewsletterRateThrottle]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscriber, created = serializer.save()

        if created:
            logger.info(f"New subscriber created: {subscriber.email}")

            # ─────────────────────────────────────────
            # CELERY TASK TRIGGER (SAFE VERSION)
            # ─────────────────────────────────────────
            try:
                result = send_welcome_email.delay(subscriber.pk)

                # optional debug (VERY useful)
                logger.info(
                    f"Celery task queued: task_id={result.id} for {subscriber.email}"
                )

            except Exception as e:
                # DO NOT silently hide this in production
                logger.error(
                    f"FAILED to queue welcome email task for {subscriber.email}: {e}"
                )
                return Response(
                    {
                        "message": "Subscribed, but email system failed to trigger."
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {'message': 'You have successfully subscribed to our newsletter.'},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {'message': 'You are already subscribed to our newsletter.'},
            status=status.HTTP_200_OK,
        )

class UnsubscribeView(APIView):
    """
    POST /api/v1/newsletter/unsubscribe/
    Unsubscribe using email or UUID token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        token = serializer.validated_data.get('token')

        try:
            if token:
                subscriber = Subscriber.objects.get(unsubscribe_token=token)
            else:
                subscriber = Subscriber.objects.get(email=email.lower())

            if subscriber.is_active:
                subscriber.unsubscribe()
                logger.info(f"Unsubscribed: {subscriber.email}")
                return Response(
                    {'message': 'You have been unsubscribed from our newsletter.'},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {'message': 'This email is not currently subscribed.'},
                    status=status.HTTP_200_OK,
                )

        except Subscriber.DoesNotExist:
            # Return 200 to prevent email enumeration
            return Response(
                {'message': 'If this email was subscribed, it has been removed.'},
                status=status.HTTP_200_OK,
            )
