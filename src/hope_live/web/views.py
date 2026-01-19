import calendar
from datetime import date, timedelta
from typing import Any

from django.core.cache import cache
from django.db.models import Count, Q, Sum, Value
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from hope_live.models import BusinessArea, HopeProgram, Payment
from hope_live.utils.cache import DashboardCache


class ContactView(TemplateView):
    template_name = "pages/contacts.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


class IndexView(TemplateView):
    template_name = "pages/index.html"


class DashboardView(TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        current_year = timezone.now().year

        payments = Payment.objects.all()

        successful_statuses = [
            "Distribution Successful",
            "Partially Distributed",
            "Transaction Successful",
        ]

        successful_payments = payments.filter(status__in=successful_statuses)

        pending_statuses = ["Sent to Payment Gateway", "Sent to FSP", "Pending"]
        pending_payments = payments.filter(status__in=pending_statuses)

        total_delivered_usd = successful_payments.aggregate(total=Sum("delivered_quantity_usd"))["total"] or 0

        total_pending_usd = pending_payments.aggregate(total=Sum("entitlement_quantity_usd"))["total"] or 0

        total_payments_count = payments.count()
        successful_payments_count = successful_payments.count()
        pending_payments_count = pending_payments.count()

        business_areas = BusinessArea.objects.filter(active=True)

        programs = HopeProgram.objects.filter(status="Active")[:10]

        current_year_payments = payments.filter(delivery_date__year=current_year)
        current_year_total = current_year_payments.aggregate(total=Sum("delivered_quantity_usd"))["total"] or 0

        context.update(
            {
                "total_delivered_usd": total_delivered_usd,
                "total_pending_usd": total_pending_usd,
                "total_payments_count": total_payments_count,
                "successful_payments_count": successful_payments_count,
                "pending_payments_count": pending_payments_count,
                "business_areas": business_areas,
                "programs": programs,
                "current_year": current_year,
                "current_year_total": current_year_total,
            }
        )

        return context


class PaymentAggregatesView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        business_area = request.GET.get("business_area")

        end_date = date.today() if not end_date_str else date.fromisoformat(end_date_str)
        start_date = end_date - timedelta(days=730) if not start_date_str else date.fromisoformat(start_date_str)

        cache_key = DashboardCache.get_key("aggregates", start=start_date, end=end_date, area=business_area)
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data, safe=False)

        date_q = (
            Q(delivery_date__range=[start_date, end_date])
            | Q(entitlement_date__range=[start_date, end_date])
            | Q(status_date__range=[start_date, end_date])
        )

        queryset = Payment.objects.filter(
            date_q,
            is_removed=False,
            conflicted=False,
        )

        if business_area:
            queryset = queryset.filter(business_area__slug=business_area)

        queryset = queryset.select_related(
            "program", "business_area", "delivery_type", "financial_service_provider"
        ).annotate(
            payment_date=Coalesce("delivery_date", "entitlement_date", "status_date"),
            business_area_name=Coalesce("business_area__name", "Unknown Country"),
            region_name=Coalesce("business_area__region_name", "Unknown Region"),
            program_name=Coalesce("program__name", "Unknown Program"),
            sector_name=Coalesce("program__sector", "Unknown Sector"),
            delivery_type_name=Coalesce("delivery_type__name", "Unknown Delivery Type"),
            fsp_name=Coalesce("financial_service_provider__name", "Unknown FSP"),
            currency_code=Coalesce("currency", "UNK"),
        )

        payments = queryset.values(
            "id",
            "payment_date",
            "status",
            "delivered_quantity_usd",
            "delivered_quantity",
            "entitlement_quantity_usd",
            "business_area_name",
            "region_name",
            "program_name",
            "sector_name",
            "delivery_type_name",
            "fsp_name",
            "currency_code",
        ).order_by("payment_date")

        data = []
        for payment in payments:
            payment_date = payment["payment_date"]

            data.append(
                {
                    "id": str(payment["id"]),
                    "payment_date": payment_date.isoformat() if payment_date else None,
                    "business_area": payment["business_area_name"],
                    "region": payment["region_name"],
                    "program": payment["program_name"],
                    "sector": payment["sector_name"],
                    "status": payment["status"],
                    "delivery_type": payment["delivery_type_name"],
                    "fsp": payment["fsp_name"],
                    "currency": payment["currency_code"],
                    "delivered_quantity_usd": float(payment["delivered_quantity_usd"] or 0),
                    "delivered_quantity": float(payment["delivered_quantity"] or 0),
                    "entitlement_quantity_usd": float(payment["entitlement_quantity_usd"] or 0),
                }
            )

        cache.set(cache_key, data, DashboardCache.TTL)

        return JsonResponse(data, safe=False)


class DashboardDataView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        business_area_slug = request.GET.get("business_area")

        cache_key = DashboardCache.get_key("dashboard_data", area=business_area_slug)
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data, safe=False)

        queryset = Payment.objects.filter(
            is_removed=False,
            conflicted=False,
        )

        if business_area_slug:
            queryset = queryset.filter(business_area__slug=business_area_slug)

        queryset = queryset.select_related(
            "program", "business_area", "delivery_type", "financial_service_provider"
        ).annotate(
            year=ExtractYear(Coalesce("delivery_date", "entitlement_date", "status_date")),
            month=ExtractMonth(Coalesce("delivery_date", "entitlement_date", "status_date")),
            business_area_name=Coalesce("business_area__name", "Unknown Country"),
            region_name=Coalesce("business_area__region_name", "Unknown Region"),
            program_name=Coalesce("program__name", "Unknown Program"),
            sector_name=Coalesce("program__sector", "Unknown Sector"),
            delivery_type_name=Coalesce("delivery_type__name", "Unknown Delivery Type"),
            fsp_name=Coalesce("financial_service_provider__name", "Unknown FSP"),
            currency_code=Coalesce("currency", "UNK"),
            admin1_name=Value("Unknown Admin1"),
        )

        aggregates = queryset.values(
            "year",
            "month",
            "business_area_name",
            "region_name",
            "program_name",
            "sector_name",
            "status",
            "delivery_type_name",
            "fsp_name",
            "currency_code",
            "admin1_name",
        ).annotate(
            payment_count=Count("id"),
            total_delivered_quantity_usd=Sum("delivered_quantity_usd"),
            total_delivered_quantity=Sum("delivered_quantity"),
            total_entitlement_quantity_usd=Sum("entitlement_quantity_usd"),
        )

        data = []
        for agg in aggregates:
            month_name = "Unknown"
            if agg["month"] and 1 <= agg["month"] <= 12:  # noqa: PLR2004
                month_name = calendar.month_name[agg["month"]]

            data.append(
                {
                    "total_delivered_quantity_usd": float(agg["total_delivered_quantity_usd"] or 0),
                    "total_delivered_quantity": float(agg["total_delivered_quantity"] or 0),
                    "payments": agg["payment_count"],
                    "individuals": 0,
                    "households": 0,
                    "children_counts": 0,
                    "pwd_counts": 0,
                    "reconciled": 0,
                    "finished_payment_plans": 0,
                    "total_payment_plans": 0,
                    "year": agg["year"],
                    "month": month_name,
                    "program": agg["program_name"],
                    "sector": agg["sector_name"],
                    "status": agg["status"],
                    "fsp": agg["fsp_name"],
                    "delivery_types": agg["delivery_type_name"],
                    "currency": agg["currency_code"],
                    "admin1": agg["admin1_name"],
                    "country": agg["business_area_name"],
                    "region": agg["region_name"],
                    "total_planned_usd": float(agg["total_entitlement_quantity_usd"] or 0),
                }
            )

        cache.set(cache_key, data, DashboardCache.TTL)

        return JsonResponse(data, safe=False)


class LiveView(TemplateView):
    template_name = "pages/live.html"


class TransfersView(TemplateView):
    template_name = "pages/transfers.html"


class DetailsView(TemplateView):
    template_name = "pages/details.html"
