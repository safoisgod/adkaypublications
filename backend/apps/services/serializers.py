"""
Serializers for the Services app.
"""
from rest_framework import serializers
from .models import Service


class ServiceListSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()
    features_list = serializers.ReadOnlyField()

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'slug', 'icon', 'short_description',
            'image_url', 'features_list', 'cta_text', 'cta_link',
            'is_featured', 'display_order',
        ]


class ServiceDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()
    features_list = serializers.ReadOnlyField()

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'slug', 'icon', 'short_description',
            'full_description', 'image_url', 'features_list',
            'cta_text', 'cta_link', 'is_featured',
            'display_order', 'created_at',
        ]
