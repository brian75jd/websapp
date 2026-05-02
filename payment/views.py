from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes
from events.models import Event,Ticket
from django.db import transaction
from rest_framework import status
from payment.models import Payment
import json


@method_decorator(csrf_exempt, name='dispatch')
class Payment_Webhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        print('Paychangu hit')
        try:
          paychangu_resp = request.data
          email = paychangu_resp.get('email')
          amount = paychangu_resp.get('amount')
          currency = paychangu_resp.get('currency')
          tx_ref = paychangu_resp.get('tx_ref')
          resp_status = paychangu_resp.get('status')
          referrence = paychangu_resp.get('reference')
          print('resp_status')
 
          if resp_status == 'success':
            with transaction.atomic():
              ticket = Ticket.objects.filter(tx_reference = tx_ref).first()
              event = ticket.event
              ticket.is_paid = True
              ticket.save()

              payment = Payment(
                 event = event,
                 email=email if email else None,
                 tx_ref = tx_ref,
                 amount = amount,
                 currency = currency,
                 status = resp_status,
                 phone = paychangu_resp.get('customer')['phone'],
                 description = paychangu_resp.get('description'),
                 reference = referrence
              )
              payment.save()
              return Response({'success':True},
                              status=status.HTTP_200_OK)
          else:
            print('Unsuccessful response')
            return Response({'detail':'Payment was not successful','success':False},
                          status=status.HTTP_400_BAD_REQUEST)

        except Exception as exp:
           return Response({'success':False},
                           status=status.HTTP_400_BAD_REQUEST)

class Get_Ticket(APIView):
    def post(self, request, *args, **kwargs):
        tx_ref = request.data.get('tx_ref')

        if not tx_ref:
            return Response(
                {'detail': 'No tx_ref given', 'success': False},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ticket = Ticket.objects.get(tx_reference=tx_ref)

            qr_image_url = ""
            if ticket.qr_image:
                try:
                    qr_image_url = request.build_absolute_uri(ticket.qr_image.url)
                except ValueError:
                    qr_image_url = ""

            return Response({
                "success": True,
                "data": {
                    "id": ticket.id,
                    "is_paid": ticket.is_paid,
                    "qr_code": ticket.ticket_code,
                    "qr_image": qr_image_url,
                }
            }, status=status.HTTP_200_OK)

        except Ticket.DoesNotExist:
            return Response(
                {'detail': 'ticket not found', 'success': False},
                status=status.HTTP_404_NOT_FOUND
            )      
      
      
            

"""
{'event_type': 'checkout.payment', 
 'first_name': 'Brian', 'last_name': 'Bingala',
   'email': 'brian75jd@gmail.com', 'currency': 'MWK', 
   'amount': 20000, 'charge': 600,
     'amount_split': {'fee_paid_by_customer': 0, 
      'fee_paid_by_merchant': 600, 'total_amount_paid_by_customer': 20000, 'amount_received_by_merchant': 19400},
        'total_amount_paid': 20000, 'mode': 'test', 'type': 'API Payment (Checkout)',
          'status': 'success', 'reference': '55564479001', 'tx_ref': '9a667844227c4304', 'customization': 
          {'title': 'Ticket Payment', 'description': '1 ticket(s) for Murray Molloy', 'logo': None}, 
          'meta': '[]', 'customer': {'customer_ref': 'cs_42fa5c1c646ac2e', 'email': 'brian75jd@gmail.com', 'first_name': 'Brian', 'last_name': 'Bingala', 'phone': '998063700', 'created_at': 1776975712, 'merchant_reference_identifier': None}, 'authorization': {'channel': 'Test', 'card_details': None, 'bank_payment_details': None, 'mobile_money': None, 'completed_at': '2026-05-02T09:31:54.000000Z'}, 'created_at': '2026-05-02T09:31:54.000000Z', 'completed_at': '2026-05-02T09:31:54.000000Z'}

                                                
"""