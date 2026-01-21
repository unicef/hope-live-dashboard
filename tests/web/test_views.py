import uuid
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
    assert context["total_delivered_usd"] == 50.00
    assert context["total_payments_count"] == 1
    assert context["successful_payments_count"] == 1
    assert context["pending_payments_count"] == 0


def test_payment_aggregates_view_get_data(client, payment):
    url = reverse("web:dashboard_data")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(payment.id)
    assert data[0]["delivered_quantity_usd"] == 50.00


def test_payment_aggregates_view_caching(client, payment):
    DashboardCache.invalidate()
    url = reverse("web:dashboard_data")

    # First call caches
    with patch("django.core.cache.cache.set") as mock_set:
        client.get(url)
        assert mock_set.called

    # Second call uses cache
    with patch("hope_live.utils.cache.DashboardCache.get_key", return_value="test_key"):
        with patch("django.core.cache.cache.get") as mock_get:
            mock_get.return_value = [{"cached": True}]
            response = client.get(url)
            assert response.json() == [{"cached": True}]


def test_dashboard_data_view_get_aggregates(client, payment):
    url = reverse("web:dashboard_api")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["total_delivered_quantity_usd"] == 50.00
    assert data[0]["payments"] == 1


@pytest.mark.parametrize(
    "view_name", ["web:index", "web:about", "web:contacts", "web:live", "web:transfers", "web:details"]
)
def test_static_pages(client, view_name):
    url = reverse(view_name)
    response = client.get(url)
    assert response.status_code == 200
