from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

import json
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import WebhookEvent
from .serializers import WebhookPayloadSerializer
from .services import WebhookVerificationService
from .tasks import process_webhook_event

logger = logging.getLogger(__name__)

class WebhookReceiver(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            signature = request.headers.get('YAYA-SIGNATURE')
            if not signature:
                return self._error_response("Missing YAYA-SIGNATURE header", status.HTTP_400_BAD_REQUEST)
            
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                return self._error_response("Invalid JSON payload", status.HTTP_400_BAD_REQUEST)
            
            serializer = WebhookPayloadSerializer(data=payload)
            if not serializer.is_valid():
                return self._error_response("Invalid payload data", status.HTTP_400_BAD_REQUEST, details=serializer.errors)
            
            verification_service = WebhookVerificationService()
            try:
                is_valid = verification_service.verify_signature(signature, payload)
            except Exception as e:
                logger.warning(f"Signature verification failed: {str(e)}")
                return self._error_response(str(e), status.HTTP_400_BAD_REQUEST)
            
            if not is_valid:
                return self._error_response("Invalid signature", status.HTTP_400_BAD_REQUEST)
            
            event_id = payload['id']
            if WebhookEvent.objects.filter(event_id=event_id).exists():
                logger.info(f"Webhook event {event_id} already processed, returning success")
                return Response({'status': 'success', 'message': 'Event already processed'}, status=status.HTTP_200_OK)
            
            webhook_event = self._create_webhook_event(payload, signature)

            self._process_webhook_async(webhook_event.id)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return self._error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _create_webhook_event(self, payload, signature):
        return WebhookEvent.objects.create(
            event_id=payload['id'],
            event_type=self._determine_event_type(payload),
            amount=payload['amount'],
            currency=payload.get('currency', 'ETB'),
            created_at_time=payload['created_at_time'],
            timestamp=payload['timestamp'],
            cause=payload['cause'],
            full_name=payload['full_name'],
            account_name=payload['account_name'],
            invoice_url=payload['invoice_url'],
            signature=signature,
            is_verified=True
        )
    
    def _determine_event_type(self, payload):
        cause = payload.get('cause', '').lower()
        if 'confirmed' in cause:
            return 'payment_confirmed'
        elif 'received' in cause:
            return 'payment_received'
        elif 'recurring' in cause:
            return 'recurring_payment'
        elif 'subscription' in cause:
            return 'subscription_payment'
        return 'payment_received'
    
    def _process_webhook_async(self, webhook_event_id):
        process_webhook_event.delay(webhook_event_id)

    def _error_response(self, message, status_code, details=None):
        error_response = {'error': message}
        if details:
            error_response['details'] = details
        return Response(error_response, status=status_code)
