import datetime

import pytest

from tests.extras.testutils.factories.analysis import (
    CompletionAggregateFactory,
    DemographicAggregateFactory,
    FinancialAggregateFactory,
    GrievanceAggregateFactory,
)

pytestmark = [pytest.mark.selenium, pytest.mark.django_db]


@pytest.fixture(autouse=True)
def clear_aggregate_api_cache():
    """The aggregates API is `cache_page`-cached in Redis for six hours.

    Each dashboard now loads two aggregate feeds (e.g. the financial page also pulls
    completion data for the pipeline funnel, and completion pulls financial data for the
    quality quadrant). Without clearing, a test would be served a previous test's cached
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
    # Additional dimensions (program, delivery_type, financial_service_provider, beneficiary_group)
    for dim_type, prefix in [
        ("program", "Program"),
        ("delivery_type", "Delivery"),
        ("financial_service_provider", "FSP"),
        ("beneficiary_group", "Group"),
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
    # Beneficiary groups
    for i, country in enumerate(countries[:3]):
        DemographicAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="monthly",
            country_slug=country,
            dimension_type="beneficiary_group",
            dimension_value=f"Group-{i}",
            total_beneficiaries=50,
            total_children=25,
            total_pwd=5,
            total_households=40,
        )
        DemographicAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="monthly",
            country_slug=country,
            dimension_type="beneficiary_group",
            dimension_value=f"Group-{i}",
            total_beneficiaries=100,
            total_children=50,
            total_pwd=10,
            total_households=80,
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
    # Beneficiary groups
    for i, country in enumerate(countries[:3]):
        CompletionAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug=country,
            dimension_type="beneficiary_group",
            dimension_value=f"Group-{i}",
            payment_count=2,
            total_usd=2000,
        )
        CompletionAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug=country,
            dimension_type="beneficiary_group",
            dimension_value=f"Group-{i}",
            payment_count=4,
            total_usd=4000,
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


def _apply_custom_range(browser, start: str, end: str) -> None:
    browser.click('button.time-preset-btn[data-preset="custom"]')
    browser.wait_for_element_visible("#custom-range-inputs")
    browser.execute_script(
        f"document.getElementById('filter-date-from').value = '{start}';"
        f"document.getElementById('filter-date-to').value = '{end}';"
    )
    browser.click("#btn-apply-custom-range")


def test_financial_dashboard_loads(browser, financial_aggregates):
    browser.login_as_user()
    browser.open("/dashboard/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible("#sector-chart canvas")
    browser.wait_for_element_visible("#country-chart canvas")
    browser.wait_for_element_visible("#total-amount-paid")
    browser.wait_for_element_visible("#total-payments")
    browser.wait_for_element_visible("#delivery-chart canvas")
    browser.wait_for_element_visible("#region-chart canvas")
    browser.wait_for_element_visible("#program-chart canvas")
    browser.wait_for_element_visible("#fsp-chart canvas")
    browser.wait_for_element_visible("#beneficiary-group-chart canvas")

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
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible("#beneficiary-group-chart canvas")

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
    browser.wait_for_element_visible("#beneficiary-group-chart canvas")

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
    browser.wait_for_text_visible("Status")
    browser.wait_for_text_visible("Priority")
    browser.wait_for_text_visible("Category")
    browser.wait_for_text_visible("Issue type")
    browser.wait_for_text_visible("Ticket status by country")
    browser.wait_for_element_visible("#grievance-status-chart canvas")
    browser.wait_for_element_visible("#grievance-priority-chart canvas")
    browser.wait_for_element_visible("#grievance-category-chart canvas")
    browser.wait_for_element_visible("#grievance-issue-type-chart canvas")
    browser.wait_for_element_visible("#grievance-country-chart canvas")
    browser.wait_for_element_visible("#time-focus-chart canvas")

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


def test_completion_quality_quadrant_loads(browser, completion_aggregates, financial_aggregates):
    browser.login_as_user()
    browser.open("/completion/")
    browser.wait_for_element_visible("#time-filter-container")
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible("#quality-quadrant-chart canvas")
