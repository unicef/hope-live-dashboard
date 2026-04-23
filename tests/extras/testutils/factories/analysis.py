import factory

from hope_live.analysis.models import DailyAggregate

from .base import AutoRegisterModelFactory


class DailyAggregateFactory(AutoRegisterModelFactory):
    date = factory.Faker("date_this_year")
    country_slug = factory.Faker("country_code")
    dimension_type = factory.Faker(
        "random_element",
        elements=[
            "sector",
            "program",
            "delivery_type",
            "financial_service_provider",
            "status",
            "currency",
            "admin_area",
            "region",
        ],
    )
    dimension_value = factory.Faker("word")

    total_usd = factory.Faker("pydecimal", left_digits=10, right_digits=2, positive=True)
    total_qty = factory.Faker("pydecimal", left_digits=10, right_digits=2, positive=True)
    payment_count = factory.Faker("random_int", min=1, max=1000)
    total_beneficiaries = factory.Faker("random_int", min=0, max=5000)
    total_children = factory.Faker("random_int", min=0, max=2000)
    total_pwd = factory.Faker("random_int", min=0, max=500)

    class Meta:
        model = DailyAggregate
