"""
Views for the Services app.
"""
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Service
from .serializers import ServiceListSerializer, ServiceDetailSerializer


class ServiceListView(generics.ListAPIView):
    """GET /api/v1/services/"""
    serializer_class = ServiceListSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by('display_order')


class ServiceDetailView(generics.RetrieveAPIView):
    """GET /api/v1/services/<slug>/"""
    serializer_class = ServiceDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Service.objects.filter(is_active=True)
