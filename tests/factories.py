import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from hope_live.models import Office, Program, UserRole

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    is_active = True


class OfficeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Office

    hope_id = factory.Sequence(lambda n: f"hope{n}")
    name = factory.Sequence(lambda n: f"Office {n}")
    long_name = factory.Sequence(lambda n: f"Long Office Name {n}")
    code = factory.Sequence(lambda n: f"OFF{n}")
    slug = factory.Sequence(lambda n: f"office-{n}")
    active = True
    enabled = True


class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program

    hope_id = factory.Sequence(lambda n: f"program_hope{n}")
    name = factory.Sequence(lambda n: f"Program {n}")
    code = factory.Sequence(lambda n: f"PRG{n}")
    status = "active"
    sector = "health"
    country_office = factory.SubFactory(OfficeFactory)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group {n}")


class UserRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserRole

    user = factory.SubFactory(UserFactory)
    country_office = factory.SubFactory(OfficeFactory)
    program = None
    group = factory.SubFactory(GroupFactory)
    expires = None
