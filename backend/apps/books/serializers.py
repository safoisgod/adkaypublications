"""
Serializers for the Books app.
"""
from rest_framework import serializers
from apps.authors.serializers import AuthorListSerializer
from .models import Book, Genre


class GenreSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug', 'description', 'book_count']

    def get_book_count(self, obj):
        return obj.books.filter(is_published=True).count()


class BookListSerializer(serializers.ModelSerializer):
    """
    Compact serializer for list/card views.
    Includes minimal author info and cover URL.
    """
    authors = AuthorListSerializer(many=True, read_only=True)
    genre = GenreSerializer(read_only=True)
    cover_url = serializers.ReadOnlyField()
    author_names = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'slug', 'subtitle', 'authors',
            'author_names', 'genre', 'cover_url', 'excerpt',
            'published_date', 'price', 'is_featured',
            'is_bestseller', 'is_new_release', 'language',
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for the book detail page.
    Includes complete author info, all fields, and related books.
    """
    authors = AuthorListSerializer(many=True, read_only=True)
    genre = GenreSerializer(read_only=True)
    cover_url = serializers.ReadOnlyField()
    author_names = serializers.ReadOnlyField()
    related_books = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'slug', 'subtitle', 'authors',
            'author_names', 'genre', 'cover_url', 'description',
            'excerpt', 'isbn', 'publisher', 'published_date',
            'pages', 'language', 'edition', 'price', 'buy_link',
            'is_featured', 'is_bestseller', 'is_new_release',
            'meta_title', 'meta_description',
            'related_books', 'created_at',
        ]

    def get_related_books(self, obj):
        """
        Returns up to 4 books from the same genre,
        excluding the current book.
        """
        if not obj.genre:
            return []
        related = (
            Book.objects
            .filter(genre=obj.genre, is_published=True)
            .exclude(pk=obj.pk)
            .select_related('genre')
            .prefetch_related('authors')[:4]
        )
        return BookListSerializer(related, many=True, context=self.context).data
