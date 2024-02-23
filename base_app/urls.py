from django.urls import path
from .views import SignUpView, IndexView, ProfileView
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'base_app'

urlpatterns = [  
  path("", IndexView.as_view(), name="index"),

  path(
    "login/",
    LoginView.as_view(
      # name of the login template
      template_name="base_app/login.html",
      # user will be redirected to index page upon successful login
      next_page="uploads_app:upload",
      redirect_authenticated_user=True,
    ),
    name="login",
  ),  
  
  path(
    "logout/",
    # user will be redirected to index page upon logout
    LogoutView.as_view(next_page="base_app:index"),
    name="logout",
  ),

  path("signup/", SignUpView.as_view(), name="signup"),
  
  path("profile/", ProfileView.as_view(), name="profile")
]
