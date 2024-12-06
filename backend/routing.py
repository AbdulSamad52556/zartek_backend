from django.urls import re_path
from api.consumers import RideNotificationConsumer, RideTrackingConsumer

websocket_urlpatterns = [
    re_path(r'ws/ride_notifications/(?P<driver_id>\d+)/$', RideNotificationConsumer.as_asgi()),
    re_path(r'ws/ride-tracking/(?P<ride_id>\d+)/$', RideTrackingConsumer.as_asgi()),

]
