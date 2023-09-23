from apps.webhook.webhook import WebhookView
from django.urls import path

urlpatterns = [
    path("webhook/", WebhookView.as_view(), name="webhook"),
]
