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
    Idempotent — re-subscribing a lapsed subscriber reactivates them.
    """
    permission_classes = [AllowAny]
    throttle_classes = [NewsletterRateThrottle]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscriber, created = serializer.save()

        if created:
            try:
                send_welcome_email.delay(subscriber.pk)
            except Exception as e:
                logger.warning(f"Celery unavailable, welcome email skipped: {e}")

            logger.info(f"New newsletter subscriber: {subscriber.email}")
            return Response(
                {'message': 'You have successfully subscribed to our newsletter.'},
                status=status.HTTP_201_CREATED,
            )
        else:
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
