"""
Serializers for the Newsletter app.
"""
from rest_framework import serializers
from .models import Subscriber


class SubscribeSerializer(serializers.Serializer):
    """Handles newsletter subscription requests."""
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    source = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_email(self, value):
        return value.lower().strip()

    def create(self, validated_data):
        email = validated_data['email']
        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={
                'first_name': validated_data.get('first_name', ''),
                'source': validated_data.get('source', ''),
            }
        )
        if not created:
            # Re-subscribe if they previously unsubscribed
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=['is_active'])
        return subscriber, created


class UnsubscribeSerializer(serializers.Serializer):
    """Handles newsletter unsubscription by email or token."""
    email = serializers.EmailField(required=False)
    token = serializers.UUIDField(required=False)

    def validate(self, attrs):
        if not attrs.get('email') and not attrs.get('token'):
            raise serializers.ValidationError(
                'Provide either email or unsubscribe token.'
            )
        return attrs
