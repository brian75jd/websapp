from django.urls import path 
from payment import views


app_name = 'payment'

urlpatterns = [
    path('api/webhook/',views.Payment_Webhook.as_view(),
         name='webhook')
]