import pytest
from django.core.exceptions import ValidationError
from testutils.factories import OfficeFactory
from testutils.factories.userrole import UserRoleFactory

from hope_live.models import Program


def test_user_role_clean_valid(db):
    office = OfficeFactory()
    # Case 1: No program
    role = UserRoleFactory(country_office=office, program=None)
    role.clean()  # Should not raise


def test_user_role_clean_invalid(db):
    office1 = OfficeFactory()
    office2 = OfficeFactory()

    # We need to create a program associated with office2
    program = Program.objects.create(country_office=office2, name="Prog 2")

    role = UserRoleFactory(country_office=office1, program=program)

    with pytest.raises(ValidationError) as exc:
        role.clean()

    assert "Program does not belong to country office" in str(exc.value)
