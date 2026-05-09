from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authuser.utils import normal_user_required
from APIS.models import APIClient

@login_required
#@normal_user_required
def UserFeed(request):
    if request.user.is_organizer:
        return redirect('/')
    try:
        client = APIClient.objects.get(user=request.user)
    except APIClient.DoesNotExist:
        client = {}
    return render(request,'pages/users.html',{'apiclient':client})