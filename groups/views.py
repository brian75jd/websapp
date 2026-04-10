from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def GroupView(request):
    return render(request,'pages/groups.html')
