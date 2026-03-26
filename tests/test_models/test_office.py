import pytest
from django.db import transaction
from django.db.utils import IntegrityError

from hope_live.models import Office


@pytest.mark.django_db
def test_office_creation_with_all_fields():
    office = Office.objects.create(
        hope_id="OFF001",
        name="Test Office",
        long_name="Test Country Office Long Name",
        code="TST",
        slug="test-office",
        active=True,
        enabled=True,
        extra_fields={"region": "EMEA", "timezone": "UTC+1"},
    )

    assert office.hope_id == "OFF001"
    assert office.name == "Test Office"
    assert office.code == "TST"
    assert office.slug == "test-office"
    assert office.active is True
    assert office.enabled is True
    assert office.extra_fields["region"] == "EMEA"


@pytest.mark.django_db
def test_office_unique_constraints_enforced():
    Office.objects.create(hope_id="UNIQUE001", name="Office 1", code="OFC1", slug="office-1")

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            Office.objects.create(hope_id="UNIQUE001", name="Office 2", code="OFC2", slug="office-2")

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            Office.objects.create(hope_id="UNIQUE002", name="Office 3", code="OFC1", slug="office-3")

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            Office.objects.create(hope_id="UNIQUE003", name="Office 4", code="OFC4", slug="office-1")


@pytest.mark.django_db
def test_office_factory_produces_valid_data(office_factory):
    office = office_factory(name="Custom Office", active=False, enabled=True)

    assert office.name == "Custom Office"
    assert office.active is False
    assert office.enabled is True
    assert office.code is not None
    assert office.slug is not None
    assert isinstance(office.extra_fields, dict)


@pytest.mark.django_db
def test_bulk_office_operations():
    offices = [
        Office(
            hope_id=f"BULK{i:03d}",
            name=f"Bulk Office {i}",
            code=f"BLK{i}",
            slug=f"bulk-office-{i}",
            active=i % 2 == 0,
            enabled=True,
        )
        for i in range(5)
    ]

    Office.objects.bulk_create(offices)

    active_offices = Office.objects.filter(active=True)
    inactive_offices = Office.objects.filter(active=False)

    assert active_offices.count() == 3
    assert inactive_offices.count() == 2
    assert Office.objects.filter(code__startswith="BLK").count() == 5
