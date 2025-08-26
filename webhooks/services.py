import hmac
import hashlib
import time

from django.conf import settings
from django.core.exceptions import ValidationError

class WebhookVerificationService:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or settings.YAYA_WEBHOOK_SECRET_KEY
    
    def generate_signed_payload(self, payload):
        values = [
            str(payload.get('id', '')),
            str(payload.get('amount', '')),
            str(payload.get('currency', '')),
            str(payload.get('created_at_time', '')),
            str(payload.get('timestamp', '')),
            str(payload.get('cause', '')),
            str(payload.get('full_name', '')),
            str(payload.get('account_name', '')),
            str(payload.get('invoice_url', ''))
        ]
    
        signed_payload = "".join(values)
        return signed_payload.encode('utf-8')
    
    def generate_signature(self, signed_payload):
        return hmac.new(
            self.secret_key.encode('utf-8'),
            signed_payload,
            hashlib.sha256
        ).hexdigest()
    
    def verify_signature(self, received_signature, payload, tolerance=300):
        current_time = int(time.time())
        payload_timestamp = int(payload.get('timestamp', 0))
        if abs(current_time - payload_timestamp) > tolerance:
            raise ValidationError("Payload timestamp is outside the allowed tolerance.")
        
        signed_payload = self.generate_signed_payload(payload)
        expected_signature = self.generate_signature(signed_payload)

        return hmac.compare_digest(expected_signature, received_signature)