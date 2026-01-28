import uuid

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
    url = reverse("web:dashboard")
    response = client.get(url)
    assert response.status_code == 200
    # DashboardView just renders template with business_areas
    assert "business_areas" in response.context


def test_payment_aggregates_api(client, payment):
    url = reverse("web:dashboard_data")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    # Deprecated endpoint returns empty list
    assert data == []


def test_dashboard_data_api(client, payment):
    url = reverse("web:dashboard_api")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    # Deprecated endpoint returns empty list
    # Use analysis:stats for real data
    assert data == []


def test_caching_mechanism(client, payment):
    DashboardCache.invalidate()
    url = reverse("web:dashboard_api")

    # Deprecated endpoint doesn't use caching
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == []


def test_cache_invalidation():
    DashboardCache.invalidate()
    key1 = DashboardCache.get_key("test")
    DashboardCache.invalidate()
    key2 = DashboardCache.get_key("test")
    assert key1 != key2
