from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def AppSettings(request):
    return render(request,'pages/settings.html')