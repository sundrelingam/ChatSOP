from django.urls import path
from .views import query

app_name = 'chat_app'

urlpatterns = [  
  path("chat/", query, name="chat")
]
