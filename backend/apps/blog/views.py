"""
Views for the Blog app.
"""
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.pagination import StandardResultsPagination
from .models import Post, Category, Tag
from .serializers import (
    PostListSerializer, PostDetailSerializer,
    CategorySerializer, TagSerializer,
)
from .filters import PostFilter


class PostListView(generics.ListAPIView):
    """
    GET /api/v1/blog/posts/
    Paginated, filterable list of published posts.

    Query params:
      - ?search=       search in title, excerpt, body
      - ?category=     category slug
      - ?tag=          tag slug
      - ?author=       author username
      - ?is_featured=  true|false
      - ?year= / ?month=
      - ?ordering=     -published_at | views | reading_time
    """
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'subtitle', 'excerpt', 'body', 'author__first_name', 'author__last_name']
    ordering_fields = ['published_at', 'views', 'reading_time', 'created_at']
    ordering = ['-published_at']

    def get_queryset(self):
        return (
            Post.objects
            .filter(is_published=True)
            .select_related('author', 'category')
            .prefetch_related('tags')
            .distinct()
        )


class PostFeaturedView(generics.ListAPIView):
    """
    GET /api/v1/blog/posts/featured/
    No pagination — for homepage/widgets.
    """
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Post.objects
            .filter(is_published=True, is_featured=True)
            .select_related('author', 'category')
            .prefetch_related('tags')
            .order_by('-published_at')[:4]
        )


class PostDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/blog/posts/<slug>/
    Full post detail with related posts.
    """
    serializer_class = PostDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Post.objects
            .filter(is_published=True)
            .select_related('author', 'category')
            .prefetch_related('tags')
        )


class PostIncrementViewView(APIView):
    """
    POST /api/v1/blog/posts/<slug>/view/
    Increment view counter — called by frontend when user reads a post.
    """
    permission_classes = [AllowAny]

    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug, is_published=True)
            post.increment_views()
            return Response({'views': post.views + 1}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


class CategoryListView(generics.ListAPIView):
    """
    GET /api/v1/blog/categories/
    All categories with post counts.
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Category.objects.all().prefetch_related('posts')


class TagListView(generics.ListAPIView):
    """
    GET /api/v1/blog/tags/
    All tags with post counts.
    """
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Tag.objects
            .prefetch_related('posts')
            .filter(posts__is_published=True)
            .distinct()
        )
