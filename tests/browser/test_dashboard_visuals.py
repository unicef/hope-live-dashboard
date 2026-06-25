import datetime

import pytest

from tests.extras.testutils.factories.analysis import (
    CompletionAggregateFactory,
    DemographicAggregateFactory,
    FinancialAggregateFactory,
    GrievanceAggregateFactory,
)

pytestmark = [pytest.mark.selenium, pytest.mark.django_db]


@pytest.fixture
def financial_aggregates(db):
    year = datetime.datetime.now().year
    # Current year
    for i in range(5):
        FinancialAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug=f"country-{i}",
            dimension_type="sector",
            dimension_value=f"Health-{i}",
            total_usd=10000,
            payment_count=5,
        )
    # Previous year
    for i in range(5):
        FinancialAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug=f"country-{i}",
            dimension_type="sector",
            dimension_value=f"Health-{i}",
            total_usd=20000,
            payment_count=10,
        )


@pytest.fixture
def demographic_aggregates(db):
    year = datetime.datetime.now().year
    # Current year
    for i in range(5):
        DemographicAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug=f"country-{i}",
            dimension_type="sector",
            dimension_value=f"Education-{i}",
            total_beneficiaries=200,
            total_children=100,
            total_pwd=10,
            total_households=150,
        )
    # Previous year
    for i in range(5):
        DemographicAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug=f"country-{i}",
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
    # Current year
    for i in range(5):
        CompletionAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug=f"country-{i}",
            dimension_type="status",
            dimension_value=f"RECONCILED-{i}",
            payment_count=3,
            total_usd=5000,
        )
    # Previous year
    for i in range(5):
        CompletionAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug=f"country-{i}",
            dimension_type="status",
            dimension_value=f"RECONCILED-{i}",
            payment_count=6,
            total_usd=10000,
        )


@pytest.fixture
def grievance_aggregates(db):
    year = datetime.datetime.now().year
    # Current year
    for i in range(5):
        GrievanceAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="category",
            dimension_value=f"Feedback-{i}",
            ticket_count=10,
        )
    # Previous year
    for i in range(5):
        GrievanceAggregateFactory(
            date=datetime.date(year - 1, 1, i + 1),
            time_grain="daily",
            country_slug="country-test",
            dimension_type="category",
            dimension_value=f"Feedback-{i}",
            ticket_count=20,
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


def test_financial_dashboard_loads(browser, financial_aggregates):
    browser.login_as_user()
    browser.open("/dashboard/")
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible("#sector-chart canvas")
    browser.wait_for_element_visible("#country-chart canvas")
    browser.wait_for_element_visible("#total-amount-paid")
    browser.wait_for_element_visible("#total-payments")
    browser.wait_for_element_visible("#delivery-chart canvas")
    browser.wait_for_element_visible("#region-chart canvas")
    browser.wait_for_element_visible("#program-chart canvas")
    browser.wait_for_element_visible("#fsp-chart canvas")
    browser.wait_for_element_visible("#total-qty-distributed")

    # Assert current year totals (for loops will default to current year first)
    browser.assert_text("25", "#total-payments")

    # Click the previous year tab
    prev_year = datetime.datetime.now().year - 1
    browser.click(f'button.year-tab[data-year="{prev_year}"]')

    # Wait and assert updated previous year totals
    browser.wait_for_text_visible("50", "#total-payments")


def test_demographic_dashboard_loads(browser, demographic_aggregates, financial_aggregates):
    browser.login_as_user()
    browser.open("/demographic/")
    browser.wait_for_element_visible("#total-individuals")
    browser.wait_for_element_visible("#total-children")
    browser.wait_for_element_visible("#total-households")
    browser.wait_for_element_visible("#total-pwd")
    browser.wait_for_element_visible("#sector-individuals-chart canvas")
    browser.wait_for_element_visible("#sector-children-chart canvas")
    browser.wait_for_element_visible("#country-individuals-chart canvas")
    browser.wait_for_element_visible("#country-pwd-chart canvas")
    browser.wait_for_element_visible("#time-focus-chart canvas")

    # Assert current year totals
    browser.assert_text("1,000", "#total-individuals")
    browser.assert_text("500", "#total-children")
    browser.assert_text("750", "#total-households")
    browser.assert_text("50", "#total-pwd")

    # Click the previous year tab
    prev_year = datetime.datetime.now().year - 1
    browser.click(f'button.year-tab[data-year="{prev_year}"]')

    # Wait and assert updated previous year totals
    browser.wait_for_text_visible("2,000", "#total-individuals")
    browser.wait_for_text_visible("1,000", "#total-children")
    browser.wait_for_text_visible("1,500", "#total-households")
    browser.wait_for_text_visible("100", "#total-pwd")


def test_completion_dashboard_loads(browser, completion_aggregates, financial_aggregates):
    browser.login_as_user()
    browser.open("/completion/")
    browser.wait_for_element_visible("#total-reconciled")
    browser.wait_for_element_visible("#total-opened")
    browser.wait_for_element_visible("#time-focus-chart canvas")
    browser.wait_for_element_visible("#status-country-chart canvas")
    browser.wait_for_element_visible("#completion-gauge canvas")

    # Assert current year totals
    browser.assert_text("15 (100.0% out of 15 total)", "#total-reconciled")

    # Click the previous year tab
    prev_year = datetime.datetime.now().year - 1
    browser.click(f'button.year-tab[data-year="{prev_year}"]')

    # Wait and assert updated previous year totals
    browser.wait_for_text_visible("30 (100.0% out of 30 total)", "#total-reconciled")


def test_grievance_dashboard_loads(browser, grievance_aggregates, grievance_status_aggregates, financial_aggregates):
    browser.login_as_user()
    browser.open("/grievance/")
    browser.wait_for_element_visible("#total-tickets")
    browser.wait_for_element_visible("#year-tabs")
    browser.wait_for_text_visible("Status")
    browser.wait_for_text_visible("Priority")
    browser.wait_for_text_visible("Category")
    browser.wait_for_text_visible("Issue Type")
    browser.wait_for_text_visible("Ticket Status by Country")
    browser.wait_for_element_visible("#grievance-status-chart canvas")
    browser.wait_for_element_visible("#grievance-priority-chart canvas")
    browser.wait_for_element_visible("#grievance-category-chart canvas")
    browser.wait_for_element_visible("#grievance-issue-type-chart canvas")
    browser.wait_for_element_visible("#grievance-country-chart canvas")
    browser.wait_for_element_visible("#time-focus-chart canvas")

    # Assert current year totals
    browser.assert_text("50", "#total-tickets")

    # Click the previous year tab
    prev_year = datetime.datetime.now().year - 1
    browser.click(f'button.year-tab[data-year="{prev_year}"]')

    # Wait and assert updated previous year totals
    browser.wait_for_text_visible("100", "#total-tickets")
