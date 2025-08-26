from uuid import UUID
from datetime import datetime, timezone
from django.test import TestCase, Client
from django.urls import reverse
import json
from unittest.mock import patch

from .models import WebhookEvent

class YayaWebhookTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('yaya-webhook-receiver')
        self.valid_payload = {
            "id": "1dd2854e-3a79-4548-ae36-97e4a18ebf81",
            "amount": 100,
            "currency": "ETB",
            "created_at_time": int(datetime.now(timezone.utc).timestamp()),
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "cause": "Test Payment",
            "full_name": "Test User",
            "account_name": "testuser",
            "invoice_url": "https://yayawallet.com/en/invoice/test123"
        }
        self.secret_key = "test-secret-key"

    def _generate_signature(self, payload):
        """Generate a valid signature for testing"""
        from .services import WebhookVerificationService
        service = WebhookVerificationService(self.secret_key)
        signed_payload = service.generate_signed_payload(payload)
        return service.generate_signature(signed_payload)

    def test_webhook_with_valid_signature(self):
        """Test webhook with valid signature"""
        signature = self._generate_signature(self.valid_payload)
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json',
            headers={'YAYA-SIGNATURE': signature}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WebhookEvent.objects.count(), 1)
        
        event = WebhookEvent.objects.first()
        
        self.assertEqual(event.event_id, UUID(self.valid_payload['id']))
        self.assertTrue(event.is_verified)

    def test_webhook_with_invalid_signature(self):
        """Test webhook with invalid signature"""
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json',
            headers={'YAYA-SIGNATURE': 'malformed-signature'}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(WebhookEvent.objects.count(), 0)

    def test_webhook_with_malformed_json(self):
        """Test webhook with invalid JSON"""
        response = self.client.post(
            self.webhook_url,
            data='invalid-json',
            content_type='application/json',
            headers={'YAYA-SIGNATURE': 'test-signature'}
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('webhooks.tasks.process_webhook_event.delay')
    def test_webhook_triggers_async_processing(self, mock_task):
        """Test that webhook triggers async processing"""
        signature = self._generate_signature(self.valid_payload)
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json',
            headers={'YAYA-SIGNATURE': signature}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_task.called)
        
        event = WebhookEvent.objects.first()
        mock_task.assert_called_with(event.id)
