from datetime import date

import pytest
from rest_framework.test import APIClient

from tests.extras.testutils.factories.analysis import RiskAggregateFactory


@pytest.fixture
def api_client():
    from django.core.cache import cache

    cache.clear()
    return APIClient()


@pytest.mark.django_db
def test_aggregate_list_risk_dashboard(api_client):
    RiskAggregateFactory.create_batch(3)

    response = api_client.get("/api/analysis/daily-aggregates/", {"dashboard": "risk"})

    assert response.status_code == 200
    assert len(response.data) == 3
    assert "module" in response.data[0]
    assert "severity" in response.data[0]
    assert "risk_code" in response.data[0]


@pytest.mark.django_db
def test_aggregate_list_risk_filter_module_and_severity(api_client):
    RiskAggregateFactory(module="payment_operations", severity="critical")
    RiskAggregateFactory(module="registration", severity="normal")

    response = api_client.get(
        "/api/analysis/daily-aggregates/",
        {"dashboard": "risk", "module": "payment_operations", "severity": "critical"},
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["module"] == "payment_operations"
    assert response.data[0]["severity"] == "critical"


@pytest.mark.django_db
def test_aggregate_list_date_range_filter(api_client):
    RiskAggregateFactory(date=date(2024, 1, 1))
    RiskAggregateFactory(date=date(2024, 6, 1))
    RiskAggregateFactory(date=date(2025, 1, 1))

    response = api_client.get(
        "/api/analysis/daily-aggregates/",
        {"dashboard": "risk", "date_from": "2024-01-01", "date_to": "2024-12-31"},
    )

    assert response.status_code == 200
    assert len(response.data) == 2
