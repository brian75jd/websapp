from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from APIS.serializers import MatchSerializer
from APIS.models import Match
from APIS.authentication import APIClientAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes
from APIS.models import APIClient,Vacancy
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
import json


#Template rendering functions

@login_required
def vacancy_view(request,vac_id):
    vacancy = Vacancy.objects.get(id=vac_id)
    data = {
        'id':vacancy.id,
        'position':vacancy.position,
        'location':vacancy.location,
        'description':vacancy.description,
        'salary': vacancy.salary if vacancy.salary else 0.00,
        'email': vacancy.email if vacancy.email else "None",
        'organization':vacancy.organization,
        'type':f"{vacancy.type} time",
        'dead_line': vacancy.dead_line.strftime('%Y-%m-%d'),
        'date_posted':vacancy.date_posted.strftime('%Y-%m-%d')
    }
    return render(request,'pages/vacancy.html',{'data_json':json.dumps(data)})
    










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


class VacancyManager(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args, **kwargs):
        try:
            vacancies = Vacancy.objects.all()
            data = []

            for vacancy in vacancies:
                data.append({
                    'id':vacancy.id,
                    'role':vacancy.position,
                    'date_posted':vacancy.date_posted.strftime('%Y-%m-%d'),
                    'deadline':vacancy.dead_line.strftime('%Y-%m-%d'),
                    'description':vacancy.description,
                    'is_valid': vacancy.check_validity,
                    'location':vacancy.location,
                    'pay':vacancy.salary if vacancy.salary else "Not set",
                    'type':vacancy.type,
                    'org': vacancy.organization if vacancy.organization else 'NICO'
                })
            
            return Response({
                'data':data,
                'success':True,
            })
        
        except Exception as exp:
            return Response({
                'detail':str(exp),
                'success':False,
            })

            
