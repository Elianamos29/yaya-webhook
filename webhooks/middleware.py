from django.conf import settings
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)

class IPWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/webhooks/yaya-wallet/'):
            client_ip = self.get_client_ip(request)
            
            if client_ip not in settings.YAYA_WALLET_ALLOWED_IPS:
                logger.warning(f"Blocked webhook request from unauthorized IP: {client_ip}")
                return HttpResponseForbidden("IP not allowed")
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip