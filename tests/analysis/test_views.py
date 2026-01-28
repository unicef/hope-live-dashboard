import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from hope_live.models import BusinessArea, DeliveryMechanism, FinancialServiceProvider, HopeProgram, Payment


@pytest.mark.django_db
def test_dashboard_stats_api_view():
    # Setup test data
    ba = BusinessArea.objects.create(id=uuid.uuid4(), name="Test Area", slug="test-area", active=True)
    prog = HopeProgram.objects.create(
        id=uuid.uuid4(),
        name="Test Program",
        sector="Health",
        status="Active",
        business_area=ba,
    )
    dm = DeliveryMechanism.objects.create(id=uuid.uuid4(), name="Cash")
    fsp = FinancialServiceProvider.objects.create(id=uuid.uuid4(), name="Bank")

    # Create a payment
    Payment.objects.create(
        id=uuid.uuid4(),
        business_area=ba,
        program=prog,
        delivery_type=dm,
        financial_service_provider=fsp,
        status="Distribution Successful",
        delivered_quantity_usd=100.00,
        delivery_date=timezone.now(),
        currency="USD",
    )

    # Run the aggregation task
    from hope_live.analysis.tasks import refresh_daily_aggregates

    refresh_daily_aggregates()

    # Test the API
    from django.test import Client

    client = Client()
    url = reverse("analysis:stats")

    # Test with program dimension
    response = client.get(url, {"dimension": "program", "country_office": "test-area"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Test with sector dimension
    response = client.get(url, {"dimension": "sector", "country_office": "test-area"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Test without country_office filter
    response = client.get(url, {"dimension": "program"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
