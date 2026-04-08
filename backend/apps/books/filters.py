"""
Filter classes for the Books app.
"""
import django_filters
from .models import Book, Genre


class BookFilter(django_filters.FilterSet):
    """
    Filterset for book list endpoint.
    Supports: genre, year, price range, flags, language.
    """
    genre = django_filters.CharFilter(field_name='genre__slug', lookup_expr='exact')
    author = django_filters.CharFilter(field_name='authors__slug', lookup_expr='exact')
    language = django_filters.CharFilter(lookup_expr='iexact')
    year = django_filters.NumberFilter(field_name='published_date__year')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_featured = django_filters.BooleanFilter()
    is_bestseller = django_filters.BooleanFilter()
    is_new_release = django_filters.BooleanFilter()

    class Meta:
        model = Book
        fields = [
            'genre', 'author', 'language', 'year',
            'min_price', 'max_price',
            'is_featured', 'is_bestseller', 'is_new_release',
        ]
