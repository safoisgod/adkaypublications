"""
URL configuration for the feeds app.

Maps RSS feed views to clean, user-friendly URLs.

Available feeds:
    /rss/  → LatestPostsFeed (20 most recent blog posts)
"""
from django.urls import path
from .feeds import LatestPostsFeed

urlpatterns = [
    path('rss/', LatestPostsFeed(), name='rss-feed'),
]