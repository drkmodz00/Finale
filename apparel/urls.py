"""
morado_project/urls.py  —  root URL configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Morado POS app — all routes defined in morado/urls.py
    path('', include('dmep.urls')),
]

# ── Serve media files during development ──────────────────────
# In production, your web server (nginx/apache) handles this.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)