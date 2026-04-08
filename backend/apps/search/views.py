"""
Search app — unified search across Books, Posts, and Authors.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db.models import Q

from apps.books.models import Book
from apps.blog.models import Post
from apps.authors.models import Author
from apps.books.serializers import BookListSerializer
from apps.blog.serializers import PostListSerializer
from apps.authors.serializers import AuthorListSerializer

logger = logging.getLogger('apps.search')

MAX_RESULTS_PER_TYPE = 6


class SearchView(APIView):
    """
    GET /api/v1/search/?q=<query>&type=<books|posts|authors|all>

    Searches across:
      - Books (title, subtitle, description, author name, ISBN)
      - Blog Posts (title, subtitle, excerpt, body)
      - Authors (full name, bio, role)

    Query params:
      - q      (required) Search term, min 2 characters
      - type   (optional) Filter to a specific resource type
                          Options: books | posts | authors | all (default)
      - limit  (optional) Max results per type (default 6, max 12)

    Returns:
      {
        "query": "...",
        "total": N,
        "results": {
          "books": [...],
          "posts": [...],
          "authors": [...]
        }
      }
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all').lower()
        try:
            limit = min(int(request.query_params.get('limit', MAX_RESULTS_PER_TYPE)), 12)
        except (ValueError, TypeError):
            limit = MAX_RESULTS_PER_TYPE

        # Validate query
        if not query:
            return Response(
                {'detail': 'Search query parameter "q" is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(query) < 2:
            return Response(
                {'detail': 'Search query must be at least 2 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(query) > 200:
            return Response(
                {'detail': 'Search query must be under 200 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_types = {'all', 'books', 'posts', 'authors'}
        if search_type not in valid_types:
            search_type = 'all'

        results = {}
        total = 0

        # ── BOOKS ─────────────────────────────────────────────────────────
        if search_type in ('all', 'books'):
            book_qs = (
                Book.objects
                .filter(is_published=True)
                .filter(
                    Q(title__icontains=query) |
                    Q(subtitle__icontains=query) |
                    Q(description__icontains=query) |
                    Q(authors__full_name__icontains=query) |
                    Q(isbn__icontains=query) |
                    Q(genre__name__icontains=query)
                )
                .select_related('genre')
                .prefetch_related('authors')
                .distinct()[:limit]
            )
            book_data = BookListSerializer(book_qs, many=True, context={'request': request}).data
            results['books'] = book_data
            total += len(book_data)

        # ── BLOG POSTS ─────────────────────────────────────────────────────
        if search_type in ('all', 'posts'):
            post_qs = (
                Post.objects
                .filter(is_published=True)
                .filter(
                    Q(title__icontains=query) |
                    Q(subtitle__icontains=query) |
                    Q(excerpt__icontains=query) |
                    Q(body__icontains=query) |
                    Q(category__name__icontains=query) |
                    Q(tags__name__icontains=query) |
                    Q(author__first_name__icontains=query) |
                    Q(author__last_name__icontains=query)
                )
                .select_related('author', 'category')
                .prefetch_related('tags')
                .distinct()[:limit]
            )
            post_data = PostListSerializer(post_qs, many=True, context={'request': request}).data
            results['posts'] = post_data
            total += len(post_data)

        # ── AUTHORS ────────────────────────────────────────────────────────
        if search_type in ('all', 'authors'):
            author_qs = (
                Author.objects
                .filter(is_active=True)
                .filter(
                    Q(full_name__icontains=query) |
                    Q(bio__icontains=query) |
                    Q(short_bio__icontains=query) |
                    Q(role__icontains=query)
                )
                .prefetch_related('books')
                .distinct()[:limit]
            )
            author_data = AuthorListSerializer(author_qs, many=True, context={'request': request}).data
            results['authors'] = author_data
            total += len(author_data)

        logger.info(f"Search: q='{query}' type={search_type} total={total}")

        return Response({
            'query': query,
            'type': search_type,
            'total': total,
            'results': results,
        })
