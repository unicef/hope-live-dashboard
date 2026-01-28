from django.urls import path

from .views import DashboardStatsAPIView, DashboardTotalsAPIView

app_name = "analysis"

urlpatterns = [
    path("stats/", DashboardStatsAPIView.as_view(), name="stats"),
    path("totals/", DashboardTotalsAPIView.as_view(), name="totals"),
]
