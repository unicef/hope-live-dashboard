import re
from pathlib import Path

from django.template import Context, Template

from hope_live.web.chart_metadata import CHART_GUIDANCE, CHART_INFO

PAGES = Path(__file__).parents[2] / "src" / "hope_live" / "templates" / "pages"


def _template_keys() -> set[str]:
    keys: set[str] = set()
    for name in (
        "dashboard.html",
        "demographic.html",
        "completion.html",
        "grievance.html",
        "risk.html",
        "landing.html",
    ):
        text = (PAGES / name).read_text(encoding="utf-8")
        keys.update(re.findall(r'{%\s*chart_info\s+"([^"]+)"', text))
    return keys


def test_every_chart_in_the_templates_has_metadata() -> None:
    # Extra definitions are allowed: landing metadata is retained even though the
    # public page no longer exposes chart-info explanations.
    assert _template_keys() <= set(CHART_INFO)


def test_every_chart_has_definition_source_and_method() -> None:
    for key, meta in CHART_INFO.items():
        assert meta.get("definition"), key
        assert meta.get("source"), key
        assert meta.get("method"), key


def test_chart_info_tag_renders_methodology_and_note_only() -> None:
    rendered = Template('{% load chart_info %}{% chart_info "financial.program" %}').render(Context())

    assert 'data-chart-info="financial.program"' in rendered
    assert "Methodology:" in rendered
    assert "top 10 programmes" in rendered
    assert "Note:" in rendered
    assert "Formula:" not in rendered
    assert "Source:" not in rendered
    assert "How to read:" not in rendered
    assert "Cash disbursed or payments by programme." not in rendered


def test_unknown_chart_key_renders_an_empty_panel() -> None:
    rendered = Template('{% load chart_info %}{% chart_info "missing.key" %}').render(Context())

    assert 'data-chart-info="missing.key"' in rendered


def test_every_internal_metric_has_formula_and_how_to_read() -> None:
    internal_prefixes = ("financial.", "demographic.", "completion.", "grievance.", "risk.")
    internal_keys = [key for key in CHART_INFO if key.startswith(internal_prefixes)]

    assert internal_keys
    for key in internal_keys:
        meta = CHART_INFO[key]
        guidance = CHART_GUIDANCE.get(key, {})
        assert meta.get("definition"), key
        assert guidance.get("formula"), key
        assert guidance.get("how_to_read"), key


def test_dashboards_no_longer_use_the_page_level_methodology_panel() -> None:
    for name in ("dashboard.html", "demographic.html", "completion.html", "grievance.html", "risk.html"):
        text = (PAGES / name).read_text(encoding="utf-8")
        assert "methodology_panel" not in text, name


def test_methodology_matches_the_delivered_and_children_rules() -> None:
    financial = str(CHART_INFO["financial.timeline"]["method"])
    children = str(CHART_INFO["demographic.children"]["method"])
    grievance = str(CHART_INFO["grievance.payee_type"]["method"])

    assert "delivered quantity only" in financial
    assert "entitlement is not used for paid amounts" in financial
    assert "TFR" in children
    assert "household_size - 1" in children
    assert "UNSPECIFIED" in grievance


def test_country_chart_notes_describe_the_top_ten_and_other_bucket() -> None:
    for key in (
        "financial.country",
        "financial.outstanding_country",
        "demographic.country",
        "completion.country",
        "completion.rates",
        "grievance.country",
    ):
        note = str(CHART_INFO[key]["note"])
        assert "Top 10 countries" in note, key
