from django.urls import path
from .views import (
    BookListView,
    BookFeaturedView,
    BookBestsellerView,
    BookNewReleasesView,
    BookDetailView,
    GenreListView,
)

urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('featured/', BookFeaturedView.as_view(), name='book-featured'),
    path('bestsellers/', BookBestsellerView.as_view(), name='book-bestsellers'),
    path('new-releases/', BookNewReleasesView.as_view(), name='book-new-releases'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
    path('<slug:slug>/', BookDetailView.as_view(), name='book-detail'),
]
