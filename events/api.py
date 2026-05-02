from django.http import JsonResponse
from django.views.decorators.http import require_GET
from events.models import (Event, Ticket,TicketType,Question)
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from events.utils import generate_ticket_code
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
import requests
from django.conf import settings


User = get_user_model()

success_status = status.HTTP_200_OK
bad_request_status = status.HTTP_400_BAD_REQUEST

@require_GET
def GetEvents(request):
    events = Event.objects.prefetch_related('ticket_types').all().order_by('-created_at')
    data = []

    for event in events:
        total_left = sum(t.tickets_left() for t in event.ticket_types.all())
        data.append({
            'id':event.id,
            'title':event.title,
            'desc':event.description,
            'type':event.event_type,
            'venue':event.location,
            'date':str(event.event_date),
            'start_at':event.start_time.strftime('%H:%M'),
            'finish_at':event.finish_time.strftime('%H:%M'),
            'is_paid':event.is_paid,
            'poster':event.poster.url,
            'organizers':'Ecom',
            'seeds':['tom','james','emily'],
            'thumbnail':event.thumbnail.url if event.thumbnail else "",
            'tickets_left': total_left
        })
    
    return JsonResponse({'events':data})



class Verify_Ticket(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):   
        qr_code = request.POST.get('qr_code')

        if not qr_code:
            return Response({'status': 'error', 'message': 'Missing QR'},
                             status= status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                ticket = Ticket.objects.select_related('event', 'ticket_type')\
                                    .select_for_update()\
                                    .get(qr_code=qr_code)

                if ticket.is_used:
                    return Response({
                        'status': 'used',
                        'message': 'Already used ',
                        'event': ticket.event.title,
                        'type': ticket.ticket_type.type,
                        'ticket_code': ticket.ticket_code,
                    },status=status.HTTP_400_BAD_REQUEST)

                ticket.is_used = True
                ticket.verified_by = request.user
                ticket.save(update_fields=['is_used','verified_by'])

                return Response({
                    'status': 'valid',
                    'message': 'Access granted ✅',
                    'event': ticket.event.title,
                    'type': ticket.ticket_type.type,
                    'ticket_code': ticket.ticket_code,
                    'holder': ticket.verified_by.username
                },status=success_status)

        except Ticket.DoesNotExist:
            return Response({
                'status': 'invalid',
                'message': 'Invalid ticket ❌'
            }, status=status.HTTP_404_NOT_FOUND)


class Get_EventId(APIView):

    def get(self,request, event_id):
        try:
            event = get_object_or_404(Event.objects.prefetch_related('ticket_types__tickets'), id=event_id)


            total_left = sum([t.tickets_left() for t in event.ticket_types.all()])

            ticket_types_data = []

            if event.is_paid:
                for t in event.ticket_types.all():
                    ticket_types_data.append({
                        'label': t.type.capitalize(),
                        'type': t.type,                
                        'price': t.price,
                        'left': t.tickets_left(),
                        'soldOut': t.tickets_left() == 0
                    })
            else:
                ticket_types_data.append({
                    'label': 'Free Entry',
                    'type': 'free',
                    'price': 0,
                    'left': total_left,
                    'soldOut': total_left == 0
                })

            data = [{
                'id': event.id,
                'title': event.title,
                'desc': event.description,
                'category': event.event_type,
                'venue': event.location,

                'startTime': event.start_time.strftime('%I:%M %p'),
                'endTime': event.finish_time.strftime('%I:%M %p'),
                'date': str(event.event_date),

                'poster': event.poster.url if event.poster else "",
                'soldOut': total_left == 0,
                'src': event.thumbnail.url if event.thumbnail else "",

                'ticketTypes': ticket_types_data,

                'totalSeats': total_left,
                'seatsLeft': total_left,

                # UI styling
                'catLabel': event.event_type.capitalize(),
                'catBg': '#fee2e2',
                'catText': '#7f1d1d',
                'accent': '#ef4444',
            }]

            return Response({'events': data},status=success_status)

        except Exception as exp:
            return Response({'detail': str(exp)}, bad_request_status)
    

class Buy_Tickets(APIView):
    
    def post(self, request,*args, **kwargs):
        import uuid
        event_id = request.POST.get('event_id')
        ticket_type_value = request.POST.get('ticket_type', '').lower()
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            return Response({'error': 'Invalid quantity'}, status=400)

        if not event_id or not ticket_type_value:
            return Response({'error': 'Missing event_id or ticket_type'}, status=400)

        try:
            event = Event.objects.get(pk=event_id)
            ticket_type = TicketType.objects.get(event=event, type=ticket_type_value)
            amount = ticket_type.price * quantity
        except (Event.DoesNotExist, TicketType.DoesNotExist):
            return Response({'error': 'Event or ticket type not found'}, status=404)

        tx_ref = uuid.uuid4().hex[:16]   # Make it a bit longer for safety

        url = "https://api.paychangu.com/payment"

        payload = {
            "amount": f"{amount}",                    # ← Send as number, not string
            "currency": "MWK",
            "tx_ref": tx_ref,
            "first_name": "Brian",
            "last_name": "Bingala",
            'meta':[],
            "email": "brian75jd@gmail.com",
            "callback_url": "https://websapp.up.railway.app/await-ticket/", 
            "webhook_url": "https://websapp.up.railway.app/payment/webhook",
            "webhook_url": "https://websapp.up.railway.app/payment/api/webhook",   
            "customization": {
                "title": "Ticket Payment",
                "description": f"{quantity} ticket(s) for {event.title}"
            }
        
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {settings.PAYCHANGU_SECRET_KEY}"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()

            if data.get('status') == 'success':
            
                checkout_url = data.get('data', {}).get('checkout_url') or data.get('data', {}).get('link')
                if checkout_url:
                   
                    return Response({
                        'success': True,
                        'checkout_url': checkout_url,
                        'tx_ref': tx_ref
                    })

            
            return Response({
                'success': False,
                'error': data.get('message') or data.get('error') or str(data)
            }, status=400)

        except requests.exceptions.RequestException as e:
            return Response({'success': False, 'error': f'Network error'}, status=500)


class HandleQuestions(APIView):
    def post(self,request):
        try:
            json_data = []
            data = request.data
            event_id = data.get('eventId')
            questions = Question.objects.filter(
                event__id = event_id,
                is_answered =True
            )
            for question in questions:
                json_data.append({
                    'q': question.question,
                    'a':question.answer
                })

            return Response({'data':json_data})
        except Exception as exp:
            return Response({'detail':str(exp)})


class SendQuestion(APIView):
    def post(self,request):
        data =request.data
        try:
            event_id = data['eventId']
            message = data['message']
            email = data['email']
            event = Event.objects.get(id=event_id)

            Question.objects.create(
                event = event,
                question = message,
                sender_email = email if email else None
            )

            return Response({'success':True})
        
        except Exception as exp:
            print(exp)
            return Response({'error':str(exp)})



