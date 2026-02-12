"""
Basic test to verify coverage is working.
"""

import pytest


def test_import_hope_live():
    """Test that we can import the main module."""
    import hope_live

    assert hope_live is not None
    assert hasattr(hope_live, "__version__")


def test_import_models():
    """Test that we can import models."""
    from hope_live.models import Office, Program, User, UserRole

    assert User is not None
    assert Office is not None
    assert Program is not None
    assert UserRole is not None


def test_import_analysis():
    """Test that we can import analysis module."""
    from hope_live.analysis.models import DailyAggregate

    assert DailyAggregate is not None


@pytest.mark.django_db
def test_create_user(user_factory):
    """Test user creation with factory."""
    user = user_factory()
    assert user is not None
    assert user.username is not None
    assert user.email is not None


@pytest.mark.django_db
def test_create_office(office_factory):
    """Test office creation with factory."""
    office = office_factory()
    assert office is not None
    assert office.name is not None
    assert office.code is not None


@pytest.mark.django_db
def test_create_program(program_factory, office_factory):
    """Test program creation with factory."""
    office = office_factory()
    program = program_factory(country_office=office)
    assert program is not None
    assert program.name is not None
    assert program.country_office == office
