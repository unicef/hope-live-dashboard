import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_authentication_workflow():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="securepass123")

    assert user.check_password("securepass123")
    assert not user.check_password("wrongpassword")
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_superuser_privileges():
    superuser = User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass123")

    assert superuser.is_staff
    assert superuser.is_superuser
    assert superuser.is_active
    assert superuser.check_password("adminpass123")


@pytest.mark.django_db
def test_user_factory_creates_valid_users(user_factory):
    user1 = user_factory()
    user2 = user_factory(username="specific_user", email="specific@example.com")

    assert user1.pk is not None
    assert user2.pk is not None
    assert user2.username == "specific_user"
    assert user2.email == "specific@example.com"

    user1.set_password("newpassword123")
    assert user1.check_password("newpassword123")


@pytest.mark.django_db
def test_multiple_users_with_factory(user_factory):
    users = [user_factory() for _ in range(10)]

    assert len(users) == 10
    assert len({u.username for u in users}) == 10
    assert len({u.email for u in users}) == 10
    assert all(u.pk is not None for u in users)
