import random
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string


def get_otp():
    return str(random.randint(100000, 999999))

def send_notification(email, token):
    print(f"From: Webs \n" 
          f"To:{email} \n"
          f"Your OTP: {token}")

def send_Email(otp, email,first_name,last_name):
    html_content = render_to_string('auth/otp_email.html',{
        'first_name':first_name,
        'last_name':last_name,
        'otp':otp
    })
    email = EmailMultiAlternatives(
        subject= 'Email Verification',
        body=f'Your otp is {otp}',
        from_email= "Webs <jaydeemalawi@gmail.com>",
        to= [email]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()             
    

    