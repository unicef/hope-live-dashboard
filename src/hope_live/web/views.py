from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView, TemplateView


class ContactView(TemplateView):
    template_name = "pages/contacts.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


class IndexView(RedirectView):
    pattern_name = "web:dashboard"


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


class LiveView(LoginRequiredMixin, TemplateView):
    template_name = "pages/live.html"


class TransfersView(LoginRequiredMixin, TemplateView):
    template_name = "pages/transfers.html"


class DetailsView(LoginRequiredMixin, TemplateView):
    template_name = "pages/details.html"
