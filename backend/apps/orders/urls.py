from django.urls import path

from .webhook import WebhookView

urlpatterns = [
    path("webhook/", WebhookView.as_view(), name="webhook"),
]
