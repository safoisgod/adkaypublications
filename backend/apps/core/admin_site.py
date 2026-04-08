"""
Custom Django Admin Site with branded dashboard and stats.
Register this in apps/core/apps.py and config/urls.py.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta


class PublishingAdminSite(admin.AdminSite):
    """
    Custom admin site with Publishing House branding
    and a stats dashboard on the index page.
    """
    site_header = format_html(
        '<span style="font-family:Georgia,serif;letter-spacing:2px;">'
        '📚 PUBLISHING HOUSE</span>'
    )
    site_title = 'Publishing House CMS'
    index_title = 'Content Management Dashboard'

    def index(self, request, extra_context=None):
        """Inject dashboard stats into admin index."""
        extra_context = extra_context or {}

        try:
            from apps.books.models import Book
            from apps.blog.models import Post
            from apps.authors.models import Author
            from apps.newsletter.models import Subscriber
            from apps.contact.models import ContactMessage

            now = timezone.now()
            thirty_days_ago = now - timedelta(days=30)

            extra_context['dashboard_stats'] = {
                'books': {
                    'total': Book.objects.count(),
                    'published': Book.objects.filter(is_published=True).count(),
                    'new_this_month': Book.objects.filter(created_at__gte=thirty_days_ago).count(),
                },
                'posts': {
                    'total': Post.objects.count(),
                    'published': Post.objects.filter(is_published=True).count(),
                    'new_this_month': Post.objects.filter(created_at__gte=thirty_days_ago).count(),
                    'total_views': Post.objects.aggregate(Sum('views'))['views__sum'] or 0,
                },
                'authors': {
                    'total': Author.objects.count(),
                    'active': Author.objects.filter(is_active=True).count(),
                    'featured': Author.objects.filter(is_featured=True).count(),
                },
                'newsletter': {
                    'total': Subscriber.objects.count(),
                    'active': Subscriber.objects.filter(is_active=True).count(),
                    'new_this_month': Subscriber.objects.filter(
                        created_at__gte=thirty_days_ago
                    ).count(),
                },
                'messages': {
                    'total': ContactMessage.objects.count(),
                    'unread': ContactMessage.objects.filter(is_read=False).count(),
                    'unreplied': ContactMessage.objects.filter(is_replied=False).count(),
                },
            }
        except Exception:
            # Gracefully degrade if models aren't migrated yet
            extra_context['dashboard_stats'] = {}

        return super().index(request, extra_context)
