from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from APIS.models import APIClient

class APIClientAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.GET.get('Authorization')
        secret_key = request.headers.get('X-SECRET_KEY')

        if not authorization:
            raise AuthenticationFailed(
                'Authorization token is required'
            )
        
        try:
            client = APIClient.objects.get(
                api_key = authorization
            )
        
        except APIClient.DoesNotExist:
            raise AuthenticationFailed(
                'Invalid API credentials'
            )
        
        return (client,None)