import pytest
from rest_framework.test import APIClient

from hope_live.analysis.models import FinancialAggregate, ProgramType
from hope_live.analysis.tasks import _normalise_program_type, save_aggregates
from tests.extras.testutils.factories.analysis import FinancialAggregateFactory

FINANCIAL_UPDATE_FIELDS = ["total_usd", "total_qty", "payment_count"]


def _payment_row(**overrides):
    row = {
        "date": "2024-01-01",
        "time_grain": "daily",
        "country_slug": "kenya",
        "dimension_type": "sector",
        "dimension_value": "health",
        "total_usd": 100,
        "total_qty": 10,
        "payment_count": 5,
    }
    row.update(overrides)
    return row


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("SOCIAL", ProgramType.SOCIAL),
        ("social", ProgramType.SOCIAL),
        ("SOCIAL_WORKER", ProgramType.SOCIAL),
        ("Social Workers", ProgramType.SOCIAL),
        ("HOUSEHOLD", ProgramType.STANDARD),
        ("STANDARD", ProgramType.STANDARD),
        ("standard", ProgramType.STANDARD),
        (None, ProgramType.STANDARD),
        ("", ProgramType.STANDARD),
        ("unexpected-value", ProgramType.STANDARD),
    ],
)
def test_normalise_program_type(raw, expected):
    assert _normalise_program_type(raw) == expected


@pytest.mark.django_db
def test_save_aggregates_defaults_program_type_to_standard():
    save_aggregates([_payment_row()], 2024, "FinancialAggregate", FINANCIAL_UPDATE_FIELDS)

    agg = FinancialAggregate.objects.get()
    assert agg.program_type == ProgramType.STANDARD


@pytest.mark.django_db
def test_save_aggregates_keeps_both_cohorts_for_the_same_key():
    """The two cohorts share every other key, so they must not collapse into one row."""
    rows = [
        _payment_row(program_type="STANDARD", total_usd=100),
        _payment_row(program_type="SOCIAL", total_usd=250),
    ]
    save_aggregates(rows, 2024, "FinancialAggregate", FINANCIAL_UPDATE_FIELDS)

    assert FinancialAggregate.objects.count() == 2
    assert FinancialAggregate.objects.get(program_type=ProgramType.STANDARD).total_usd == 100
    assert FinancialAggregate.objects.get(program_type=ProgramType.SOCIAL).total_usd == 250


@pytest.mark.django_db
def test_save_aggregates_normalises_cohort_aliases():
    rows = [
        _payment_row(program_type="SOCIAL_WORKER"),
        _payment_row(program_type="HOUSEHOLD"),
    ]
    save_aggregates(rows, 2024, "FinancialAggregate", FINANCIAL_UPDATE_FIELDS)

    assert FinancialAggregate.objects.filter(program_type=ProgramType.SOCIAL).count() == 1
    assert FinancialAggregate.objects.filter(program_type=ProgramType.STANDARD).count() == 1


@pytest.fixture
def api_client():
    from django.core.cache import cache

    cache.clear()
    return APIClient()


@pytest.mark.django_db
def test_aggregate_api_exposes_program_type(api_client):
    FinancialAggregateFactory(dimension_type="sector", program_type=ProgramType.SOCIAL)

    response = api_client.get(
        "/api/analysis/daily-aggregates/",
        {"dashboard": "financial", "dimension_type": "sector"},
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["program_type"] == ProgramType.SOCIAL


@pytest.mark.django_db
def test_aggregate_api_filters_by_program_type(api_client):
    FinancialAggregateFactory(dimension_type="sector", dimension_value="health", program_type=ProgramType.STANDARD)
    FinancialAggregateFactory(dimension_type="sector", dimension_value="health", program_type=ProgramType.SOCIAL)

    response = api_client.get(
        "/api/analysis/daily-aggregates/",
        {"dashboard": "financial", "dimension_type": "sector", "program_type": "social"},
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["program_type"] == ProgramType.SOCIAL
