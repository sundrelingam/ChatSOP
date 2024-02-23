from django.urls import path
from .views import upload, vectorstore

app_name = 'uploads_app'

urlpatterns = [
  path("upload/", upload, name="upload"),
  path("vectorstore/", vectorstore, name="vectorstore")
]
