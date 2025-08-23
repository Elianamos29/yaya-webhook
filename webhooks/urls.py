from django.urls import path

from .views import WebhookReceiver

urlpatterns = [
    path('webhook/', WebhookReceiver.as_view(), name='webhook_receiver'),
]