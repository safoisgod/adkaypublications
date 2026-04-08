"""
Views for the Authors app.
"""
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.pagination import StandardResultsPagination
from .models import Author
from .serializers import AuthorListSerializer, AuthorDetailSerializer


class AuthorListView(generics.ListAPIView):
    """
    GET /api/v1/authors/
    Returns paginated list of active authors.
    Supports: ?search=name, ?is_featured=true, ?ordering=display_order
    """
    serializer_class = AuthorListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured']
    search_fields = ['full_name', 'role', 'bio']
    ordering_fields = ['display_order', 'full_name', 'created_at']
    ordering = ['display_order']

    def get_queryset(self):
        return (
            Author.objects
            .filter(is_active=True)
            .prefetch_related('books')
        )


class AuthorFeaturedView(generics.ListAPIView):
    """
    GET /api/v1/authors/featured/
    Returns featured authors — no pagination, for homepage use.
    """
    serializer_class = AuthorListSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Author.objects
            .filter(is_active=True, is_featured=True)
            .prefetch_related('books')
            .order_by('display_order')[:8]
        )


class AuthorDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/authors/<slug>/
    Full author profile with their published books.
    """
    serializer_class = AuthorDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Author.objects
            .filter(is_active=True)
            .prefetch_related('books__genre')
        )
