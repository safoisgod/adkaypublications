"""
RSS 2.0 Feed definitions for A-D Kay Publications.

Uses Django's built-in syndication framework (django.contrib.syndication)
to produce valid RSS 2.0 XML compatible with Mailchimp RSS Campaigns.

Currently provides:
    - LatestPostsFeed: 20 most recent published blog posts.

To add more feeds (e.g. Books), create additional Feed subclasses
and register them in urls.py.
"""
import re

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils import timezone
from django.utils.feedgenerator import Rss201rev2Feed

from apps.blog.models import Post


# ─────────────────────────────────────────
# HELPER: Build absolute frontend URL for a post
# ─────────────────────────────────────────
def _post_url(post):
    """
    Returns the absolute URL to the blog detail page on the frontend.

    The frontend uses blog-detail.html with a ?slug= query parameter,
    so we construct: {FRONTEND_URL}/blog-detail.html?slug={post.slug}
    """
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
    return f"{frontend_url}/blog-detail.html?slug={post.slug}"


# ─────────────────────────────────────────
# HELPER: Build item description / body HTML
# ─────────────────────────────────────────
def _build_description(post):
    """
    Constructs an HTML description for RSS feed items.

    Includes (in order):
      1. Cover image as <img> tag (if available)
      2. Post excerpt or first text content block as fallback
      3. Reading time badge
    """
    parts = []

    # 1. Featured image
    cover_url = post.cover_url
    if cover_url:
        parts.append(
            f'<p><a href="{_post_url(post)}">'
            f'<img src="{cover_url}" alt="{post.title}" '
            f'style="max-width:100%;height:auto;border-radius:4px;" />'
            f'</a></p>'
        )

    # 2. Excerpt or fallback to first text content block
    description_text = post.excerpt.strip() if post.excerpt else ''
    if not description_text:
        # Fallback: grab the first text content block
        first_text = post.contents.filter(content_type='text').first()
        if first_text and first_text.text:
            # Strip HTML tags for a clean excerpt
            plain = re.sub(r'<[^>]+>', ' ', first_text.text)
            description_text = plain.strip()[:500]

    if description_text:
        parts.append(f'<p>{description_text}</p>')

    # 3. Reading time badge
    if post.reading_time:
        parts.append(
            f'<p style="font-size:0.85em;color:#666;">'
            f'📖 {post.reading_time} min read</p>'
        )

    return ''.join(parts)


# ─────────────────────────────────────────
# MAIN FEED: Latest Blog Posts
# ─────────────────────────────────────────
class LatestPostsFeed(Feed):
    """
    RSS 2.0 feed returning the 20 most recent published blog posts.

    URL: /rss/ (or /feed/ as configured in urls.py)
    Compatible with Mailchimp RSS Campaigns.

    Feed-level metadata:
        title          = A-D Kay Publications | Journal
        link           = FRONTEND_URL/blog.html
        description    = Latest articles, insights, and stories from
                         A-D Kay Publications
        language       = en-us
    """
    feed_type = Rss201rev2Feed
    title = f"{settings.SITE_NAME} | Journal"
    link = f"{settings.FRONTEND_URL}/blog.html"
    description = (
        "Latest articles, insights, and stories from "
        f"{settings.SITE_NAME}. Explore African literature, "
        "publishing tips, author interviews, and more."
    )
    language = "en-us"

    # ── Feed Item Queryset ────────────────────
    def items(self):
        """
        Returns the 20 most recent published blog posts.
        Uses select_related and prefetch_related for optimal DB performance.
        """
        return (
            Post.objects
            .filter(is_published=True)
            .select_related('author', 'category')
            .prefetch_related('tags', 'contents')
            .order_by('-published_at')[:20]
        )

    # ── Item Metadata ──────────────────────────

    def item_title(self, item):
        """The post title becomes the RSS <title>."""
        return item.title

    def item_description(self, item):
        """
        The RSS <description> — contains cover image + excerpt in HTML.
        """
        return _build_description(item)

    def item_link(self, item):
        """
        The RSS <link> — points to the frontend blog detail page.
        Each post gets a unique, permanent link.
        """
        return _post_url(item)

    def item_guid(self, item):
        """
        The RSS <guid> — unique, permanent identifier.
        Using the same URL as the link with isPermaLink="true".
        """
        return _post_url(item)

    def item_pubdate(self, item):
        """
        The RSS <pubDate> — post's publication date in RFC 2822 format.
        Falls back to created_at if published_at is not set.
        """
        if item.published_at:
            # Ensure timezone awareness
            if timezone.is_naive(item.published_at):
                return timezone.make_aware(
                    item.published_at,
                    timezone=timezone.get_current_timezone()
                )
            return item.published_at
        return item.created_at

    def item_author_name(self, item):
        """
        The RSS <author> — post author's full name.
        Falls back to 'Editorial Team' if no author is assigned.
        """
        return item.author_name

    def item_categories(self, item):
        """
        The RSS <category> elements.
        Returns a list of plain category name strings.
        Includes both the primary category and all tags.
        """
        categories = []
        if item.category:
            categories.append(item.category.name)
        for tag in item.tags.all():
            categories.append(tag.name)
        return categories

    def item_extra_kwargs(self, item):
        """
        Returns extra keyword arguments for the RSS item XML.

        Currently returns an empty dict. The featured image and
        content are already included in the <description> element
        via item_description(), which is sufficient for Mailchimp
        RSS Campaigns and all standard RSS readers.

        If custom XML namespaces are needed in the future
        (e.g. <media:content>, <content:encoded>), subclass
        Rss201rev2Feed and add the appropriate root_element
        and add_item_elements methods.
        """
        return {}
