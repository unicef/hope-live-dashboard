from django.views.generic import TemplateView


class ContactView(TemplateView):
    template_name = "pages/contacts.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


class IndexView(TemplateView):
    template_name = "pages/index.html"


class DashboardView(TemplateView):
    template_name = "pages/dashboard.html"


class LiveView(TemplateView):
    template_name = "pages/live.html"


class TransfersView(TemplateView):
    template_name = "pages/transfers.html"


class DetailsView(TemplateView):
    template_name = "pages/details.html"
