import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from factories import GroupFactory, OfficeFactory, ProgramFactory, UserFactory, UserRoleFactory

pytestmark = pytest.mark.django_db


def test_create_user_role_without_program():
    """Test creating a UserRole without a program should be valid."""
    user = UserFactory()
    office = OfficeFactory()
    group = GroupFactory()

    role = UserRoleFactory(user=user, country_office=office, group=group, program=None)
    role.full_clean()
    assert role.program is None


def test_create_user_role_with_program_same_office():
    """Test creating a UserRole with a program belonging to the same office."""
    office = OfficeFactory()
    program = ProgramFactory(country_office=office)
    user = UserFactory()
    group = GroupFactory()

    role = UserRoleFactory(user=user, country_office=office, program=program, group=group)
    role.full_clean()
    assert role.program == program
    assert role.country_office == office


def test_create_user_role_with_program_different_office_raises_validation_error():
    """Test that a UserRole with a program from a different office raises ValidationError."""
    office1 = OfficeFactory()
    office2 = OfficeFactory()
    program = ProgramFactory(country_office=office2)
    user = UserFactory()
    group = GroupFactory()

    role = UserRoleFactory.build(user=user, country_office=office1, program=program, group=group)
    with pytest.raises(ValidationError) as exc_info:
        role.full_clean()
    assert "program" in str(exc_info.value)


def test_unique_constraint_user_office_group():
    """Test that the same user, office, and group combination cannot exist twice."""
    user = UserFactory()
    office = OfficeFactory()
    group = GroupFactory()

    UserRoleFactory(user=user, country_office=office, group=group)
    with pytest.raises(IntegrityError):
        UserRoleFactory(user=user, country_office=office, group=group)


def test_unique_constraint_allows_different_groups():
    """Test that the same user and office with different groups are allowed."""
    user = UserFactory()
    office = OfficeFactory()
    group1 = GroupFactory()
    group2 = GroupFactory()

    role1 = UserRoleFactory(user=user, country_office=office, group=group1)
    role2 = UserRoleFactory(user=user, country_office=office, group=group2)
    assert role1.group != role2.group
    assert role1.user == role2.user
    assert role1.country_office == role2.country_office


def test_unique_constraint_allows_different_offices():
    """Test that the same user and group with different offices are allowed."""
    user = UserFactory()
    office1 = OfficeFactory()
    office2 = OfficeFactory()
    group = GroupFactory()

    role1 = UserRoleFactory(user=user, country_office=office1, group=group)
    role2 = UserRoleFactory(user=user, country_office=office2, group=group)
    assert role1.country_office != role2.country_office
    assert role1.user == role2.user
    assert role1.group == role2.group


def test_expires_field_nullable():
    """Test that expires field can be null."""
    role = UserRoleFactory(expires=None)
    assert role.expires is None


def test_expires_field_set():
    """Test that expires field can be set to a date."""
    from datetime import date

    future_date = date(2025, 12, 31)
    role = UserRoleFactory(expires=future_date)
    assert role.expires == future_date


def test_str_representation():
    """Test the string representation of UserRole."""
    user = UserFactory(username="testuser")
    office = OfficeFactory(name="Test Office")
    group = GroupFactory(name="Test Group")
    role = UserRoleFactory(user=user, country_office=office, group=group)
    str(role)


def test_clean_method_called_on_save():
    """Test that the clean method is called when saving a UserRole."""
    office1 = OfficeFactory()
    office2 = OfficeFactory()
    program = ProgramFactory(country_office=office2)
    user = UserFactory()
    group = GroupFactory()

    role = UserRoleFactory.build(user=user, country_office=office1, program=program, group=group)
    with pytest.raises(ValidationError):
        role.full_clean()
