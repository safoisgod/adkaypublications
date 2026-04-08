"""
Serializers for the Authors app.
"""
from rest_framework import serializers
from .models import Author


class AuthorListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views and embedded references."""
    photo_url = serializers.ReadOnlyField()
    book_count = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = [
            'id', 'full_name', 'slug', 'photo_url',
            'role', 'short_bio', 'is_featured', 'book_count',
        ]


class AuthorDetailSerializer(serializers.ModelSerializer):
    """Full serializer for author detail pages."""
    photo_url = serializers.ReadOnlyField()
    book_count = serializers.ReadOnlyField()
    books = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'full_name', 'slug', 'photo_url', 'role',
            'bio', 'short_bio', 'twitter', 'linkedin',
            'instagram', 'website', 'is_featured',
            'display_order', 'book_count', 'books', 'created_at',
        ]

    def get_books(self, obj):
        from apps.books.serializers import BookListSerializer
        books = obj.books.filter(is_published=True).select_related('genre')[:6]
        return BookListSerializer(books, many=True, context=self.context).data
