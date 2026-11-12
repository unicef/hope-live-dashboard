from django import template

from hope_live.web.chart_metadata import CHART_INFO

register = template.Library()


@register.inclusion_tag("includes/chart_info.html")
def chart_info(key: str) -> dict[str, str]:
    """Render the definition/source/method panel for one chart."""
    meta = CHART_INFO.get(key, {})
    return {
        "chart_key": key,
        "definition": meta.get("definition", ""),
        "source": meta.get("source", ""),
        "method": meta.get("method", ""),
        "note": meta.get("note", ""),
    }
