"""
Serializers for the Contact app.
"""
import re
from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Validates and creates a contact form submission.
    Read-only fields are excluded from the write interface.
    """

    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone',
            'subject', 'message', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        if len(value) > 200:
            raise serializers.ValidationError('Name must be under 200 characters.')
        return value

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError(
                'Message must be at least 20 characters.'
            )
        if len(value) > 5000:
            raise serializers.ValidationError(
                'Message must be under 5000 characters.'
            )
        return value

    def validate_phone(self, value):
        if value:
            # Strip spaces/dashes, allow +, digits only
            cleaned = re.sub(r'[\s\-\(\)]', '', value)
            if not re.match(r'^\+?\d{7,15}$', cleaned):
                raise serializers.ValidationError('Enter a valid phone number.')
        return value

    def validate_email(self, value):
        return value.lower().strip()
