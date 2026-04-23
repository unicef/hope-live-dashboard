import datetime

import pytest

pytestmark = [pytest.mark.selenium, pytest.mark.django_db]


@pytest.fixture
def financial_aggregates(db):
    from testutils.factories.analysis import DailyAggregateFactory

    year = datetime.datetime.now().year
    for i in range(5):
        DailyAggregateFactory(
            date=datetime.date(year, 1, i + 1),
            country_slug=f"country-{i}",
            dimension_type="sector",
            dimension_value=f"Health-{i}",
            total_usd=10000,
            payment_count=5,
        )


@pytest.fixture
def demographic_aggregates(db):
    from testutils.factories.analysis import DailyAggregateFactory

    year = datetime.datetime.now().year
    for i in range(5):
        DailyAggregateFactory(
            date=datetime.date(year, 6, i + 1),
            country_slug=f"country-{i}",
            dimension_type="sector",
            dimension_value=f"Education-{i}",
            total_beneficiaries=200,
            total_children=100,
            total_pwd=10,
        )


@pytest.fixture
def completion_aggregates(db):
    from testutils.factories.analysis import DailyAggregateFactory

    year = datetime.datetime.now().year
    for i in range(5):
        DailyAggregateFactory(
            date=datetime.date(year, 9, i + 1),
            country_slug=f"country-{i}",
            dimension_type="status",
            dimension_value=f"RECONCILED-{i}",
            payment_count=3,
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
    browser.wait_for_element_visible("#sector-individuals-chart")
    browser.wait_for_element_visible("#country-individuals-chart")


def test_completion_dashboard_loads(browser, completion_aggregates):
    browser.login_as_user()
    browser.open("/completion/")
    browser.wait_for_element_visible("#reconciliation-pie-chart")
    browser.wait_for_element_visible("#status-country-chart")


def test_live_overview_dashboard_loads(browser):
    browser.login_as_user()
    browser.open("/dashboard/")
    browser.click('a[href*="/live/"]')
    browser.assert_url_contains("/live/")
