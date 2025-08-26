from rest_framework import serializers

from .models import WebhookEvent

class WebhookPayloadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='ETB')
    created_at_time = serializers.IntegerField()
    timestamp = serializers.IntegerField()
    cause = serializers.CharField(max_length=255)
    full_name = serializers.CharField(max_length=255)
    account_name = serializers.CharField(max_length=100)
    invoice_url = serializers.URLField()

class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = '__all__'
        read_only_fields = ('received_at', 'processed', 'is_verified')