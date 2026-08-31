import factory

from hope_live.analysis.models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
    RiskAggregate,
    TimeGrain,
)

from .base import AutoRegisterModelFactory


class FinancialAggregateFactory(AutoRegisterModelFactory):
    date = factory.Faker("date_this_year")
    time_grain = TimeGrain.DAILY
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

    class Meta:
        model = FinancialAggregate


class DemographicAggregateFactory(AutoRegisterModelFactory):
    date = factory.Faker("date_this_year")
    time_grain = TimeGrain.MONTHLY
    country_slug = factory.Faker("country_code")
    dimension_type = "sector"
    dimension_value = factory.Faker("word")

    total_beneficiaries = factory.Faker("random_int", min=0, max=100000)
    total_children = factory.Faker("random_int", min=0, max=50000)
    total_pwd = factory.Faker("random_int", min=0, max=10000)

    class Meta:
        model = DemographicAggregate


class CompletionAggregateFactory(AutoRegisterModelFactory):
    date = factory.Faker("date_this_year")
    time_grain = TimeGrain.DAILY
    country_slug = factory.Faker("country_code")
    dimension_type = "sector"
    dimension_value = factory.Faker("word")

    payment_count = factory.Faker("random_int", min=0, max=1000)
    total_usd = factory.Faker("pydecimal", left_digits=10, right_digits=2, positive=True)

    class Meta:
        model = CompletionAggregate


class GrievanceAggregateFactory(AutoRegisterModelFactory):
    date = factory.Faker("date_this_year")
    time_grain = TimeGrain.DAILY
    country_slug = factory.Faker("country_code")
    dimension_type = "category"
    dimension_value = factory.Faker("word")

    ticket_count = factory.Faker("random_int", min=0, max=5000)

    class Meta:
        model = GrievanceAggregate


class RiskAggregateFactory(AutoRegisterModelFactory):
    date = factory.Faker("date_this_year")
    time_grain = TimeGrain.DAILY
    country_slug = factory.Faker("country_code")
    dimension_type = "risk_module"
    dimension_value = factory.Faker("slug")

    module = factory.Faker(
        "random_element",
        elements=["registration", "payment_operations", "reconciliation", "verification", "grievance"],
    )
    risk_code = factory.LazyAttribute(lambda o: o.dimension_value)
    risk_name = factory.Faker("sentence", nb_words=3)
    issue_count = factory.Faker("random_int", min=0, max=500)
    percentage = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    unit_label = "payments"
    severity = factory.Faker("random_element", elements=["critical", "warning", "caution", "normal"])
    trend = factory.Faker("random_element", elements=["up", "down", "neutral"])

    class Meta:
        model = RiskAggregate
