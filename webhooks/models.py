from django.db import models

class WebhookEvent(models.Model):
    EVENT_TYPES = [
        ('payment_confirmed', 'Payment Confirmed'),
        ('payment_received', 'Payment Received'),
        ('recurring_payment', 'Recurring Payment'),
        ('subscription_payment', 'Subscription Payment'),
    ]
    
    event_id = models.UUIDField(unique=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')
    created_at_time = models.BigIntegerField()
    timestamp = models.BigIntegerField()
    cause = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    account_name = models.CharField(max_length=100)
    invoice_url = models.URLField()
    signature = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.amount} {self.currency}"