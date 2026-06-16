from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Sum
from django.views.generic import TemplateView

from hope_live.analysis.models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
)


class ContactView(TemplateView):
    template_name = "pages/contacts.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


BILLION = 1_000_000_000
MILLION = 1_000_000
THOUSAND = 1_000


def format_large_number(num: float) -> str:
    if num >= BILLION:
        val = num / BILLION
        return f"{val:.1f}B".replace(".0B", "B")
    if num >= MILLION:
        val = num / MILLION
        return f"{val:.1f}M".replace(".0M", "M")
    if num >= THOUSAND:
        val = num / THOUSAND
        return f"{val:.1f}K".replace(".0K", "K")
    return str(int(num))


class IndexView(TemplateView):
    template_name = "pages/landing.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Calculate Total Cash Disbursed (filtering by sector to avoid double counting)
        total_usd = (
            FinancialAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_usd"))["total"] or 0
        )

        # Calculate Total Individuals Reached
        total_beneficiaries = (
            DemographicAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_beneficiaries"))[
                "total"
            ]
            or 0
        )

        # Calculate Total Children Reached
        total_children = (
            DemographicAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_children"))["total"]
            or 0
        )

        # Calculate Total Households Reached
        total_households = (
            DemographicAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_households"))[
                "total"
            ]
            or 0
        )

        # Calculate Active Countries Count
        total_countries = FinancialAggregate.objects.values("country_slug").distinct().count()

        # HOPE at a glance sidebar statistics
        # Unique countries across all aggregates
        countries_set = set(FinancialAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.update(DemographicAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.update(CompletionAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.update(GrievanceAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.discard("")
        countries_set.discard(None)
        total_countries_glance = len(countries_set)

        # Unique programs count from FinancialAggregate (where dimension_type is program)
        total_programs_glance = (
            FinancialAggregate.objects.filter(dimension_type="program").values("dimension_value").distinct().count()
        )

        # Data source name
        total_sources_glance = "HOPE Database"

        # Find latest data date
        latest_date_f = FinancialAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        latest_date_d = DemographicAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        latest_date_c = CompletionAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        latest_date_g = GrievanceAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        dates = [d for d in [latest_date_f, latest_date_d, latest_date_c, latest_date_g] if d]
        latest_data_date = max(dates) if dates else None

        if latest_data_date:
            latest_data_str = latest_data_date.strftime("%B %Y")
        else:
            latest_data_str = "May 2026"

        context["total_cash_disbursed"] = format_large_number(total_usd)
        context["total_individuals_reached"] = format_large_number(total_beneficiaries)
        context["total_children"] = format_large_number(total_children)
        context["total_households"] = format_large_number(total_households)
        context["total_countries"] = total_countries
        # Calculate verification success rate from CompletionAggregate status counts
        reconciled_sum = (
            CompletionAggregate.objects.filter(dimension_type="status", dimension_value="RECONCILED").aggregate(
                total=Sum("payment_count")
            )["total"]
            or 0
        )
        open_sum = (
            CompletionAggregate.objects.filter(dimension_type="status", dimension_value="OPEN").aggregate(
                total=Sum("payment_count")
            )["total"]
            or 0
        )
        total_payments = reconciled_sum + open_sum
        if total_payments > 0:
            context["verification_success_rate"] = round((reconciled_sum / total_payments) * 100, 1)
        else:
            context["verification_success_rate"] = 98.7

        context["total_countries_glance"] = total_countries_glance or 170
        context["total_programs_glance"] = total_programs_glance or 450
        context["total_sources_glance"] = total_sources_glance
        context["latest_data_str"] = latest_data_str

        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)
        # Data is now fetched via REST API by year tabs
        # No server-side metrics or embedded JSON needed


class DemographicView(LoginRequiredMixin, TemplateView):
    template_name = "pages/demographic.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)
        # Data is now fetched via REST API by year tabs
        # No server-side metrics or embedded JSON needed


class CompletionView(LoginRequiredMixin, TemplateView):
    template_name = "pages/completion.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)
        # Data is now fetched via REST API by year tabs
        # No server-side metrics or embedded JSON needed


class GrievanceView(LoginRequiredMixin, TemplateView):
    template_name = "pages/grievance.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)


class TransfersView(LoginRequiredMixin, TemplateView):
    template_name = "pages/transfers.html"


class DetailsView(LoginRequiredMixin, TemplateView):
    template_name = "pages/details.html"
