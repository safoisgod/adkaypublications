"""
Homepage aggregated API endpoint.
Returns everything the homepage needs in one request.
"""
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.books.models import Book
from apps.blog.models import Post
from apps.authors.models import Author
from apps.books.serializers import BookListSerializer
from apps.blog.serializers import PostListSerializer
from apps.authors.serializers import AuthorListSerializer


class HomepageView(APIView):
    """
    GET /api/v1/homepage/
    Aggregated endpoint: featured books, latest posts, featured authors, stats.
    Cached for 5 minutes.
    """
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 5))
    def get(self, request):
        # Featured books (up to 6)
        featured_books = (
            Book.objects
            .filter(is_published=True, is_featured=True)
            .select_related('genre')
            .prefetch_related('authors')
            .order_by('-published_date')[:6]
        )

        # Latest blog posts (up to 4)
        latest_posts = (
            Post.objects
            .filter(is_published=True)
            .select_related('author', 'category')
            .order_by('-published_at')[:4]
        )

        # Featured authors (up to 6)
        featured_authors = (
            Author.objects
            .filter(is_featured=True)
            .order_by('display_order')[:6]
        )

        # Platform stats
        stats = {
            'total_books': Book.objects.filter(is_published=True).count(),
            'total_posts': Post.objects.filter(is_published=True).count(),
            'total_authors': Author.objects.filter(is_active=True).count(),
        }

        return Response({
            'featured_books': BookListSerializer(
                featured_books, many=True, context={'request': request}
            ).data,
            'latest_posts': PostListSerializer(
                latest_posts, many=True, context={'request': request}
            ).data,
            'featured_authors': AuthorListSerializer(
                featured_authors, many=True, context={'request': request}
            ).data,
            'stats': stats,
        })
