from django import template

from hope_live.web.chart_metadata import CHART_INFO

register = template.Library()


@register.inclusion_tag("includes/chart_info.html")
def chart_info(key: str) -> dict[str, str]:
    """Render the methodology and note for one chart."""
    meta = CHART_INFO.get(key, {})
    return {
        "chart_key": key,
        "method": meta.get("method", ""),
        "note": meta.get("note", ""),
    }
