import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("hope_live.web.urls", namespace="web")),
    path("admin/", admin.site.urls),
    path(r"social/", include("social_django.urls", namespace="social")),
    path(r"adminactions/", include("adminactions.urls")),
    path("issues/", include("issues.urls")),
    path("ws/", include("hope_live.ws.urls", namespace="ws")),
    path(r"__debug__/", include(debug_toolbar.urls)),
]

if settings.DEBUG and "django_browser_reload.middleware.BrowserReloadMiddleware" in settings.MIDDLEWARE:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
