import datetime
import re

import pytest

from tests.extras.testutils.factories.analysis import (
    CompletionAggregateFactory,
    DemographicAggregateFactory,
    FinancialAggregateFactory,
    GrievanceAggregateFactory,
    RiskAggregateFactory,
)

pytestmark = [pytest.mark.selenium, pytest.mark.django_db]


@pytest.fixture(autouse=True)
def clear_aggregate_api_cache():
    """The aggregates API is `cache_page`-cached in Redis for six hours.

    Each dashboard now loads two aggregate feeds (e.g. the financial page also pulls
    completion data for the pipeline funnel, and completion pulls financial data for the
    delivery success rates). Without clearing, a test would be served a previous test's cached
    payload — including empty payloads cached when that test had no rows for the feed.
    """
    from django.core.cache import cache

    cache.clear()


@pytest.fixture
def financial_aggregates(db):
    year = datetime.datetime.now().year
    countries = ["kenya", "somalia", "nigeria", "ukraine", "bangladesh"]
    # Current year sector
    for i, country in enumerate(countries):
        FinancialAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug=country,
            dimension_type="sector",
            dimension_value=f"Health-{i}",
            total_usd=10000,
            payment_count=5,
        )
    # Previous year sector
    for i, country in enumerate(countries):
        FinancialAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug=country,
            dimension_type="sector",
            dimension_value=f"Health-{i}",
            total_usd=20000,
            payment_count=10,
        )
    # Additional dimensions (program, delivery_type, financial_service_provider)
    for dim_type, prefix in [
        ("program", "Program"),
        ("delivery_type", "Delivery"),
        ("financial_service_provider", "FSP"),
    ]:
        for i, country in enumerate(countries[:3]):
            FinancialAggregateFactory(
                date=datetime.date(year, 1, i + 1),
                time_grain="daily",
                country_slug=country,
                dimension_type=dim_type,
                dimension_value=f"{prefix}-{i}",
                total_usd=5000,
                payment_count=2,
            )
            FinancialAggregateFactory(
                date=datetime.date(year - 1, 1, i + 1),
                time_grain="daily",
                country_slug=country,
                dimension_type=dim_type,
                dimension_value=f"{prefix}-{i}",
                total_usd=5000,
                payment_count=2,
            )


@pytest.fixture
def demographic_aggregates(db):
    year = datetime.datetime.now().year
    countries = ["kenya", "somalia", "nigeria", "ukraine", "bangladesh"]
    # Current year
    for i, country in enumerate(countries):
        DemographicAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="monthly",
            country_slug=country,
            dimension_type="sector",
            dimension_value=f"Education-{i}",
            total_beneficiaries=200,
            total_children=100,
            total_pwd=10,
            total_households=150,
        )
    # Region dimension used by the Region Share chart.
    for i, country in enumerate(countries):
        DemographicAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="monthly",
            country_slug=country,
            dimension_type="region",
            dimension_value=["MENAR", "ESAR", "WCAR", "ECAR", "SAR"][i],
            total_beneficiaries=200,
            total_children=100,
            total_pwd=10,
            total_households=150,
        )
    # Previous year
    for i, country in enumerate(countries):
        DemographicAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="monthly",
            country_slug=country,
            dimension_type="sector",
            dimension_value=f"Education-{i}",
            total_beneficiaries=400,
            total_children=200,
            total_pwd=20,
            total_households=300,
        )


@pytest.fixture
def completion_aggregates(db):
    year = datetime.datetime.now().year
    countries = ["kenya", "somalia", "nigeria", "ukraine", "bangladesh"]
    # Current year
    for i, country in enumerate(countries):
        CompletionAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug=country,
            dimension_type="status",
            dimension_value=f"RECONCILED-{i}",
            payment_count=3,
            total_usd=5000,
        )
    # Previous year
    for i, country in enumerate(countries):
        CompletionAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug=country,
            dimension_type="status",
            dimension_value=f"RECONCILED-{i}",
            payment_count=6,
            total_usd=10000,
        )


@pytest.fixture
def grievance_aggregates(db):
    year = datetime.datetime.now().year
    # Current year category
    for i in range(5):
        GrievanceAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="category",
            dimension_value=f"Feedback-{i}",
            ticket_count=10,
        )
    # Previous year category
    for i in range(5):
        GrievanceAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="category",
            dimension_value=f"Feedback-{i}",
            ticket_count=20,
        )
    # Priority
    for i in range(3):
        GrievanceAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="priority",
            dimension_value=f"Priority-{i}",
            ticket_count=5,
        )
        GrievanceAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="priority",
            dimension_value=f"Priority-{i}",
            ticket_count=10,
        )
    # Issue Type
    for i in range(3):
        GrievanceAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="issue_type",
            dimension_value=f"Issue-{i}",
            ticket_count=5,
        )
        GrievanceAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="issue_type",
            dimension_value=f"Issue-{i}",
            ticket_count=10,
        )


@pytest.fixture
def grievance_status_aggregates(db):
    year = datetime.datetime.now().year
    statuses = ["OPEN", "CLOSED", "PENDING", "RESOLVED"]
    for idx, status in enumerate(statuses):
        GrievanceAggregateFactory(
            date=datetime.date(year, 1, idx + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="status",
            dimension_value=status,
            ticket_count=5,
        )
        # Previous year status aggregates
        GrievanceAggregateFactory(
            date=datetime.date(year - 1, 1, idx + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="status",
            dimension_value=status,
            ticket_count=10,
        )


@pytest.fixture
def social_worker_aggregates(db):
    """Social-worker cohort rows, kept separate so standard-programme totals stay unchanged."""
    year = datetime.datetime.now().year
    for i in range(2):
        FinancialAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug="kenya",
            dimension_type="sector",
            dimension_value=f"Protection-{i}",
            total_usd=1000,
            payment_count=7,
            program_type="SOCIAL",
        )
    for i in range(2):
        FinancialAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug="kenya",
            dimension_type="status",
            dimension_value="DISTRIBUTION SUCCESSFUL",
            total_usd=1000,
            payment_count=7,
            program_type="SOCIAL",
        )


@pytest.fixture
def risk_aggregates(db):
    """Two countries x two programmes, with predictable issue totals."""
    year = datetime.datetime.now().year
    rows = [
        ("kenya", "Child Protection - THABAT", "Targeting", "critical", 10),
        ("kenya", "Education THABAT", "Payment Operations", "warning", 5),
        ("somalia", "Child Protection - THABAT", "Targeting", "critical", 7),
        ("somalia", "Education THABAT", "Payment Operations", "warning", 3),
    ]
    for index, (country, programme, module, severity, issues) in enumerate(rows):
        RiskAggregateFactory(
            date=datetime.date(year, 1, index + 1),
            time_grain="daily",
            country_slug=country,
            dimension_type="risk_code",
            dimension_value=f"CODE_{index}",
            risk_code=f"CODE_{index}",
            risk_name=f"Risk {index}",
            module=module,
            program_name=programme,
            category="operational",
            issue_count=issues,
            severity=severity,
            trend="up",
            unit_label="payments",
            percentage=None,
        )


@pytest.fixture
def risk_shared_code(db):
    """The same risk code in two countries with different programme/severity/%."""
    year = datetime.datetime.now().year
    rows = [
        ("kenya", "Kenya Programme", "critical", 10, 80),
        ("somalia", "Somalia Programme", "warning", 7, 10),
    ]
    for index, (country, programme, severity, issues, percentage) in enumerate(rows):
        RiskAggregateFactory(
            date=datetime.date(year, 1, index + 1),
            time_grain="daily",
            country_slug=country,
            dimension_type="risk_code",
            dimension_value="MISSING_ID_DOCUMENTS",
            risk_code="MISSING_ID_DOCUMENTS",
            risk_name="Missing ID Documents",
            module="Registration",
            program_name=programme,
            category="operational",
            issue_count=issues,
            severity=severity,
            trend="up",
            unit_label="% of individuals",
            percentage=percentage,
        )


def _apply_custom_range(browser, start: str, end: str) -> None:
    browser.click('button.time-preset-btn[data-preset="custom"]')
    browser.wait_for_element_visible("#custom-range-inputs")
    browser.execute_script(
        f"document.getElementById('filter-date-from').value = '{start}';"
        f"document.getElementById('filter-date-to').value = '{end}';"
    )
    browser.click("#btn-apply-custom-range")


def test_landing_kpis_have_definitions_and_exact_date(browser, financial_aggregates):
    browser.login_as_user()
    browser.open("/")
    browser.wait_for_element_visible("#latest-data-date")

    latest = browser.get_text("#latest-data-date")
    assert re.search(r"\d{2} [A-Z][a-z]{2} \d{4}", latest), latest

    for key in (
        "children",
        "households",
        "individuals",
        "active_countries",
        "assistance",
        "reconciled",
        "social_workers",
    ):
        browser.wait_for_element_visible(f'[data-chart-info="landing.{key}"]')

    browser.click('[data-chart-info="landing.children"] summary')
    browser.wait_for_text_visible("Children reached through household programmes")


def test_country_filter_is_available_on_dashboards(  # noqa: PLR0917
    browser,
    financial_aggregates,
    demographic_aggregates,
    completion_aggregates,
    grievance_aggregates,
    grievance_status_aggregates,
):
    browser.login_as_user()

    expected = {
        "/dashboard/": "kenya",
        "/demographic/": "kenya",
        "/completion/": "kenya",
        "/grievance/": "country-test",
    }
    for path, country in expected.items():
        browser.open(path)
        browser.wait_for_element_visible("#country-filter")
        browser.wait_for_element_visible(f"#country-filter option[value='{country}']")

    browser.open("/dashboard/")
    browser.wait_for_element_visible("#country-filter option[value='kenya']")
    browser.select_option_by_value("#country-filter", "kenya")
    browser.assert_text("5", "#total-payments")

    # The country filter survives navigation to another dashboard.
    browser.open("/demographic/")
    browser.wait_for_element_visible("#country-filter option[value='kenya']")
    assert browser.get_value("#country-filter") == "kenya"

    # The period preset is persisted too.
    browser.click('button.time-preset-btn[data-preset="this_month"]')
    browser.open("/completion/")
    browser.wait_for_element_visible('button.time-preset-btn[data-preset="this_month"].active-preset')


def test_financial_dashboard_loads(browser, financial_aggregates):
    browser.login_as_user()
    browser.open("/dashboard/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible("#sector-chart canvas")
    browser.wait_for_element_visible("#country-chart canvas")
    browser.wait_for_element_visible("#outstanding-country-chart canvas")
    browser.wait_for_element_visible("#total-amount-paid")
    browser.wait_for_element_visible("#total-payments")
    browser.wait_for_element_visible("#delivery-chart canvas")
    browser.wait_for_element_visible("#region-chart canvas")
    browser.wait_for_element_visible("#program-chart canvas")
    browser.wait_for_element_visible("#fsp-chart canvas")

    browser.assert_text("Cash disbursed by sector", "#sector-title")
    browser.assert_text("Cash disbursed by delivery type", "#delivery-title")
    browser.assert_text("Cash disbursed by region", "#region-title")
    browser.assert_text("Cash disbursed (paid) by country", "#country-title")
    browser.assert_text("Cash disbursed by programme", "#program-title")
    browser.assert_text("Cash disbursed by financial service provider (FSP)", "#fsp-title")

    browser.wait_for_element_visible('[data-chart-info="financial.timeline"]')
    browser.wait_for_element_visible('[data-chart-info="financial.program"]')
    browser.click('[data-chart-info="financial.program"] summary')
    browser.wait_for_text_visible("top 10 programmes")

    # Month axes show a short year (Nov 25), while tooltips keep the full date.
    axis_label = browser.execute_script(
        "const o = echarts.getInstanceByDom(document.getElementById('time-focus-chart')).getOption();"
        "return o.xAxis[0].axisLabel.formatter(new Date(2025, 10, 1).getTime());"
    )
    assert axis_label == "Nov 25"

    # The header shows the latest aggregate date once the data is loaded.
    assert browser.get_text("#data-as-of") != "—"

    # Assert current year totals (default "This Year" preset)
    browser.assert_text("25", "#total-payments")

    # Apply a custom period covering the previous year
    prev_year = datetime.datetime.now().year - 1
    _apply_custom_range(browser, f"{prev_year}-01-01", f"{prev_year}-12-31")

    # Wait and assert updated previous year totals
    browser.wait_for_text_visible("50", "#total-payments")


def test_demographic_dashboard_loads(browser, demographic_aggregates, financial_aggregates):
    browser.login_as_user()
    browser.open("/demographic/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#total-individuals")
    browser.wait_for_element_visible("#total-children")
    browser.wait_for_element_visible("#total-households")
    browser.wait_for_element_visible("#total-pwd")
    browser.wait_for_element_visible("#sector-children-chart canvas")
    browser.wait_for_element_visible("#country-pwd-chart canvas")
    browser.wait_for_element_visible("#region-share-chart canvas")
    browser.wait_for_element_visible("#demographic-country-show-all")
    browser.wait_for_element_visible("#time-focus-chart canvas")

    browser.assert_text("Children reached", "#card-children h3")
    browser.assert_text("Persons with disabilities reached", "#card-pwd h3")
    browser.assert_text("Region share of reached population", "#region-share-title")

    region_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('region-share-chart')).getOption();"
    )
    assert len(region_option["series"][0]["data"]) == 5

    country_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('country-pwd-chart')).getOption();"
    )
    assert country_option["series"][0]["type"] == "bar"
    assert len(country_option["series"][0]["data"]) == 5

    browser.wait_for_element_visible('[data-chart-info="demographic.timeline"]')
    browser.wait_for_element_visible('[data-chart-info="demographic.country"]')
    browser.wait_for_text_visible("Method and caveats")
    browser.click("//summary[contains(., 'Method and caveats')]")
    browser.wait_for_text_visible("Qualifying payments must belong to accepted, finished or closed payment plans")

    # Assert current year totals
    browser.assert_text("1,000", "#total-individuals")
    browser.assert_text("500", "#total-children")
    browser.assert_text("750", "#total-households")
    browser.assert_text("50", "#total-pwd")

    # Apply a custom period covering the previous year
    prev_year = datetime.datetime.now().year - 1
    _apply_custom_range(browser, f"{prev_year}-01-01", f"{prev_year}-12-31")

    # Wait and assert updated previous year totals
    browser.wait_for_text_visible("2,000", "#total-individuals")
    browser.wait_for_text_visible("1,000", "#total-children")
    browser.wait_for_text_visible("1,500", "#total-households")
    browser.wait_for_text_visible("100", "#total-pwd")


def test_completion_dashboard_loads(browser, completion_aggregates, financial_aggregates):
    browser.login_as_user()
    browser.open("/completion/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#total-reconciled")
    browser.wait_for_element_visible("#total-opened")
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible("#status-country-chart canvas")
    browser.wait_for_element_visible("#completion-gauge canvas")

    browser.assert_text("Pending Reconciliation", "#opened-card-title")
    browser.assert_text("Payment reconciliation dashboard", "h1")

    browser.wait_for_element_visible('[data-chart-info="completion.timeline"]')
    browser.wait_for_element_visible('[data-chart-info="completion.rates"]')

    # Country chart: absolute default, 100% share toggle flips the axis to percentages.
    browser.assert_element_not_visible("#verification-card")
    browser.click("#country-view-share")
    share_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('status-country-chart')).getOption();"
    )
    assert share_option["yAxis"][0]["max"] == 100
    assert share_option["series"][0].get("stack") == "total"
    browser.click("#country-view-absolute")
    absolute_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('status-country-chart')).getOption();"
    )
    assert absolute_option["series"][0].get("stack") in (None, "")

    # Assert current year totals
    browser.assert_text("15 (100.0% out of 15 total)", "#total-reconciled")
    # Apply a custom period covering the previous year
    prev_year = datetime.datetime.now().year - 1
    _apply_custom_range(browser, f"{prev_year}-01-01", f"{prev_year}-12-31")

    # Wait and assert updated previous year totals
    browser.wait_for_text_visible("30 (100.0% out of 30 total)", "#total-reconciled")


def test_grievance_dashboard_loads(browser, grievance_aggregates, grievance_status_aggregates, financial_aggregates):
    browser.login_as_user()
    browser.open("/grievance/")
    browser.wait_for_element_visible("#total-tickets")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_text_visible("Tickets by status")
    browser.wait_for_text_visible("Tickets by priority")
    browser.wait_for_text_visible("Tickets by category")
    browser.wait_for_text_visible("Tickets by subcategory")
    browser.wait_for_text_visible("Tickets by status and country")
    browser.wait_for_element_visible('[data-chart-info="grievance.timeline"]')
    browser.wait_for_element_visible('[data-chart-info="grievance.subcategory"]')
    browser.wait_for_element_visible("#grievance-status-chart canvas")
    browser.wait_for_element_visible("#grievance-priority-chart canvas")
    browser.wait_for_element_visible("#grievance-category-chart canvas")
    browser.wait_for_element_visible("#grievance-issue-type-chart canvas")
    browser.wait_for_element_visible("#grievance-country-chart canvas")
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible('.grievance-show-all[data-chart="category"]')
    browser.wait_for_element_visible('.grievance-show-all[data-chart="issue-type"]')
    browser.wait_for_element_visible("#status-count-new")
    browser.wait_for_element_visible("#status-count-closed")

    # Key-status figures reconcile with the status doughnut (fixture: 5 CLOSED +
    # 5 RESOLVED in the current year).
    browser.wait_for_text_visible("10 (20.0%)", "#status-count-closed")
    browser.wait_for_text_visible("Open & Active covers")
    browser.wait_for_text_visible("Priority is an optional field")

    # Category and subcategory bars show count and share, not only the count.
    for chart_id in ("grievance-category-chart", "grievance-issue-type-chart"):
        label = browser.execute_script(
            f"const o = echarts.getInstanceByDom(document.getElementById('{chart_id}')).getOption();"
            "return o.series[0].label.formatter({value: 10});"
        )
        assert re.search(r"\(\d+\.\d%\)", label), label

    country_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('grievance-country-chart')).getOption();"
    )
    assert country_option["series"][0].get("stack") in (None, "")
    country_label = browser.execute_script(
        "const o = echarts.getInstanceByDom(document.getElementById('grievance-country-chart')).getOption();"
        "return o.series[0].label.formatter({dataIndex: 0, value: 5});"
    )
    assert "%" in country_label

    # Assert current year totals
    browser.assert_text("50", "#total-tickets")

    # Apply a custom period covering the previous year
    prev_year = datetime.datetime.now().year - 1
    _apply_custom_range(browser, f"{prev_year}-01-01", f"{prev_year}-12-31")

    # Wait and assert updated previous year totals
    browser.wait_for_text_visible("100", "#total-tickets")


def test_financial_dashboard_cohort_toggle_and_pipeline(browser, financial_aggregates, social_worker_aggregates):
    browser.login_as_user()
    browser.open("/dashboard/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#total-payments")
    browser.wait_for_element_visible("#pipeline-funnel-chart canvas")

    # All cohorts: standard (25) plus social-worker (14) sector rows
    browser.wait_for_text_visible("39", "#total-payments")

    # Social-worker cohort narrows the totals (and the pipeline funnel follows it)
    browser.click('.cohort-tab[data-cohort="SOCIAL"]')
    browser.wait_for_text_visible("14", "#total-payments")

    # Back to all cohorts
    browser.click('.cohort-tab[data-cohort="ALL"]')
    browser.wait_for_text_visible("39", "#total-payments")


def test_demographic_dashboard_cohort_toggle(browser, demographic_aggregates, financial_aggregates):
    browser.login_as_user()
    browser.open("/demographic/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#total-individuals")

    # Social-worker programmes do not collect household-level demographics
    browser.click('.cohort-tab[data-cohort="SOCIAL"]')
    browser.assert_element_not_visible("#card-households")
    browser.assert_element_not_visible("#card-children")
    browser.assert_element_not_visible("#card-pwd")
    browser.assert_text("Workers", "#btn-individuals")
    browser.assert_text("Workers reached", "#individuals-card-title")

    browser.click('.cohort-tab[data-cohort="ALL"]')
    browser.assert_element_visible("#card-households")
    browser.assert_element_visible("#card-children")
    browser.assert_element_visible("#card-pwd")
    browser.assert_text("Individuals", "#btn-individuals")
    browser.assert_text("Individuals reached", "#individuals-card-title")


def test_completion_rates_chart_loads(browser, completion_aggregates, financial_aggregates):
    year = datetime.datetime.now().year
    # Delivery-status rows so the chart has both feeds for the same countries.
    for i, country in enumerate(["kenya", "somalia", "nigeria", "ukraine", "bangladesh"]):
        for status, count in [("DISTRIBUTION SUCCESSFUL", 80 + i), ("PENDING", 20 - i)]:
            FinancialAggregateFactory(
                date=datetime.date(year, 1, i + 1),
                time_grain="daily",
                country_slug=country,
                dimension_type="status",
                dimension_value=status,
                total_usd=1000 * count,
                payment_count=count,
            )

    browser.login_as_user()
    browser.open("/completion/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible("#completion-rates-chart canvas")

    rates_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('completion-rates-chart')).getOption();"
    )
    assert [s["type"] for s in rates_option["series"]] == ["bar", "bar"]
    assert rates_option["xAxis"][0]["max"] == 100


def test_completion_verification_panel(browser, completion_aggregates, financial_aggregates):
    year = datetime.datetime.now().year
    for i, (value, count) in enumerate([("SELECTED", 100), ("VERIFIED", 92), ("PENDING", 5), ("DISCREPANCIES", 3)]):
        CompletionAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug="kenya",
            dimension_type="verification",
            dimension_value=value,
            payment_count=count,
            total_usd=count * 100,
        )

    browser.login_as_user()
    browser.open("/completion/")
    browser.wait_for_element_visible("#verification-card")
    browser.assert_text("100", "#verification-selected")
    browser.assert_text("92", "#verification-verified")
    browser.assert_text("5", "#verification-pending")
    browser.assert_text("3", "#verification-discrepancies")
    browser.assert_text("92.0%", "#verification-rate")


def test_program_and_country_charts_show_top_ten_with_other(browser, db):
    """The dashboard must show the top 10 categories plus an Other bucket."""
    year = datetime.datetime.now().year
    for i in range(12):
        FinancialAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug=f"country-{i}",
            dimension_type="sector",
            dimension_value=f"Sector {i}",
            total_usd=1000 + i,
            payment_count=1,
        )
        FinancialAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug=f"country-{i}",
            dimension_type="program",
            dimension_value=f"Programme {i}",
            total_usd=1000 + i,
            payment_count=1,
        )

    browser.login_as_user()
    browser.open("/dashboard/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#total-payments")
    browser.wait_for_element_visible("#program-chart canvas")
    browser.wait_for_element_visible("#country-chart canvas")

    program_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('program-chart')).getOption();"
    )
    program_names = [item["name"] for item in program_option["series"][0]["data"]]
    assert len(program_names) == 11, program_names
    assert "Other" in program_names, program_names

    country_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('country-chart')).getOption();"
    )
    country_names = [item["name"] for item in country_option["series"][0]["data"]]
    assert len(country_names) == 11, country_names
    assert "Other" in country_names, country_names

    # Expanding a chart replaces the Other bucket with every underlying category.
    browser.click('.show-all-toggle[data-chart="program"]')
    browser.wait_for_text_visible("Show top 10", '.show-all-toggle[data-chart="program"]')
    program_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('program-chart')).getOption();"
    )
    program_names = [item["name"] for item in program_option["series"][0]["data"]]
    assert len(program_names) == 12, program_names
    assert "Other" not in program_names, program_names

    browser.click('.show-all-toggle[data-chart="program"]')
    browser.wait_for_text_visible("Show all", '.show-all-toggle[data-chart="program"]')
    program_option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('program-chart')).getOption();"
    )
    assert len(program_option["series"][0]["data"]) == 11


def test_risk_filters_are_searchable(browser, risk_aggregates):
    browser.login_as_user()
    browser.open("/risk/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_text_visible("25", "#total-issues")

    # Programme combobox: search, then select the match
    browser.click("#program-filter-input")
    browser.type("#program-filter-input", "Child")
    browser.wait_for_element_visible('#program-filter-list [role="option"]')
    browser.assert_text("Child Protection - THABAT", '#program-filter-list [role="option"]')
    browser.click('#program-filter-list [role="option"]')
    assert browser.get_value("#program-filter-input") == "Child Protection - THABAT"
    browser.wait_for_text_visible("17", "#total-issues")

    # Country combobox: search, then select the match
    browser.click("#country-filter-input")
    browser.type("#country-filter-input", "Kenya")
    browser.wait_for_element_visible('#country-filter-list [role="option"]')
    browser.click('#country-filter-list [role="option"]')
    assert browser.get_value("#country-filter-input") == "Kenya"
    browser.wait_for_text_visible("10", "#total-issues")

    # Clearing the programme leaves the country filter active
    browser.click("#program-filter-clear")
    browser.wait_for_text_visible("15", "#total-issues")
    assert browser.get_value("#program-filter-input") == ""


def test_risk_table_uses_the_filtered_country(browser, risk_shared_code):
    """The table must not keep another country's programme/severity/percentage."""
    browser.login_as_user()
    browser.open("/risk/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_text_visible("17", "#total-issues")

    browser.click("#country-filter-input")
    browser.type("#country-filter-input", "Somalia")
    browser.wait_for_element_visible('#country-filter-list [role="option"]')
    browser.click('#country-filter-list [role="option"]')
    browser.wait_for_text_visible("7", "#total-issues")

    table = browser.get_text("#risk-top-table")
    assert "Somalia" in table
    assert "Somalia Programme" in table
    assert "Warning" in table
    assert "10%" in table

    assert "Kenya Programme" not in table
    assert "Critical" not in table
    assert "80%" not in table


def test_grievance_resolution_and_source_filter(browser, grievance_aggregates, grievance_status_aggregates):
    year = datetime.datetime.now().year
    GrievanceAggregateFactory(
        date=datetime.date(year, 1, 1),
        time_grain="daily",
        country_slug="country-test",
        dimension_type="resolution",
        dimension_value="1",
        ticket_count=10,
        avg_resolution_days=3.5,
        ticket_source="GRIEVANCE",
    )
    GrievanceAggregateFactory(
        date=datetime.date(year, 1, 1),
        time_grain="daily",
        country_slug="country-test",
        dimension_type="category",
        dimension_value="9",
        ticket_count=100,
        ticket_source="SYSTEM_FLAG",
    )

    browser.login_as_user()
    browser.open("/grievance/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#resolution-card")
    browser.assert_element_not_visible("#status-card")
    browser.assert_text("50", "#total-tickets")

    option = browser.execute_script(
        "return echarts.getInstanceByDom(document.getElementById('grievance-resolution-chart')).getOption();"
    )
    assert option["series"][0]["type"] == "bar"

    browser.click("#source-all")
    browser.wait_for_text_visible("150", "#total-tickets")
