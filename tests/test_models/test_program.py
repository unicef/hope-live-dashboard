import pytest
from django.db.utils import IntegrityError

from hope_live.models import Office, Program


@pytest.mark.django_db
def test_program_creation_and_relationships():
    office = Office.objects.create(name="Main Office", code="MAIN", slug="main-office")
    program = Program.objects.create(
        hope_id="PROG001",
        country_office=office,
        name="Health Program",
        code="HLTH001",
        status="active",
        sector="Health",
    )

    assert program.hope_id == "PROG001"
    assert program.country_office == office
    assert program.name == "Health Program"
    assert program.status == "active"
    assert program.sector == "Health"
    assert program in office.programs.all()


@pytest.mark.django_db
def test_program_hope_id_uniqueness():
    office = Office.objects.create(name="Test Office", code="TEST", slug="test-office")
    Program.objects.create(
        hope_id="UNIQUE001", country_office=office, name="Program A", status="active", sector="Health"
    )

    with pytest.raises(IntegrityError):
        Program.objects.create(
            hope_id="UNIQUE001", country_office=office, name="Program B", status="draft", sector="Education"
        )


@pytest.mark.django_db
def test_program_factory_with_office_relationship(program_factory, office_factory):
    office = office_factory()
    program = program_factory(country_office=office, name="Factory Program", status="completed", sector="Nutrition")

    assert program.country_office == office
    assert program.name == "Factory Program"
    assert program.status == "completed"
    assert program.sector == "Nutrition"
    assert program in office.programs.all()


@pytest.mark.django_db
def test_multiple_programs_per_office(program_factory, office_factory):
    office = office_factory()
    programs = [
        program_factory(country_office=office, name=f"Program {i}", sector=["Health", "Education", "Nutrition"][i % 3])
        for i in range(6)
    ]

    assert len(programs) == 6
    assert office.programs.count() == 6
    assert len({p.sector for p in programs}) == 3
    assert all(p.country_office == office for p in programs)
