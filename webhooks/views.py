from rest_framework.views import APIView
from rest_framework.response import Response

class WebhookReceiver(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        print("Received webhook data:", data)
        
        return Response({"status": "success", "message": "Webhook received"}, status=200)