from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from APIS.serializers import MatchSerializer
from APIS.models import Match
from APIS.authentication import APIClientAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.decorators import parser_classes, authentication_classes



class Sports_Update(APIView):
    #authentication_classes =[APIClientAuthentication]
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
            print(exp)
            return Response({''
            'success':False,
            'error':str(exp)},status=status.HTTP_400_BAD_REQUEST)
            
