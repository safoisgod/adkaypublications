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

from apps.core.utils import frontend_base
from django.contrib.sitemaps import Sitemap

from apps.books.models import Book
from apps.blog.models import Post


# ─────────────────────────────────────────
# CANONICAL SITEMAP BASE
# ─────────────────────────────────────────
class CanonicalSitemap(Sitemap):
    """
    Sitemap base that always emits the canonical frontend origin
    (https://adkaypublications.com) in front of every location.

    Django's Sitemap._urls() prepends '{protocol}://{domain}' to every
    location() result UNCONDITIONALLY, so location() must return a
    RELATIVE path. protocol/domain are derived from frontend_base() here
    so the generated URLs always use exactly one canonical origin.
    """

    def get_protocol(self, protocol=None):
        base = frontend_base()
        return base.split("://", 1)[0] or "https"

    def get_domain(self, site=None):
        base = frontend_base()
        if "://" in base:
            return base.split("://", 1)[1]
        return "adkaypublications.com"


# ─────────────────────────────────────────
# HELPER: Build relative frontend path
# ─────────────────────────────────────────
def _frontend_url(path: str, query: dict | None = None) -> str:
    """
    Returns a RELATIVE canonical path for the frontend (e.g. '/about' or
    '/book-detail?slug=x'). The absolute http(s)://host prefix is supplied
    by CanonicalSitemap.get_protocol/get_domain — never returned here —
    so Django cannot double-prefix an already-absolute URL.
    """
    url = f"/{path.lstrip('/')}" if path else "/"
    if query:
        url = f"{url}?{urlencode(query)}"
    return url


# ─────────────────────────────────────────
# 1. STATIC PAGES
# ─────────────────────────────────────────
class StaticViewSitemap(CanonicalSitemap):
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
class BookSitemap(CanonicalSitemap):
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
class PostSitemap(CanonicalSitemap):
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