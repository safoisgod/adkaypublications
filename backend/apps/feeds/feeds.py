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
from django.utils.html import escape

from apps.blog.models import Post


# ─────────────────────────────────────────
# HELPER: Build absolute frontend URL for a post
# ─────────────────────────────────────────
def _post_url(post):
    """
    Returns the absolute URL to the blog detail page on the frontend.

    Frontend route:
        /blog-detail?slug={post.slug}
    """

    frontend_url = getattr(
        settings,
        "FRONTEND_URL",
        "http://localhost:5500"
    ).rstrip("/")

    return f"{frontend_url}/blog-detail?slug={post.slug}"


# ─────────────────────────────────────────
# HELPER: Build item description / body HTML
# ─────────────────────────────────────────
def _build_description(post):
    """
    Constructs an HTML description for RSS feed items.

    Includes:
        1. Cover image
        2. Post excerpt
        3. Reading time
    """

    parts = []

    # 1. Featured image
    cover_url = post.cover_url

    if cover_url:
        parts.append(
            f'<p>'
            f'<a href="{_post_url(post)}">'
            f'<img src="{escape(cover_url)}" '
            f'alt="{escape(post.title)}" '
            f'style="max-width:100%;height:auto;border-radius:4px;" />'
            f'</a>'
            f'</p>'
        )

    # 2. Excerpt fallback
    description_text = (
        post.excerpt.strip()
        if post.excerpt
        else ""
    )

    if not description_text:
        first_text = (
            post.contents
            .filter(content_type="text")
            .first()
        )

        if first_text and first_text.text:
            plain = re.sub(
                r"<[^>]+>",
                " ",
                first_text.text
            )

            description_text = plain.strip()[:500]

    if description_text:
        parts.append(
            f"<p>{escape(description_text)}</p>"
        )

    # 3. Reading time badge
    if post.reading_time:
        parts.append(
            '<p style="font-size:0.85em;color:#666;">'
            f'📖 {post.reading_time} min read'
            '</p>'
        )

    return "".join(parts)


# ─────────────────────────────────────────
# MAIN FEED: Latest Blog Posts
# ─────────────────────────────────────────
class LatestPostsFeed(Feed):

    feed_type = Rss201rev2Feed

    title = f"{settings.SITE_NAME} | Journal"

    link = (
        f"{settings.FRONTEND_URL.rstrip('/')}"
        "/blog"
    )

    description = (
        "Latest articles, insights, and stories from "
        f"{settings.SITE_NAME}. Explore African literature, "
        "publishing tips, author interviews, and more."
    )

    language = "en-us"


    # ─────────────────────────────────────
    # Feed Items
    # ─────────────────────────────────────
    def items(self):

        return (
            Post.objects
            .filter(is_published=True)
            .select_related(
                "author",
                "category"
            )
            .prefetch_related(
                "tags",
                "contents"
            )
            .order_by("-published_at")[:20]
        )


    # ─────────────────────────────────────
    # Item Metadata
    # ─────────────────────────────────────

    def item_title(self, item):
        return item.title


    def item_description(self, item):
        return _build_description(item)


    def item_link(self, item):
        return _post_url(item)


    def item_guid(self, item):
        return _post_url(item)


    def item_pubdate(self, item):

        if item.published_at:

            if timezone.is_naive(item.published_at):

                return timezone.make_aware(
                    item.published_at,
                    timezone=timezone.get_current_timezone()
                )

            return item.published_at

        return item.created_at


    def item_author_name(self, item):

        return item.author_name


    def item_categories(self, item):

        categories = []

        if item.category:
            categories.append(
                item.category.name
            )

        for tag in item.tags.all():
            categories.append(
                tag.name
            )

        return categories


    def item_extra_kwargs(self, item):

        return {}