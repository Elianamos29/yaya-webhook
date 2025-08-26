from django.urls import path

from .views import WebhookReceiver

urlpatterns = [
    path('webhooks/yaya-wallet/', WebhookReceiver.as_view(), name='yaya-webhook-receiver'),
]