from unittest.mock import patch

import pytest
import responses
from constance import config

from hope_live.analysis.models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
    RiskAggregate,
    RiskSeverity,
    RiskTrend,
)
from hope_live.analysis.tasks import (
    _find_dataset_id_for_year,
    clear_daily_aggregates,
    save_aggregates,
    sync_daily_aggregates,
)
from tests.extras.testutils.factories.analysis import (
    CompletionAggregateFactory,
    DemographicAggregateFactory,
    FinancialAggregateFactory,
    GrievanceAggregateFactory,
    RiskAggregateFactory,
)


@pytest.mark.django_db
def test_save_aggregates_basic():
    rows = [
        {
            "date": "2023-01-01",
            "time_grain": "daily",
            "country_slug": "test",
            "dimension_type": "sector",
            "dimension_value": "health",
            "total_usd": 100,
            "total_qty": 10,
            "payment_count": 5,
            "total_beneficiaries": 50,
            "total_children": 20,
            "total_pwd": 5,
        },
        {
            "country_slug": "missing_date",  # Should be skipped
        },
    ]
    save_aggregates(rows, 2023, "FinancialAggregate", ["total_usd", "total_qty", "payment_count"])
    assert FinancialAggregate.objects.count() == 1


@pytest.mark.django_db
def test_save_aggregates_batching():
    rows = [
        {
            "date": "2023-01-01",
            "time_grain": "daily",
            "country_slug": f"country_{i}",
            "dimension_type": "sector",
            "dimension_value": "health",
        }
        for i in range(1005)
    ]
    with patch("hope_live.analysis.tasks.BATCH_SIZE", 1000):
        save_aggregates(rows, 2023, "FinancialAggregate", ["total_usd"])
    assert FinancialAggregate.objects.count() == 1005


def test_find_dataset_id_for_year():
    datasets = [{"id": 1, "arguments": {"year": 2023}}, {"id": 2, "arguments": {"year": 2024}}]
    assert _find_dataset_id_for_year(datasets, 2023) == 1
    assert _find_dataset_id_for_year(datasets, 2025) is None


@pytest.mark.django_db
def test_sync_daily_aggregates_e2e_success(mocked_responses):
    """Test the full sync process end-to-end using mocked HTTP responses."""
    api_url = config.HOPE_COUNTRY_REPORT_API_URL
    query_id = config.HOPE_COUNTRY_REPORT_QUERY_ID

    # 1. Mock the dataset list endpoint
    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset",
        json={"results": [{"id": 1, "arguments": {"year": 2023}}]},
        status=200,
    )

    # 2. Mock the paginated data endpoint (Page 1)
    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset/1/data/?page_size=1000",
        json={
            "results": [
                {
                    "date": "2023-01-01",
                    "time_grain": "daily",
                    "country_slug": "test",
                    "dimension_type": "sector",
                    "dimension_value": "health",
                    "total_usd": 100,
                }
            ],
            "next": f"{api_url}queries/{query_id}/dataset/1/data/?page=2",
        },
        status=200,
    )

    # 3. Mock the paginated data endpoint (Page 2)
    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset/1/data/?page=2",
        json={
            "results": [
                {
                    "date": "2023-01-02",
                    "time_grain": "daily",
                    "country_slug": "test",
                    "dimension_type": "sector",
                    "dimension_value": "health",
                    "total_usd": 200,
                }
            ],
            "next": None,
        },
        status=200,
    )

    # Execute the actual function
    with patch.object(sync_daily_aggregates, "update_state") as mock_update_state:
        result = sync_daily_aggregates(target_years=[2023])

    # Verify the database was populated correctly (FinancialAggregate is the default model)
    assert FinancialAggregate.objects.count() == 2
    assert FinancialAggregate.objects.filter(date="2023-01-01").exists()
    assert FinancialAggregate.objects.filter(date="2023-01-02").exists()
    assert "Successfully synced 2 rows" in result
    mock_update_state.assert_called_once()


@pytest.mark.django_db
def test_sync_daily_aggregates_extracts_years(mocked_responses):
    """Test that target years are extracted from datasets if not provided."""
    api_url = config.HOPE_COUNTRY_REPORT_API_URL
    query_id = config.HOPE_COUNTRY_REPORT_QUERY_ID

    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset",
        json={"results": [{"id": 1, "arguments": {"year": 2024}}]},
        status=200,
    )
    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset/1/data/?page_size=1000",
        json={
            "data": [
                {
                    "date": "2024-01-01",
                    "time_grain": "daily",
                    "country_slug": "test",
                    "dimension_type": "sector",
                    "dimension_value": "health",
                }
            ]
        },
        status=200,
    )

    # Execute without passing target_years
    with patch.object(sync_daily_aggregates, "update_state"):
        result = sync_daily_aggregates()

    assert FinancialAggregate.objects.count() == 1
    assert "Successfully synced 1 rows" in result


@pytest.mark.django_db
def test_sync_daily_aggregates_api_failure(mocked_responses):
    """Test graceful handling when the API returns an error."""
    api_url = config.HOPE_COUNTRY_REPORT_API_URL
    query_id = config.HOPE_COUNTRY_REPORT_QUERY_ID

    mocked_responses.add(responses.GET, f"{api_url}queries/{query_id}/dataset", status=500)

    with patch.object(sync_daily_aggregates, "update_state"):
        result = sync_daily_aggregates(target_years=[2023])

    assert FinancialAggregate.objects.count() == 0
    assert result == "Successfully synced 0 rows."


@pytest.mark.django_db
def test_sync_daily_aggregates_no_data_for_year(mocked_responses):
    """Test when a dataset exists but returns no rows."""
    api_url = config.HOPE_COUNTRY_REPORT_API_URL
    query_id = config.HOPE_COUNTRY_REPORT_QUERY_ID

    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset",
        json={"results": [{"id": 1, "arguments": {"year": 2023}}]},
        status=200,
    )
    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset/1/data/?page_size=1000",
        json={"results": []},
        status=200,
    )

    with patch.object(sync_daily_aggregates, "update_state"):
        result = sync_daily_aggregates(target_years=[2023])

    assert FinancialAggregate.objects.count() == 0
    assert "Successfully synced 0 rows" in result


# ---- Risk aggregate tests ----


@pytest.mark.django_db
def test_save_aggregates_risk():
    rows = [
        {
            "date": "2024-01-01",
            "time_grain": "daily",
            "country_slug": "test",
            "dimension_type": "risk_module",
            "dimension_value": "CODE_A",
            "module": "registration",
            "risk_code": "CODE_A",
            "risk_name": "Risk A",
            "issue_count": 10,
            "percentage": 50.5,
            "unit_label": "payments",
            "severity": "CRITICAL",
            "trend": "UP",
            "threshold_info": ">=150%",
        }
    ]
    save_aggregates(
        rows,
        2024,
        "RiskAggregate",
        [
            "issue_count",
            "percentage",
            "module",
            "risk_code",
            "risk_name",
            "unit_label",
            "severity",
            "trend",
            "threshold_info",
        ],
    )

    agg = RiskAggregate.objects.get()
    assert agg.risk_code == "CODE_A"
    assert agg.module == "registration"
    assert agg.severity == RiskSeverity.CRITICAL
    assert agg.trend == RiskTrend.UP
    assert agg.issue_count == 10
    assert agg.threshold_info == ">=150%"


@pytest.mark.django_db
def test_save_aggregates_risk_defaults_and_normalization():
    rows = [
        {
            "date": "2024-01-01",
            "time_grain": "daily",
            "country_slug": "test",
            "dimension_type": "risk_module",
            "dimension_value": "code_b",
            "module": "registration",
            "issue_count": 3,
        }
    ]
    save_aggregates(
        rows,
        2024,
        "RiskAggregate",
        [
            "issue_count",
            "percentage",
            "module",
            "risk_code",
            "risk_name",
            "unit_label",
            "severity",
            "trend",
            "threshold_info",
        ],
    )

    agg = RiskAggregate.objects.get()
    assert agg.risk_code == "code_b"  # falls back to dimension_value
    assert agg.severity == RiskSeverity.NORMAL
    assert agg.trend == RiskTrend.NEUTRAL
    assert agg.unit_label == "payments"


@pytest.mark.django_db
def test_sync_daily_aggregates_with_risk_dataset(mocked_responses):
    """Risk dataset (query #10) is fetched and persisted into RiskAggregate."""
    api_url = config.HOPE_COUNTRY_REPORT_API_URL
    query_id = config.HOPE_RISK_REPORT_QUERY_ID

    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset",
        json={"results": [{"id": 1, "arguments": {"year": 2024}}]},
        status=200,
    )
    mocked_responses.add(
        responses.GET,
        f"{api_url}queries/{query_id}/dataset/1/data/?page_size=1000",
        json={
            "results": [
                {
                    "date": "2024-01-01",
                    "time_grain": "daily",
                    "country_slug": "test",
                    "dimension_type": "risk_module",
                    "dimension_value": "reconciliation_gap",
                    "module": "reconciliation",
                    "risk_code": "reconciliation_gap",
                    "risk_name": "Reconciliation gap",
                    "issue_count": 5,
                    "percentage": 80.5,
                    "unit_label": "payments",
                    "severity": "warning",
                    "trend": "up",
                }
            ],
            "next": None,
        },
        status=200,
    )

    with patch.object(sync_daily_aggregates, "update_state"):
        result = sync_daily_aggregates(target_years=[2024])

    assert RiskAggregate.objects.count() == 1
    agg = RiskAggregate.objects.get()
    assert agg.module == "reconciliation"
    assert agg.risk_code == "reconciliation_gap"
    assert agg.severity == RiskSeverity.WARNING
    assert agg.trend == RiskTrend.UP
    assert "Successfully synced 1 rows" in result


@pytest.mark.django_db
def test_clear_daily_aggregates_clears_risk(user_factory):
    user = user_factory(is_superuser=True)
    RiskAggregateFactory()
    assert RiskAggregate.objects.count() == 1

    result = clear_daily_aggregates(user.id)

    assert RiskAggregate.objects.count() == 0
    assert "Successfully deleted 1" in result


# ---- Parametrized clear tests ----

CLEAR_MODELS = [
    pytest.param(FinancialAggregateFactory, FinancialAggregate, id="financial"),
    pytest.param(DemographicAggregateFactory, DemographicAggregate, id="demographic"),
    pytest.param(CompletionAggregateFactory, CompletionAggregate, id="completion"),
    pytest.param(GrievanceAggregateFactory, GrievanceAggregate, id="grievance"),
]


@pytest.mark.django_db
@pytest.mark.parametrize(("factory_cls", "model_cls"), CLEAR_MODELS)
def test_clear_daily_aggregates_success(user_factory, factory_cls, model_cls):
    user = user_factory(is_superuser=True)
    factory_cls()
    assert model_cls.objects.count() == 1

    result = clear_daily_aggregates(user.id)
    assert model_cls.objects.count() == 0
    assert "Successfully deleted 1" in result


@pytest.mark.django_db
@pytest.mark.parametrize(("factory_cls", "model_cls"), CLEAR_MODELS)
def test_clear_daily_aggregates_non_superuser(user_factory, factory_cls, model_cls):
    user = user_factory(is_superuser=False)
    factory_cls()

    with pytest.raises(PermissionError, match="Permission denied"):
        clear_daily_aggregates(user.id)

    assert model_cls.objects.count() == 1


@pytest.mark.django_db
def test_clear_daily_aggregates_invalid_user():
    with pytest.raises(ValueError, match="Error: User not found."):
        clear_daily_aggregates(9999)
