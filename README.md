# YaYa Wallet Webhook

A Django REST Framework implementation for handling YaYa Wallet webhook notifications with secure signature verification, async processing, and comprehensive testing.

## Features

- ✅ **Secure Webhook Verification**: HMAC SHA256 signature validation
- ✅ **Async Processing**: Celery-based background task processing
- ✅ **Duplicate Handling**: Idempotent webhook processing
- ✅ **IP Whitelisting**: Middleware for allowed IP validation
- ✅ **Comprehensive Testing**: test with Django test client
- ✅ **RESTful API**: Class-based views with Django REST Framework
- ✅ **Database Storage**: Persistent storage of webhook events
- ✅ **Error Handling**: Robust error handling and logging

## Installation

### Prerequisites

- Python 3.8+
- Django 3.2+
- Django REST Framework
- Redis (for Celery broker)
- PostgreSQL (recommended) or SQLite

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Elianamos29/yaya-webhook.git
   cd yaya-webhook
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**
   Create a `.env` file:
   ```bash
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   YAYA_WALLET_WEBHOOK_SECRET=your-webhook-secret-key
   DATABASE_URL=postgresql://user:password@localhost:5432/yaya_webhooks
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```
   
7. **Run celery**
   ```bash
   docker run -d -p 6379:6379 redis:alpine #start redis, Or install locally

   celery -A config worker --loglevel=info  # Basic worker
   ```

## Configuration

### YaYa Wallet Dashboard

1. Log in to your YaYa Wallet dashboard
2. Navigate to Webhooks section
3. Register your webhook endpoint: `https://yourdomain.com/webhooks/yaya-wallet/`
4. Set the same secret key in both dashboard and your `.env` file

### Allowed IPs

Configure allowed YaYa Wallet IPs in settings:
```python
YAYA_WALLET_ALLOWED_IPS = [
    '192.168.1.1',  # Replace with actual YaYa Wallet IPs
    '10.0.0.1',
]
```

## API Endpoints

### Webhook Endpoint
- **URL**: `/webhooks/yaya-wallet/`
- **Method**: POST
- **Headers**:
  - `Content-Type: application/json`
  - `YAYA-SIGNATURE: <hmac-signature>`


## Webhook Payload Example

```json
{
  "id": "1dd2854e-3a79-4548-ae36-97e4a18ebf81",
  "amount": 100,
  "currency": "ETB",
  "created_at_time": 1673381836,
  "timestamp": 1701272333,
  "cause": "Testing",
  "full_name": "Abebe Kebede",
  "account_name": "abebekebede1",
  "invoice_url": "https://yayawallet.com/en/invoice/xxxx"
}
```

## Signature Verification

The webhook signature is verified using HMAC SHA256 with your secret key. The signed payload is created by concatenating all values from the JSON payload in the order they appear.

Example signature generation:
```python
# Values are concatenated in order:
signed_payload = "1dd2854e-3a79-4548-ae36-97e4a18ebf81100ETB16733818361701272333TestingAbebe Kebedeabebekebede1https://yayawallet.com/en/invoice/xxxx"

# Signature is HMAC SHA256 of signed_payload using your secret key
signature = hmac.new(secret_key.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
```

## Async Processing

Webhooks are processed asynchronously using Celery:

1. Webhook received → Immediate 200 response
2. Event stored in database → Signature verified
3. Celery task triggered → Background processing
4. Business logic executed → Database updated

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test -v 2
```

### Manual Testing

Use the test script to send mock webhooks:
```bash
python scripts/send_test_webhook.py
```

## Project Structure

```
yaya-webhook/
├── webhooks/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── middleware.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── __init__.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scripts/
│   └── send_test_webhook.py
├── requirements.txt
├── manage.py
└── .env.example
```

## Security Considerations

### IP Whitelisting
Ensure only YaYa Wallet IPs can access your webhook endpoint by maintaining the `YAYA_WALLET_ALLOWED_IPS` list.

### Replay Attack Prevention
Webhook signatures include timestamps with a configurable tolerance period (default: 5 minutes) to prevent replay attacks.

## Error Handling

The system handles various error scenarios:
- Invalid JSON payloads → 400 Bad Request
- Missing signature header → 400 Bad Request
- Invalid signature → 400 Bad Request
- Duplicate events → 200 OK (idempotent)
- Server errors → 500 Internal Server Error

## Monitoring

Check webhook processing status via Django admin or database queries:
```python
from webhooks.models import WebhookEvent

# Get processed events
processed_events = WebhookEvent.objects.filter(processed=True)

# Get failed events
failed_events = WebhookEvent.objects.filter(processed=False)
```