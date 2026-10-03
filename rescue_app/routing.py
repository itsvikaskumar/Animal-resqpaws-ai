from django.urls import re_path
from .consumers import AmbulanceTrackingConsumer

websocket_urlpatterns = [
    re_path(
        r"^ws/rescue/track/(?P<tracking_id>[^/]+)/$",
        AmbulanceTrackingConsumer.as_asgi(),
    ),
]