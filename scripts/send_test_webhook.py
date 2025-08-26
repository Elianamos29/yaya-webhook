import requests
import json
import hmac
import hashlib
from datetime import datetime, timezone

def send_test_webhook():
    payload = {
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
    
    secret_key = "test-secret-key"
    signed_payload = ''.join(str(v) for v in payload.values()).encode('utf-8')
    signature = hmac.new(
        secret_key.encode('utf-8'),
        signed_payload,
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'YAYA-SIGNATURE': signature
    }
    
    response = requests.post(
        'http://localhost:8000/webhooks/yaya-wallet/',
        data=json.dumps(payload),
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    send_test_webhook()