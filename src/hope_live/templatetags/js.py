from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def static_js(path: str) -> str:
    """Return the static URL for a JavaScript file.

    In production (``DEBUG=False``) the minified build is served; in development
    the unminified source is served so edits take effect without a rebuild.
    """
    if not settings.DEBUG and path.endswith(".js") and not path.endswith(".min.js"):
        path = f"{path[:-3]}.min.js"
    return static(path)
