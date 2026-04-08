"""
Root URL configuration for A-D Kay Publications.
API is versioned under /api/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from apps.core.health import health_check

# ─────────────────────────────────────────
# ADMIN CUSTOMIZATION
# ─────────────────────────────────────────
admin.site.site_header = 'A-D Kay Publications Admin'
admin.site.site_title = 'A-D Kay Publications'
admin.site.index_title = 'Content Management'

# ─────────────────────────────────────────
# API URL PATTERNS
# ─────────────────────────────────────────
api_patterns = [
    path('auth/', include('apps.accounts.urls')),
    path('books/', include('apps.books.urls')),
    path('blog/', include('apps.blog.urls')),
    path('authors/', include('apps.authors.urls')),
    path('services/', include('apps.services.urls')),
    path('contact/', include('apps.contact.urls')),
    path('newsletter/', include('apps.newsletter.urls')),
    path('search/', include('apps.search.urls')),
    path('homepage/', include('apps.core.homepage_urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API
    path('api/', include(api_patterns)),

    # Health check
    path('health/', health_check, name='health-check'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# ─────────────────────────────────────────
# DEVELOPMENT: serve media files
# ─────────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
