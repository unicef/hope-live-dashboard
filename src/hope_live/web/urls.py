from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "web"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("login/", LoginView.as_view(template_name="pages/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="web:index"), name="logout"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("demographic/", views.DemographicView.as_view(), name="demographic"),
    path("completion/", views.CompletionView.as_view(), name="completion"),
    path("details/", views.DetailsView.as_view(), name="details"),
    path("transfers/", views.TransfersView.as_view(), name="transfers"),
    path("grievance/", views.GrievanceView.as_view(), name="grievance"),
    path("risk/", views.RiskView.as_view(), name="risk"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contacts/", TemplateView.as_view(template_name="pages/contacts.html"), name="contacts"),
]
