from datetime import date
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
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

        # Default to current year, or allow filtering via GET params later
        target_year = date.today().year

        # Base QuerySet for this year
        qs = DailyAggregate.objects.filter(date__year=target_year)

        # For High-Level Totals (Cards), we must filter by ONE dimension type to avoid double counting.
        # "sector" is a good candidate if every payment has a sector.
        # Alternatively "status" (but status might be mixed).
        # Let's use 'sector' as the primary partition.
        primary_dim = "sector"

        totals = qs.filter(dimension_type=primary_dim).aggregate(
            total_usd=Sum("total_usd", default=0),
            total_qty=Sum("total_qty", default=0),
            total_payments=Sum("payment_count", default=0),
            total_beneficiaries=Sum("total_beneficiaries", default=0),
        )

        context.update(
            {
                "year": target_year,
                "financial": {
                    "total_usd": totals["total_usd"],
                    "total_payments": totals["total_payments"],
                },
                "demographic": {
                    "total_individuals": totals["total_beneficiaries"],
                },
                # Chart Data: By Sector
                "by_sector": list(
                    qs.filter(dimension_type="sector")
                    .values("dimension_value")
                    .annotate(value=Sum("total_usd"))
                    .order_by("-value")
                ),
                # Chart Data: By Country
                "by_country": list(
                    qs.filter(dimension_type=primary_dim)
                    .values("country_slug")
                    .annotate(value=Sum("total_usd"))
                    .order_by("-value")
                ),
            }
        )
        return context


class LiveView(LoginRequiredMixin, TemplateView):
    template_name = "pages/live.html"


class TransfersView(LoginRequiredMixin, TemplateView):
    template_name = "pages/transfers.html"


class DetailsView(LoginRequiredMixin, TemplateView):
    template_name = "pages/details.html"
