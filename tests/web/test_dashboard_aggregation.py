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

    url = reverse("web:dashboard_api")
    response = client.get(url, {"business_area": "test-area"})

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    item = data[0]

    # Verify Aggregations
    # Total USD: 100 + 50 + 200 = 350
    assert item["total_delivered_quantity_usd"] == 350.0

    # Payments: 3
    assert item["payments"] == 3

    # Households: 2 (HH1 and HH2)
    assert item["households"] == 2

    # Individuals: HH1(4) + HH2(5) = 9
    assert item["individuals"] == 9

    # Children: HH1(2) + HH2(3) = 5.
    # Note: HH1 is counted once despite having 2 payments.
    assert item["children_counts"] == 5

    # PWD: HH1(1) + HH2(2) = 3
    assert item["pwd_counts"] == 3
