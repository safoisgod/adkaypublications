"""
XML Sitemap definitions for A-D Kay Publications.

Uses Django's built-in django.contrib.sitemaps framework to generate
valid Sitemap Protocol XML for all public content.

Sitemaps defined:
    - StaticViewSitemap  → Static frontend pages (home, about, blog list, books list, services, team)
    - BookSitemap        → Individual book detail pages
    - PostSitemap        → Individual blog post detail pages

REMOVED vs. the original file (see audit notes):
    - AuthorSitemap  — every author resolved to the same '/team' URL, so this
      generated N duplicate sitemap entries for one physical page. '/team'
      is already covered once by StaticViewSitemap.
    - ServiceSitemap — used a mismatched path ('service' singular, the real
      page is '/services') and emitted '#svc-{slug}' fragment URLs. Google
      strips URL fragments before indexing, so these fragment URLs collapse
      to the same canonical page and would still count as duplicates even if
      the path were corrected. '/services' is already covered once by
      StaticViewSitemap.

    If/when services or authors get real, unique detail pages (their own
    path, not an anchor on a shared page), add a sitemap class back for them
    at that point — pointing at the real path, not a fragment.
"""

from urllib.parse import urlencode

from django.conf import settings
from django.contrib.sitemaps import Sitemap

from apps.books.models import Book
from apps.blog.models import Post


# ─────────────────────────────────────────
# HELPER: Build absolute frontend URL
# ─────────────────────────────────────────
def _frontend_url(path: str, query: dict | None = None) -> str:
    """
    Returns an absolute, canonical URL pointing to the frontend.

    Uses FRONTEND_URL from settings (must be the canonical
    'https://adkaypublications.com' — no trailing slash, no www, no scheme
    other than https). Ensures no double slashes, normalizes the path, and
    safely URL-encodes any query parameters instead of interpolating them
    directly into the string.
    """
    base = getattr(settings, 'FRONTEND_URL', 'https://adkaypublications.com')
    base = base.rstrip('/')
    path = f"/{path.lstrip('/')}" if path else "/"
    url = f"{base}{path}"
    if query:
        url = f"{url}?{urlencode(query)}"
    return url


# ─────────────────────────────────────────
# 1. STATIC PAGES
# ─────────────────────────────────────────
class StaticViewSitemap(Sitemap):
    """
    Sitemap for static, non-database-driven frontend pages.
    """
    changefreq = 'monthly'

    # Each entry: (path, priority, changefreq)
    pages = [
        ('',          1.0, 'weekly'),   # Homepage — must resolve to '/', not '/index'
        ('about',     0.8, 'monthly'),
        ('blog',      0.7, 'weekly'),
        ('books',     0.7, 'weekly'),
        ('services',  0.8, 'monthly'),
        ('team',      0.6, 'monthly'),
    ]

    def items(self):
        return self.pages

    def location(self, item):
        return _frontend_url(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]

    def lastmod(self, item):
        return None


# ─────────────────────────────────────────
# 2. BOOKS
# ─────────────────────────────────────────
class BookSitemap(Sitemap):
    """
    Sitemap for published books.

    URLs point to the frontend book-detail page with a slug query parameter.
    """
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return (
            Book.objects
            .filter(is_published=True)
            .only('slug', 'updated_at', 'title')
        )

    def location(self, item):
        return _frontend_url('book-detail', {'slug': item.slug})

    def lastmod(self, item):
        return item.updated_at


# ─────────────────────────────────────────
# 3. BLOG POSTS
# ─────────────────────────────────────────
class PostSitemap(Sitemap):
    """
    Sitemap for published blog posts.

    URLs point to the frontend blog-detail page with a slug query parameter.
    """
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return (
            Post.objects
            .filter(is_published=True)
            .only('slug', 'updated_at', 'title')
        )

    def location(self, item):
        return _frontend_url('blog-detail', {'slug': item.slug})

    def lastmod(self, item):
        return item.updated_at


# ─────────────────────────────────────────
# SITEMAP INDEX DICTIONARY
# ─────────────────────────────────────────
sitemaps = {
    'static': StaticViewSitemap,
    'books':  BookSitemap,
    'posts':  PostSitemap,
}