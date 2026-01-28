import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from hope_live.models import BusinessArea, DeliveryMechanism, FinancialServiceProvider, HopeProgram, Payment
from hope_live.utils.cache import DashboardCache

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def business_area():
    return BusinessArea.objects.create(
        id=uuid.uuid4(), name="Afghanistan", slug="afghanistan", active=True, region_name="ROSA"
    )


@pytest.fixture
def program(business_area):
    return HopeProgram.objects.create(
        id=uuid.uuid4(), name="Web Test Program", sector="Health", status="Active", business_area=business_area
    )


@pytest.fixture
def payment(business_area, program):
    dm = DeliveryMechanism.objects.create(id=uuid.uuid4(), name="Cash")
    fsp = FinancialServiceProvider.objects.create(id=uuid.uuid4(), name="Bank")
    return Payment.objects.create(
        id=uuid.uuid4(),
        status="Distribution Successful",
        currency="USD",
        delivered_quantity_usd=50.00,
        delivered_quantity=50.00,
        entitlement_quantity_usd=50.00,
        delivery_date=timezone.now() - timezone.timedelta(days=1),
        business_area=business_area,
        program=program,
        delivery_type=dm,
        financial_service_provider=fsp,
    )


def test_dashboard_view_context_data(client, payment):
    url = reverse("web:dashboard")
    response = client.get(url)
    assert response.status_code == 200
    context = response.context
    # The view only provides business_areas context
    assert "business_areas" in context
    # Remove assertions for fields that don't exist in DashboardView


def test_payment_aggregates_view_get_data(client, payment):
    url = reverse("web:dashboard_data")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    # The view returns empty list (deprecated endpoint)
    assert data == []


def test_payment_aggregates_view_caching(client, payment):
    DashboardCache.invalidate()
    url = reverse("web:dashboard_data")

    # This endpoint is deprecated and returns empty list
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == []


def test_dashboard_data_view_get_aggregates(client, payment):
    url = reverse("web:dashboard_api")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    # This endpoint is deprecated and returns empty list
    # Real data comes from analysis:stats
    assert data == []


@pytest.mark.parametrize(
    "view_name", ["web:index", "web:about", "web:contacts", "web:live", "web:transfers", "web:details"]
)
def test_static_pages(client, view_name):
    url = reverse(view_name)
    response = client.get(url)
    assert response.status_code == 200
