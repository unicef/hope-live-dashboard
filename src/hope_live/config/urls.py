import debug_toolbar
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # 2. API endpoints (grouped together)
    path("api/analysis/", include("hope_live.analysis.api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # 3. Admin and management URLs
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path(r"adminactions/", include("adminactions.urls")),
    # 4. Authentication and security URLs
    path(r"social/", include("social_django.urls", namespace="social")),
    path("security/", include(("unicef_security.urls", "unicef_security"))),
    # 5. Other app URLs
    path("ws/", include("hope_live.ws.urls", namespace="ws")),
    path("issues/", include("issues.urls")),
    # 6. Debug/development URLs (always last)
    path(r"__debug__/", include(debug_toolbar.urls)),
]

urlpatterns += i18n_patterns(
    # 1. Main application URLs
    path("", include("hope_live.web.urls", namespace="web")),
    prefix_default_language=False,
)

if settings.DEBUG and "django_browser_reload.middleware.BrowserReloadMiddleware" in settings.MIDDLEWARE:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
