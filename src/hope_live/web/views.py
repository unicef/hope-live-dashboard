from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "index.html"


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class LiveView(TemplateView):
    template_name = "live.html"


class TransfersView(TemplateView):
    template_name = "transfers.html"


class DetailsView(TemplateView):
    template_name = "details.html"
