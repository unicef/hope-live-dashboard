from django.urls import path

from hope_live.ws.views import callback

app_name = "ws"

urlpatterns = [
    path("notify", callback, name="notify"),
]
