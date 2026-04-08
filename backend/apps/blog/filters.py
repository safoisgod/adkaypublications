"""
Filter classes for the Blog app.
"""
import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    """
    Filterset for blog post list endpoint.
    """
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    tag = django_filters.CharFilter(field_name='tags__slug', lookup_expr='exact')
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='iexact')
    year = django_filters.NumberFilter(field_name='published_at__year')
    month = django_filters.NumberFilter(field_name='published_at__month')
    is_featured = django_filters.BooleanFilter()

    class Meta:
        model = Post
        fields = ['category', 'tag', 'author', 'year', 'month', 'is_featured']
