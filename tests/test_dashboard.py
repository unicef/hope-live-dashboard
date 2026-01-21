import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from django.utils import timezone

from hope_live.models import BusinessArea, DeliveryMechanism, FinancialServiceProvider, HopeProgram, Payment
from hope_live.utils.cache import DashboardCache

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def business_area():
    return BusinessArea(id=uuid.uuid4(), name="Test Country", slug="test-country", active=True, region_name="TEST")


@pytest.fixture
def program(business_area):
    return HopeProgram(
        id=uuid.uuid4(), name="Test Program", sector="Health", status="Active", business_area=business_area
    )


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanism(id=uuid.uuid4(), name="Mobile Money")


@pytest.fixture
def fsp():
    return FinancialServiceProvider(id=uuid.uuid4(), name="Test Bank")


@pytest.fixture
def payment(business_area, program, delivery_mechanism, fsp):
    return Payment(
        id=uuid.uuid4(),
        status="Distribution Successful",
        currency="USD",
        delivered_quantity_usd=100.00,
        delivered_quantity=100.00,
        entitlement_quantity_usd=100.00,
        delivery_date=timezone.now(),
        business_area=business_area,
        program=program,
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
    )


def test_dashboard_view(client, payment):
    with patch("hope_live.web.views.Payment.objects.all") as mock_all:
        mock_queryset = MagicMock()
        mock_all.return_value = mock_queryset

        mock_filter = MagicMock()
        mock_queryset.filter.return_value = mock_filter
        mock_filter.aggregate.return_value = {"total": 100.00}

        url = reverse("web:dashboard")
        response = client.get(url)
        assert response.status_code == 200
        assert "total_delivered_usd" in response.context
        assert response.context["total_delivered_usd"] == 100.00


def test_payment_aggregates_api(client, payment):
    with patch("hope_live.web.views.Payment.objects.filter") as mock_filter:
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset

        mock_queryset.values.return_value = mock_queryset
        mock_queryset.order_by.return_value = [
            {
                "id": str(payment.id),
                "delivered_quantity_usd": 100.00,
                "status": "Distribution Successful",
                "delivery_date": payment.delivery_date,
                "business_area__name": "Test Country",
                "program__name": "Test Program",
            }
        ]

        url = reverse("web:dashboard_data")
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


def test_dashboard_data_api(client, payment):
    with patch("hope_live.web.views.Payment.objects.filter") as mock_filter:
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset

        mock_queryset.aggregate.return_value = {"total_delivered_quantity_usd": 100.00}
        mock_queryset.count.return_value = 1

        url = reverse("web:dashboard_api")
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


def test_caching_mechanism(client, payment):
    DashboardCache.invalidate()
    url = reverse("web:dashboard_api")

    with patch("django.core.cache.cache.set") as mock_set:
        with patch("hope_live.web.views.Payment.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset
            mock_queryset.aggregate.return_value = {"total_delivered_quantity_usd": 100.00}
            mock_queryset.count.return_value = 1

            client.get(url)
            assert mock_set.called

    with patch("hope_live.utils.cache.DashboardCache.get_key", return_value="test_key"):
        with patch("django.core.cache.cache.get") as mock_get:
            mock_get.return_value = [{"cached": True}]
            response = client.get(url)
            assert response.json() == [{"cached": True}]


def test_cache_invalidation():
    DashboardCache.invalidate()
    key1 = DashboardCache.get_key("test")
    DashboardCache.invalidate()
    key2 = DashboardCache.get_key("test")
    assert key1 != key2
