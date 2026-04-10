from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def ChatView(request):
    return render(request,'messages/chats.html',{})

@login_required
def Chat_List(request):
    return render(request,'messages/chat_list.html')