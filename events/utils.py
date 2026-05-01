import uuid
import random
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

list_code = ['DX','TX','SX','MX','YX','AX']
random_code = random.choice(list_code)


def generate_ticket_code(event):
    code = f"TKX-{event.id}{str(uuid.uuid4().hex[:15]).upper()}"
    return code


def check_phone_Number(data):
    if data.startswith('0'):
        data = '+265' + data[1:]

    elif data.startswith('+265'):
        pass

    return data

def organizer_required(view_func):
    def wrapper(request,*args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        if not getattr(request.user,'is_organizer',False):
            return HttpResponseForbidden('<h1>You are not authorized to access this page</h1>')
        return view_func(request, *args, **kwargs)
    return wrapper
