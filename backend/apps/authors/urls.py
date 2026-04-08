from django.urls import path
from .views import AuthorListView, AuthorFeaturedView, AuthorDetailView

urlpatterns = [
    path('', AuthorListView.as_view(), name='author-list'),
    path('featured/', AuthorFeaturedView.as_view(), name='author-featured'),
    path('<slug:slug>/', AuthorDetailView.as_view(), name='author-detail'),
]
