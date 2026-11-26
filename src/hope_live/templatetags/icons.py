from django import template
from django.utils.html import format_html

from .icon_names import ICON_NAMES

register = template.Library()


@register.simple_tag
def icon(name: str, classes: str = "") -> str:
    """Render one symbol from the inline icon sprite.

    Icons are decorative by default. Icon-only interactive elements must carry
    their accessible name on the button/link, not on the SVG.
    """
    if name not in ICON_NAMES:
        raise ValueError(f"Unknown icon: {name}")
    return format_html(
        '<svg class="{}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true" focusable="false">'
        '<use href="#icon-{}"></use></svg>',
        classes,
        name,
    )
