import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from hope_live.models import BusinessArea, Payment
from hope_live.tasks import refresh_business_area_stats, update_dashboard_cache

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def business_area():
    return BusinessArea(id=uuid.uuid4(), name="Afghanistan", slug="afghanistan", active=True, region_name="Test Region")


@pytest.fixture
def payment(business_area):
    return Payment(
        id=uuid.uuid4(),
        status="Distribution Successful",
        delivered_quantity_usd=100.00,
        business_area=business_area,
        delivery_date=timezone.now(),
    )


def test_update_dashboard_cache(payment):
    with patch("hope_live.tasks.DashboardCache.invalidate") as mock_invalidate:
        with patch("hope_live.tasks.Payment.objects.all") as mock_all:
            mock_queryset = MagicMock()
            mock_filter = MagicMock()

            mock_all.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_filter
            mock_filter.aggregate.return_value = {"total": 100.00}

            result = update_dashboard_cache()

            mock_invalidate.assert_called_once()
            assert result["total_delivered"] == 100.00
            assert "timestamp" in result


def test_refresh_business_area_stats_success(payment, business_area):
    with patch("hope_live.tasks.DashboardCache.invalidate") as mock_invalidate:
        with patch("hope_live.tasks.BusinessArea.objects.get") as mock_get:
            mock_get.return_value = business_area

            with patch("hope_live.tasks.Payment.objects.filter") as mock_filter:
                mock_queryset = MagicMock()
                mock_filter.return_value = mock_queryset

                mock_queryset.count.return_value = 1

                mock_success_filter = MagicMock()
                mock_queryset.filter.return_value = mock_success_filter
                mock_success_filter.count.return_value = 1

                mock_queryset.aggregate.return_value = {"total": 100.00}

                result = refresh_business_area_stats(business_area.slug)

                mock_invalidate.assert_called_once()
                assert result["business_area"] == business_area.slug
                assert result["total_payments"] == 1
                assert result["total_amount"] == 100.00


def test_refresh_business_area_stats_not_found():
    with patch("hope_live.tasks.logger.error") as mock_log:
        with patch("hope_live.tasks.BusinessArea.objects.get") as mock_get:
            mock_get.side_effect = BusinessArea.DoesNotExist()

            result = refresh_business_area_stats("non-existent-slug")

            assert result is None
            mock_log.assert_called()
