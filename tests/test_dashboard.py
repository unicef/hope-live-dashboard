from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone

from hope_live.models import BusinessArea, DeliveryMechanism, FinancialServiceProvider, HopeProgram, Payment
from hope_live.utils.cache import DashboardCache

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def business_area():
    return BusinessArea.objects.create(
        id="ba-1", name="Test Country", slug="test-country", active=True, region_name="TEST"
    )


@pytest.fixture
def program(business_area):
    return HopeProgram.objects.create(
        id="prog-1", name="Test Program", sector="Health", status="Active", business_area=business_area
    )


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanism.objects.create(id="dm-1", name="Mobile Money")


@pytest.fixture
def fsp():
    return FinancialServiceProvider.objects.create(id="fsp-1", name="Test Bank")


@pytest.fixture
def payment(business_area, program, delivery_mechanism, fsp):
    return Payment.objects.create(
        id="pay-1",
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
    url = reverse("web:dashboard")
    response = client.get(url)
    assert response.status_code == 200
    assert "total_delivered_usd" in response.context
    assert response.context["total_delivered_usd"] == 100.00


def test_payment_aggregates_api(client, payment):
    url = reverse("web:dashboard_data")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(payment.id)
    assert data[0]["delivered_quantity_usd"] == 100.00


def test_dashboard_data_api(client, payment):
    url = reverse("web:dashboard_api")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["total_delivered_quantity_usd"] == 100.00
    assert data[0]["payments"] == 1


def test_caching_mechanism(client, payment):
    DashboardCache.invalidate()
    url = reverse("web:dashboard_api")

    # First request - should cache
    with patch("django.core.cache.cache.set") as mock_set:
        client.get(url)
        assert mock_set.called

    # Second request - should hit cache
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
