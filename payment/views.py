from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes

@method_decorator(csrf_exempt, name='dispatch')
class Payment_Webhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        print(request.GET)
        print("🔥 GET HIT")
        print(request.GET.get('tx_ref'))
        return Response({"message": "GET received"})

    def post(self, request, *args, **kwargs):
        print("🔥 POST HIT")
        print(request.data)
        return Response({"message": "POST received"})