from django import template

from hope_live.web.chart_metadata import CHART_GUIDANCE, CHART_INFO

register = template.Library()


def _entry(key: str) -> dict[str, str]:
    """Return chart metadata merged with its formula/how-to-read guidance."""
    meta = dict(CHART_INFO.get(key, {}))
    meta.update(CHART_GUIDANCE.get(key, {}))
    return meta


@register.inclusion_tag("includes/chart_info.html")
def chart_info(key: str) -> dict[str, str]:
    """Render the definition/source/method panel for one chart."""
    meta = _entry(key)
    return {
        "chart_key": key,
        "definition": meta.get("definition", ""),
        "source": meta.get("source", ""),
        "method": meta.get("method", ""),
        "formula": meta.get("formula", ""),
        "how_to_read": meta.get("how_to_read", ""),
        "note": meta.get("note", ""),
    }


@register.inclusion_tag("includes/methodology_panel.html")
def methodology_panel(section: str) -> dict[str, object]:
    """Render the page-level methodology button and drawer for one dashboard."""
    keys = [key for key in CHART_INFO if key.startswith(f"{section}.")]
    keys.sort(key=lambda key: (0 if ".kpi_" in key else 1, list(CHART_INFO).index(key)))
    return {
        "section": section,
        "entries": [{"key": key, "meta": _entry(key)} for key in keys],
    }
