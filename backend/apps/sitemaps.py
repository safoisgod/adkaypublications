"""
XML Sitemap definitions for A-D Kay Publications.

Uses Django's built-in django.contrib.sitemaps framework to generate
valid Sitemap Protocol XML for all public content.

Sitemaps defined:
    - StaticViewSitemap  → Static frontend pages (home, about, blog list, books list, services, team)
    - BookSitemap        → Individual book detail pages
    - PostSitemap        → Individual blog post detail pages
    - ServiceSitemap     → Individual service sections (anchored on services page)

IMPORTANT: All location() methods return RELATIVE paths (e.g. '/books.html').
Django's sitemap framework automatically prepends the protocol and domain
from the request, so returning full absolute URLs would cause double URLs.
"""

from django.contrib.sitemaps import Sitemap

from apps.books.models import Book
from apps.blog.models import Post
from apps.authors.models import Author
from apps.services.models import Service


# ─────────────────────────────────────────
# 1. STATIC PAGES
# ─────────────────────────────────────────
class StaticViewSitemap(Sitemap):
    """
    Sitemap for static, non-database-driven frontend pages.

    These pages are served directly by nginx as static HTML files.
    """
    priority = 0.8
    changefreq = 'monthly'

    # Each entry: (path, priority, changefreq)
    pages = [
        ('',                       1.0, 'weekly'),       # Homepage
        ('about.html',             0.8, 'monthly'),       # About page
        ('blog.html',              0.7, 'weekly'),        # Blog listing
        ('books.html',             0.7, 'weekly'),        # Books listing
        ('services.html',          0.8, 'monthly'),       # Services listing
        ('team.html',              0.6, 'monthly'),       # Team listing
    ]

    def items(self):
        """Returns list of page tuples (path, priority, changefreq)."""
        return self.pages

    def location(self, item):
        """Returns the relative path for the given page."""
        return f"/{item[0]}"

    def priority(self, item):
        """Returns the priority for the given page."""
        return item[1]

    def changefreq(self, item):
        """Returns the change frequency for the given page."""
        return item[2]

    def lastmod(self, item):
        """
        Static pages don't have a dynamic lastmod.
        Returns None to omit the <lastmod> element.
        """
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
        """
        Returns all published books.
        Uses .only() to defer unused fields for optimal performance.
        """
        return (
            Book.objects
            .filter(is_published=True)
            .only('slug', 'updated_at', 'title')
        )

    def location(self, item):
        """Generates relative path: /book-detail?slug={slug}"""
        return f"/book-detail?slug={item.slug}"

    def lastmod(self, item):
        """Uses updated_at as the last modification date."""
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
        """
        Returns all published blog posts.
        """
        return (
            Post.objects
            .filter(is_published=True)
            .only('slug', 'updated_at', 'title')
        )

    def location(self, item):
        """Generates relative path: /blog-detail?slug={slug}"""
        return f"/blog-detail?slug={item.slug}"

    def lastmod(self, item):
        """Uses updated_at as the last modification date."""
        return item.updated_at


# ─────────────────────────────────────────
# 4. AUTHORS (Team Members)
# ─────────────────────────────────────────
class AuthorSitemap(Sitemap):
    """
    Sitemap for active authors/team members.

    Authors do not have individual detail pages; they link to the team listing.
    Priority is lower than static pages since they share a single page.
    """
    priority = 0.4
    changefreq = 'monthly'

    def items(self):
        """
        Returns all active authors.
        """
        return (
            Author.objects
            .filter(is_active=True)
            .only('slug', 'updated_at', 'full_name')
        )

    def location(self, item):
        """
        All authors link to the team page.
        Since there's no individual author detail page, they all point
        to the team listing.
        """
        return '/team.html'

    def lastmod(self, item):
        """Uses updated_at as the last modification date."""
        return item.updated_at


# ─────────────────────────────────────────
# 5. SERVICES
# ─────────────────────────────────────────
class ServiceSitemap(Sitemap):
    """
    Sitemap for active services.

    Each service is a section on the services.html page, identified by
    an anchor ID like #svc-{slug}.

    Google recommends using hash URLs for single-page sections.
    """
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        """
        Returns all active services.
        """
        return (
            Service.objects
            .filter(is_active=True)
            .only('slug', 'updated_at', 'title')
        )

    def location(self, item):
        """
        Generates relative path: /services.html#svc-{slug}

        HTML anchors are valid in sitemaps and are indexed by Google.
        """
        return f"/services.html#svc-{item.slug}"

    def lastmod(self, item):
        """Uses updated_at as the last modification date."""
        return item.updated_at


# ─────────────────────────────────────────
# SITEMAP INDEX DICTIONARY
# ─────────────────────────────────────────
sitemaps = {
    'static':     StaticViewSitemap,
    'books':      BookSitemap,
    'posts':      PostSitemap,
    'authors':    AuthorSitemap,
    'services':   ServiceSitemap,
}