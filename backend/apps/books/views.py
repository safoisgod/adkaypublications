"""
Views for the Books app.
"""
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.pagination import StandardResultsPagination, SmallResultsPagination
from .models import Book, Genre
from .serializers import BookListSerializer, BookDetailSerializer, GenreSerializer
from .filters import BookFilter


class BookListView(generics.ListAPIView):
    """
    GET /api/v1/books/
    Paginated, filterable, searchable book catalogue.

    Query params:
      - ?search=      full-text search on title, author, description
      - ?genre=       filter by genre slug
      - ?author=      filter by author slug
      - ?is_featured= true|false
      - ?is_bestseller= true|false
      - ?is_new_release= true|false
      - ?min_price=   price range
      - ?max_price=
      - ?year=        publication year
      - ?ordering=    title | -published_date | price | -price
    """
    serializer_class = BookListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'subtitle', 'description', 'isbn', 'authors__full_name']
    ordering_fields = ['title', 'published_date', 'price', 'created_at']
    ordering = ['-published_date']

    def get_queryset(self):
        return (
            Book.objects
            .filter(is_published=True)
            .select_related('genre')
            .prefetch_related('authors')
            .distinct()
        )


class BookFeaturedView(generics.ListAPIView):
    """
    GET /api/v1/books/featured/
    Featured books — no pagination, for homepage/widgets.
    """
    serializer_class = BookListSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Book.objects
            .filter(is_published=True, is_featured=True)
            .select_related('genre')
            .prefetch_related('authors')
            .order_by('-published_date')[:6]
        )


class BookBestsellerView(generics.ListAPIView):
    """
    GET /api/v1/books/bestsellers/
    """
    serializer_class = BookListSerializer
    permission_classes = [AllowAny]
    pagination_class = SmallResultsPagination

    def get_queryset(self):
        return (
            Book.objects
            .filter(is_published=True, is_bestseller=True)
            .select_related('genre')
            .prefetch_related('authors')
            .order_by('-published_date')
        )


class BookNewReleasesView(generics.ListAPIView):
    """
    GET /api/v1/books/new-releases/
    """
    serializer_class = BookListSerializer
    permission_classes = [AllowAny]
    pagination_class = SmallResultsPagination

    def get_queryset(self):
        return (
            Book.objects
            .filter(is_published=True, is_new_release=True)
            .select_related('genre')
            .prefetch_related('authors')
            .order_by('-published_date')
        )


class BookDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/books/<slug>/
    Full book detail with related books.
    """
    serializer_class = BookDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Book.objects
            .filter(is_published=True)
            .select_related('genre')
            .prefetch_related('authors')
        )


class GenreListView(generics.ListAPIView):
    """
    GET /api/v1/books/genres/
    All genres with book counts.
    """
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Genre.objects.all().prefetch_related('books')
