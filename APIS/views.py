from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from APIS.serializers import MatchSerializer
from APIS.models import Match
from APIS.authentication import APIClientAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes
from APIS.models import APIClient
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated


@login_required
def developer_page(request):
    try:
        client = APIClient.objects.get(user=request.user)
    except APIClient.DoesNotExist:
        client = APIClient.objects.create(user=request.user)
    
    return render(request, 'pages/developer.html', {
        'api_key': client.api_key if client.api_key else "",
        'secret_key': client.secret_key if client.api_key else "",
    })

class Sports_Update(APIView):
    authentication_classes =[APIClientAuthentication]
    def get(self,request,*args, **kwargs):
        try:
            queryset = Match.objects.select_related('league') \
                        .all()
            
            serializer = MatchSerializer(queryset,many=True).data
            return Response({
                'success':True,
                'data':serializer
            },status=status.HTTP_200_OK)
        
        except Exception as exp:
            return Response({''
            'success':False,
            'error':str(exp)},status=status.HTTP_400_BAD_REQUEST)

class App_Sports_Update(APIView):
    permission_classes =[IsAuthenticated]
    def get(self,request,*args, **kwargs):
        try:
            queryset = Match.objects.select_related('league') \
                        .all()
            
            serializer = MatchSerializer(queryset,many=True).data
            return Response({
                'success':True,
                'data':serializer
            },status=status.HTTP_200_OK)
        
        except Exception as exp:
            return Response({''
            'success':False,
            'error':str(exp)},status=status.HTTP_400_BAD_REQUEST)

            
