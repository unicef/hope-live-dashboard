from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("details/", views.DetailsView.as_view(), name="details"),
    path("transfers/", views.TransfersView.as_view(), name="transfers"),
    path("live/", views.LiveView.as_view(), name="live"),
]
