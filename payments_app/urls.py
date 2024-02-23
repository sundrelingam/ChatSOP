from django.urls import path
from . import views

app_name = 'payments_app'

urlpatterns = [
  path("plan/", views.PlanView.as_view(), name="plan"),
  path('plan/config/', views.stripe_config),
  path('plan/create-checkout-session/', views.create_checkout_session),
  path('success/', views.SuccessView.as_view(), name="success"),
  path('cancelled/', views.CancelledView.as_view()),
  path('deactivate/', views.cancel_subscription, name="deactivate"),
  path('webhook/', views.stripe_webhook),
]
