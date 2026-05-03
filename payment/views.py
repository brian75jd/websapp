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
from payment.utils import verify_webhook

@method_decorator(csrf_exempt, name='dispatch')
class Payment_Webhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        
        if not verify_webhook(request):
            return Response({'error': 'Invalid signature'}, status=403)

        try:
            data = request.data

            tx_ref = data.get('tx_ref')
            resp_status = data.get('status')

            if resp_status != 'success':
                return Response({'detail': 'Payment not successful'}, status=400)

            with transaction.atomic():

                if Payment.objects.filter(tx_ref=tx_ref).exists():
                    return Response({'message': 'Already processed'}, status=200)

                ticket = Ticket.objects.select_for_update().filter(tx_reference=tx_ref).first()

                if not ticket:
                    return Response({'error': 'Ticket not found'}, status=404)

                if ticket.is_paid:
                    return Response({'message': 'Ticket already paid'}, status=200)

                ticket.is_paid = True
                ticket.save()
                ticket.generate_qr()

                payment = Payment(
                    event=ticket.event,
                    email=data.get('email'),
                    tx_ref=tx_ref,
                    amount=data.get('amount'),
                    currency=data.get('currency'),
                    status=resp_status,
                    phone=data.get('customer', {}).get('phone'),
                    description=data.get('customization', {}).get('description'),
                    reference=data.get('reference')
                )

                payment.save()

                return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as exp:
            print("Webhook error:", str(exp))
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        
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
      