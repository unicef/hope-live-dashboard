from unittest.mock import patch

import pytest
from django.utils import timezone

from hope_live.models import BusinessArea, Payment
from hope_live.tasks import refresh_business_area_stats, update_dashboard_cache

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def business_area():
    return BusinessArea.objects.create(id="ba-task-1", name="Task Country", slug="task-country", active=True)


@pytest.fixture
def payment(business_area):
    return Payment.objects.create(
        id="pay-task-1",
        status="Distribution Successful",
        delivered_quantity_usd=100.00,
        business_area=business_area,
        delivery_date=timezone.now(),
    )


def test_update_dashboard_cache(payment):
    with patch("hope_live.tasks.DashboardCache.invalidate") as mock_invalidate:
        result = update_dashboard_cache()

        mock_invalidate.assert_called_once()
        assert result["total_delivered"] == 100.00
        assert "timestamp" in result


def test_refresh_business_area_stats_success(payment, business_area):
    with patch("hope_live.tasks.DashboardCache.invalidate") as mock_invalidate:
        result = refresh_business_area_stats(business_area.slug)

        mock_invalidate.assert_called_once()
        assert result["business_area"] == business_area.slug
        assert result["total_payments"] == 1
        assert result["total_amount"] == 100.00


def test_refresh_business_area_stats_not_found():
    with patch("hope_live.tasks.logger.error") as mock_log:
        result = refresh_business_area_stats("non-existent-slug")

        assert result is None
        mock_log.assert_called()
