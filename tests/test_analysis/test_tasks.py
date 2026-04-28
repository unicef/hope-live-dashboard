from unittest.mock import patch

import pytest
import responses
from constance import config

from hope_live.analysis.models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
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
    assert result == "[Job N/A] Failed to prepare sync context."


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
