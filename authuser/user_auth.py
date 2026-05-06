from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.decorators import permission_classes,api_view
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

def do_nothing():
    pass

@login_required
@api_view(['POST'])
def EditPassword(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not user.check_password(old_password):
       return JsonResponse({'detail':'Invalid user password','success':False},status=400)
    
    try:
        validate_password(new_password,user)
    
    except ValidationError as e:
        return Response({'detail':str(e.messages[0]),'success':False},status=400)
    
    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request,user)

    return JsonResponse({'success':True,'detail':'Password updated'},status=200)

@login_required
@api_view(['POST'])
def UpdateOrganizerInfo(request):
    user_id = request.user.id
    try:
        name = request.data.get('name')
        email = request.data.get('email')
        bio = request.data.get('bio')

        user = User.objects.get(id=user_id)
        user.name = name if name else do_nothing()
        user.username = name if name else do_nothing()
        user.bio = bio if bio else do_nothing()
        user.email = email if email else do_nothing()
        user.save()
        return JsonResponse({'success':True,'detail':'User details updated'},status=200)
    
    except Exception as exp:
        return JsonResponse({'success':False,'detail':str(exp)},status=400)


