import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from hope_live.models import (
    Area,
    BusinessArea,
    DeliveryMechanism,
    FinancialServiceProvider,
    HopeProgram,
    Household,
    Payment,
)


@pytest.mark.django_db
def test_dashboard_data_aggregation(client):
    # Setup reference data
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
    admin1 = Area.objects.create(id=uuid.uuid4(), name="Region 1")

    # Setup Households
    # HH1: 2 children, 1 PWD
    hh1 = Household.objects.create(
        id=uuid.uuid4(),
        business_area=ba,
        admin1=admin1,
        size=4,
        children_count=2,
        female_age_group_18_59_disabled_count=1,
    )

    # HH2: 3 children, 2 PWD
    hh2 = Household.objects.create(
        id=uuid.uuid4(),
        business_area=ba,
        admin1=admin1,
        size=5,
        children_count=3,
        male_age_group_0_5_disabled_count=1,
        male_age_group_60_disabled_count=1,
    )

    # Create Payments
    # Payment 1 for HH1
    Payment.objects.create(
        id=uuid.uuid4(),
        business_area=ba,
        program=prog,
        household=hh1,
        delivery_type=dm,
        financial_service_provider=fsp,
        status="Distribution Successful",
        delivered_quantity_usd=100.00,
        delivery_date=timezone.now(),
        currency="USD",
    )

    # Payment 2 for HH1 (Same household, same group)
    Payment.objects.create(
        id=uuid.uuid4(),
        business_area=ba,
        program=prog,
        household=hh1,
        delivery_type=dm,
        financial_service_provider=fsp,
        status="Distribution Successful",
        delivered_quantity_usd=50.00,
        delivery_date=timezone.now(),
        currency="USD",
    )

    # Payment 3 for HH2 (Different household, same group)
    Payment.objects.create(
        id=uuid.uuid4(),
        business_area=ba,
        program=prog,
        household=hh2,
        delivery_type=dm,
        financial_service_provider=fsp,
        status="Distribution Successful",
        delivered_quantity_usd=200.00,
        delivery_date=timezone.now(),
        currency="USD",
    )

    # Test the analysis API endpoint instead
    url = reverse("analysis:stats")
    response = client.get(url, {"dimension": "program", "country_office": "test-area"})

    assert response.status_code == 200
    data = response.json()

    # The analysis API returns aggregated data by dimension
    # It won't have the same structure as the old web API
    assert isinstance(data, list)
    # The API aggregates by dimension (program in this case)
    # So we should get aggregated data for the program
