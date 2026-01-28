from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.generic import TemplateView

from hope_live.models import BusinessArea


class ContactView(TemplateView):
    template_name = "pages/contacts.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["business_areas"] = BusinessArea.objects.filter(active=True)
        return context


class PaymentAggregatesView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse([], safe=False)


class DashboardDataView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse([], safe=False)


class LiveView(LoginRequiredMixin, TemplateView):
    template_name = "pages/live.html"


class TransfersView(LoginRequiredMixin, TemplateView):
    template_name = "pages/transfers.html"


class DetailsView(LoginRequiredMixin, TemplateView):
    template_name = "pages/details.html"


class LogoutConfirmView(LoginRequiredMixin, TemplateView):
    template_name = "pages/logout_confirm.html"
