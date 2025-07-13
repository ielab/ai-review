# Import
from django.urls import re_path  
from . import views  
  
# Websocket
websocket_urlpatterns = [  
    re_path(r"^ws/chat/(?P<user_id>[a-zA-Z0-9]+)/(?P<review_id>[a-zA-Z0-9]+)/$", views.ChatConsumer.as_asgi()),  
]