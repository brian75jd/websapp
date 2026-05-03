from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from events.forms import ValidateEventCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from events.models import Event,TicketType
from django.views.decorators.csrf import ensure_csrf_cookie
from events.utils import organizer_required
from django.contrib.auth import logout
from django.conf import settings
from django.core.files.storage import default_storage

User = get_user_model()

def Events(request):
    return render(request,template_name='pages/events.html')

def Loggin(request):
    return render(request,template_name='pages/login.html')

@organizer_required
@ensure_csrf_cookie
def verify_ticket(request, code):
   return render(request, 'pages/qr_scanner.html',{'code':code}) 

def Tickets(request,event_id): 
    return render(request,'pages/tickets.html',{'event_id':event_id})

def organizers(request):
    return render(request,template_name='organizer.html')

def create_User_account(request):
    return render(request,template_name='pages/createuser.html')

def ticket_await(request):
    tx_ref = request.GET.get('tx_ref')
    return render(request,'pages/await_ticket.html',{'tx_ref':tx_ref})


@login_required
def Dashboard(request):
    user = request.user
    if not user.is_organizer:
        return redirect('events:events')
    return render(request,template_name='pages/dashboard.html')


from django.db import transaction

@login_required
@require_POST
def Create_Event(request):
    form = ValidateEventCreationForm(request.POST, request.FILES)

    if form.is_valid():
        data = form.cleaned_data

        try:
            with transaction.atomic():

                event = Event.objects.create(
                    title=data.get('title'),
                    description=data.get('description'),
                    event_type=data.get('event_type'),
                    location=data.get('location'),
                    start_datetime=data.get('start_datetime'),
                    end_datetime=data.get('end_datetime'),
                    poster=data.get('poster'),
                    is_paid=True if request.POST.get('is_paid') == 'on' else False,
                    created_by=request.user,
                    organizer=request.user
                )


            
                if request.POST.get('enable_vip') == 'on':
                    TicketType.objects.create(
                        event=event,
                        type=TicketType.TypeChoices.VIP,
                        price=data.get('vip_price') or 0,
                        capacity=data.get('vip_capacity') or 0
                    )

                
                if request.POST.get('enable_standard') == 'on':
                    TicketType.objects.create(
                        event=event,
                        type=TicketType.TypeChoices.STANDARD,
                        price=data.get('standard_price') or 0,
                        capacity=data.get('standard_capacity') or 0
                    )

                # REGULAR
                if request.POST.get('enable_regular') == 'on':
                    TicketType.objects.create(
                        event=event,
                        type=TicketType.TypeChoices.REGULAR,
                        price=data.get('regular_price') or 0,
                        capacity=data.get('regular_capacity') or 0
                    )

            return JsonResponse({
                'success': True,
                'message': 'Event created successfully 🎉'
            })

        except Exception as e:
            print("SAVE ERROR:", e)
            return JsonResponse({
                'success': False,
                'detail': 'Error creating event'
            }, status=500)
    errors = {field: error[0] for field, error in form.errors.items()}

    if form.non_field_errors():
        errors['__all__'] = form.non_field_errors()[0]

    return JsonResponse({
        'success': False,
        'errors': errors
    }, status=400)

@login_required
def LogoutUser(request):
    logout(request)
    return redirect('/')



