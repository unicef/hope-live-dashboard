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
    for i in range(5):
        FinancialAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            country_slug=f"country-{i}",
            dimension_type="sector",
            dimension_value=f"Health-{i}",
            total_usd=10000,
            payment_count=5,
        )


@pytest.fixture
def demographic_aggregates(db):
    year = datetime.datetime.now().year
    for i in range(5):
        DemographicAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            country_slug=f"country-{i}",
            dimension_type="sector",
            dimension_value=f"Education-{i}",
            total_beneficiaries=200,
            total_children=100,
            total_pwd=10,
        )


@pytest.fixture
def completion_aggregates(db):
    year = datetime.datetime.now().year
    for i in range(5):
        CompletionAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            country_slug=f"country-{i}",
            dimension_type="status",
            dimension_value=f"RECONCILED-{i}",
            payment_count=3,
            total_usd=5000,
        )


def test_financial_dashboard_loads(browser, financial_aggregates):
    browser.login_as_user()
    browser.open("/dashboard/")
    browser.wait_for_element_visible("#time-focus-chart")
    browser.wait_for_element_visible("#sector-chart")
    browser.wait_for_element_visible("#country-chart")


def test_demographic_dashboard_loads(browser, demographic_aggregates):
    browser.login_as_user()
    browser.open("/demographic/")
    browser.wait_for_element_visible("#total-individuals")
    browser.wait_for_element_visible("#total-children")


def test_completion_dashboard_loads(browser, completion_aggregates):
    browser.login_as_user()
    browser.open("/completion/")
    browser.wait_for_element_visible("#total-reconciled")
    browser.wait_for_element_visible("#total-opened")


@pytest.fixture
def grievance_aggregates(db):
    year = datetime.datetime.now().year
    for i in range(5):
        GrievanceAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            country_slug="country-test",
            dimension_type="category",
            dimension_value=f"Feedback-{i}",
            ticket_count=10,
        )


@pytest.fixture
def grievance_status_aggregates(db):
    year = datetime.datetime.now().year
    statuses = ["OPEN", "CLOSED", "PENDING", "RESOLVED"]
    for idx, status in enumerate(statuses):
        GrievanceAggregateFactory(
            date=datetime.date(year, 1, idx + 1),
            country_slug="country-test",
            dimension_type="status",
            dimension_value=status,
            ticket_count=5,
        )


def test_grievance_dashboard_loads(browser, grievance_aggregates, grievance_status_aggregates):
    browser.login_as_user()
    browser.open("/grievance/")
    browser.wait_for_element_visible("#total-tickets")
    browser.wait_for_element_visible("#year-tabs")
    browser.wait_for_text_visible("Status")
    browser.wait_for_text_visible("Priority")
    browser.wait_for_text_visible("Category")
    browser.wait_for_text_visible("Issue Type")
    browser.wait_for_text_visible("Country")
    browser.wait_for_text_visible("Region")
    browser.wait_for_text_visible("Admin Level 1")
