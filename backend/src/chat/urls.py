# Import
from django.urls import path  
from . import views  
  
# URL
urlpatterns = [  
    path('ws/chat/', views.ChatConsumer.as_asgi()),  
]