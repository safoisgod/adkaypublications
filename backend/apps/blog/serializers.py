"""
Serializers for the Blog app.
"""
from rest_framework import serializers
from apps.accounts.serializers import UserProfileSerializer
from .models import Post, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'color', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.filter(is_published=True).count()


class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.filter(is_published=True).count()


class PostListSerializer(serializers.ModelSerializer):
    """Compact serializer for post cards/list views."""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cover_url = serializers.ReadOnlyField()
    author_name = serializers.ReadOnlyField()
    author_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'subtitle', 'category',
            'tags', 'cover_url', 'excerpt', 'author_name',
            'author_avatar', 'reading_time', 'views',
            'is_featured', 'published_at',
        ]

    def get_author_avatar(self, obj):
        if obj.author and obj.author.avatar:
            return obj.author.avatar.url
        return None


class PostDetailSerializer(serializers.ModelSerializer):
    """Full serializer for post detail pages."""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserProfileSerializer(read_only=True)
    cover_url = serializers.ReadOnlyField()
    related_posts = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()  # ← keep declaration

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'subtitle', 'author',
            'author_name',                               # ← ADD this line
            'category', 'tags', 'cover_url', 'excerpt', 'body',
            'reading_time', 'views', 'is_featured',
            'allow_comments', 'meta_title', 'meta_description',
            'published_at', 'updated_at', 'related_posts',
        ]

    def get_author_name(self, obj):                     # ← ADD the method body
        if obj.author:
            return obj.author.full_name
        return 'Editorial Team'

    def get_related_posts(self, obj):
        """3 posts from the same category, excluding current."""
        if not obj.category:
            return []
        related = (
            Post.objects
            .filter(category=obj.category, is_published=True)
            .exclude(pk=obj.pk)
            .select_related('author', 'category')[:3]
        )
        return PostListSerializer(related, many=True, context=self.context).data