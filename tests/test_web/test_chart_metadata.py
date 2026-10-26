import re
from pathlib import Path

from django.template import Context, Template

from hope_live.web.chart_metadata import CHART_INFO

PAGES = Path(__file__).parents[2] / "src" / "hope_live" / "templates" / "pages"


def _template_keys() -> set[str]:
    keys: set[str] = set()
    for name in ("dashboard.html", "demographic.html", "completion.html", "grievance.html"):
        text = (PAGES / name).read_text(encoding="utf-8")
        keys.update(re.findall(r'{%\s*chart_info\s+"([^"]+)"', text))
    return keys


def test_every_chart_in_the_templates_has_metadata() -> None:
    assert _template_keys() == set(CHART_INFO)


def test_every_chart_has_definition_source_and_method() -> None:
    for key, meta in CHART_INFO.items():
        assert meta.get("definition"), key
        assert meta.get("source"), key
        assert meta.get("method"), key


def test_chart_info_tag_renders_metadata() -> None:
    rendered = Template('{% load chart_info %}{% chart_info "financial.program" %}').render(Context())

    assert 'data-chart-info="financial.program"' in rendered
    assert "top 10 programmes" in rendered
    assert "country report financial feed" in rendered


def test_unknown_chart_key_renders_an_empty_panel() -> None:
    rendered = Template('{% load chart_info %}{% chart_info "missing.key" %}').render(Context())

    assert 'data-chart-info="missing.key"' in rendered
