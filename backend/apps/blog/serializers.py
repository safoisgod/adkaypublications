from rest_framework import serializers
from apps.accounts.serializers import UserProfileSerializer
from .models import Post, Category, Tag, PostContent


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'color', 'post_count']

    def get_post_count(self, obj):
        try:
            return obj.posts.filter(is_published=True).count()
        except Exception:
            return 0


class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count']

    def get_post_count(self, obj):
        try:
            return obj.posts.filter(is_published=True).count()
        except Exception:
            return 0


class PostListSerializer(serializers.ModelSerializer):
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
        try:
            if obj.author and obj.author.avatar:
                return obj.author.avatar.url
        except Exception:
            return None
        return None


# 🔥 NEW: Content serializer included
class PostContentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PostContent
        fields = [
            'id',
            'content_type',
            'text',
            'image_url',
            'video_url',
            'order',
        ]

    def get_image_url(self, obj):
    # Cloudinary field can be truthy even when empty
        if obj.image and str(obj.image):
            try:
                url = obj.image.url
                if url:
                    return url
            except Exception:
                pass
        if obj.image_url:
            return obj.image_url
        return None


class PostDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserProfileSerializer(read_only=True)

    cover_url = serializers.ReadOnlyField()
    author_name = serializers.SerializerMethodField()

    # 🔥 replaces "body"
    contents = PostContentSerializer(many=True, read_only=True)

    related_posts = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'slug',
            'subtitle',
            'author',
            'author_name',
            'category',
            'tags',
            'cover_url',
            'excerpt',
            'contents',  # ✅ FIXED (replaces body)
            'reading_time',
            'views',
            'is_featured',
            'allow_comments',
            'meta_title',
            'meta_description',
            'published_at',
            'updated_at',
            'related_posts',
        ]

    def get_author_name(self, obj):
        try:
            if obj.author:
                return obj.author.full_name
        except Exception:
            pass
        return 'Editorial Team'

    def get_related_posts(self, obj):
        try:
            if not obj.category:
                return []

            related = (
                Post.objects
                .filter(category=obj.category, is_published=True)
                .exclude(pk=obj.pk)
                .select_related('author', 'category')
                .prefetch_related('contents')[:3]
            )

            return PostListSerializer(
                related,
                many=True,
                context=self.context
            ).data

        except Exception:
            return []