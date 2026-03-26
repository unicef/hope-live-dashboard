import json
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.views.generic import RedirectView, TemplateView

from hope_live.analysis.models import DailyAggregate


class ContactView(TemplateView):
    template_name = "pages/contacts.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


class IndexView(RedirectView):
    pattern_name = "web:dashboard"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Get all records to allow client-side filtering across years
        qs = DailyAggregate.objects.all()

        # For the high-level totals on page load, we use the 'sector' primary dimension
        summary = qs.filter(dimension_type="sector").aggregate(
            total_usd=Sum("total_usd", default=0),
            total_payments=Sum("payment_count", default=0),
            total_individuals=Sum("total_beneficiaries", default=0),
        )

        # Serialize the granular data for Crossfilter
        # We include all records so the user can switch between dimensions on the fly
        # if we implement that, or at least filter by them.
        data_list = list(
            qs.values(
                "date",
                "country_slug",
                "dimension_type",
                "dimension_value",
                "total_usd",
                "payment_count",
                "total_beneficiaries",
            )
        )

        context.update(
            {
                "financial": {
                    "total_usd": summary["total_usd"],
                    "total_payments": summary["total_payments"],
                },
                "demographic": {
                    "total_individuals": summary["total_individuals"],
                },
                "dashboard_data_json": json.dumps(data_list, cls=DjangoJSONEncoder),
            }
        )
        return context


class DemographicView(LoginRequiredMixin, TemplateView):
    template_name = "pages/demographic.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Get all records for client-side filtering
        qs = DailyAggregate.objects.all()

        # For high-level totals, use 'sector' primary dimension
        summary = qs.filter(dimension_type="sector").aggregate(
            total_individuals=Sum("total_beneficiaries", default=0),
            total_children=Sum("total_children", default=0),
            total_pwd=Sum("total_pwd", default=0),
        )

        # Granular data for Demographic-specific fields
        data_list = list(
            qs.values(
                "date",
                "country_slug",
                "dimension_type",
                "dimension_value",
                "total_beneficiaries",
                "total_children",
                "total_pwd",
            )
        )

        context.update(
            {
                "demographic": {
                    "total_individuals": summary["total_individuals"],
                    "total_children": summary["total_children"],
                    "total_pwd": summary["total_pwd"],
                },
                "dashboard_data_json": json.dumps(data_list, cls=DjangoJSONEncoder),
            }
        )
        return context


class CompletionView(LoginRequiredMixin, TemplateView):
    template_name = "pages/completion.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Get all records
        qs = DailyAggregate.objects.all()

        # For completion rate, we focus on the 'status' dimension type
        summary = qs.filter(dimension_type="status").aggregate(
            total_payments=Sum("payment_count", default=0),
            total_usd=Sum("total_usd", default=0),
        )

        # Granular data for Crossfilter
        data_list = list(
            qs.values(
                "date",
                "country_slug",
                "dimension_type",
                "dimension_value",
                "total_usd",
                "payment_count",
            )
        )

        context.update(
            {
                "completion": {
                    "total_payments": summary["total_payments"],
                    "total_usd": summary["total_usd"],
                },
                "dashboard_data_json": json.dumps(data_list, cls=DjangoJSONEncoder),
            }
        )
        return context


class LiveView(LoginRequiredMixin, TemplateView):
    template_name = "pages/live.html"


class TransfersView(LoginRequiredMixin, TemplateView):
    template_name = "pages/transfers.html"


class DetailsView(LoginRequiredMixin, TemplateView):
    template_name = "pages/details.html"
