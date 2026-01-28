from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from hope_live.web import views

app_name = "web"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="index"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("logout/confirm/", views.LogoutConfirmView.as_view(), name="logout_confirm"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/data/", views.PaymentAggregatesView.as_view(), name="dashboard_data"),
    path("dashboard/api/", views.DashboardDataView.as_view(), name="dashboard_api"),
    path("details/", views.DetailsView.as_view(), name="details"),
    path("transfers/", views.TransfersView.as_view(), name="transfers"),
    path("live/", views.LiveView.as_view(), name="live"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contacts/", views.ContactView.as_view(), name="contacts"),
]
