from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import TemplateView

from hope_live.analysis.models import DemographicAggregate, FinancialAggregate


class ContactView(TemplateView):
    template_name = "pages/contacts.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


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

        context["total_cash_disbursed"] = f"{total_usd:,.0f}"
        context["total_individuals_reached"] = f"{total_beneficiaries:,}"
        context["verification_success_rate"] = 98.7  # Hardcoded for now as per mockup

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
