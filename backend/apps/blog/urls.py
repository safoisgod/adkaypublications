from django.urls import path
from .views import (
    PostListView,
    PostFeaturedView,
    PostDetailView,
    PostIncrementViewView,
    CategoryListView,
    TagListView,
)

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/featured/', PostFeaturedView.as_view(), name='post-featured'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<slug:slug>/view/', PostIncrementViewView.as_view(), name='post-increment-view'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('tags/', TagListView.as_view(), name='tag-list'),
]
