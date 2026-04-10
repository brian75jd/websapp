from django.shortcuts import render,redirect
from authuser.forms import (UserRegistrationPhaseOne, UserRegistrationPhaseTwo,LogginUser,
                            OTP_Class)
from django.contrib.auth import authenticate,login
from django.contrib.auth import get_user_model
from authuser.utils import get_otp, send_notification,send_Email
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy

User = get_user_model()

def SignUp(request):
    if request.method =='POST':
        form = UserRegistrationPhaseOne(request.POST)
        if form.is_valid():
            request.session['user_data'] = {
                'first_name': form.cleaned_data.get('first_name'),
                'last_name': form.cleaned_data.get('last_name'),
                'username': form.cleaned_data.get('username'),
                'email': form.cleaned_data.get('email'),
                'password':form.cleaned_data.get('password1')
            }
            token = get_otp()
            request.session['otp'] = token
            send_Email(otp=token,email=form.cleaned_data.get('email'),first_name=form.cleaned_data.get('first_name'),last_name=form.cleaned_data.get('last_name'))
            #send_notification(email=form.cleaned_data.get('email'), token=token)
            
            return redirect('authuser:verify')
        return render(request,'auth/register.html',{'form':form})         
    form = UserRegistrationPhaseOne()
    return render(request,'auth/register.html',{'form':form})

def Verify_otp(request):
    request.session['is_verified'] = False
    if not request.session.get('otp') or not request.session.get('user_data'):
        return redirect('authuser:signup')
    otp = request.session['otp']
    if request.method =='POST':
        form = OTP_Class(request.POST)
        if form.is_valid():
            form_otp = form.cleaned_data.get('otp')
            if form_otp != otp:
                messages.error(request,'Invalid OTP')
                return render(request,'auth/verify.html',{'form':form})
            request.session['is_verified'] = True
            return redirect('authuser:register_2')
    return render(request,'auth/verify.html',{'email':request.session.get('user_data')['email']})

def SignInPhaseTwo(request):
    if not request.session.get('user_data') or not request.session.get('is_verified'):
        return redirect('authuser:signup')
    session_data = request.session.get('user_data')
    if request.method =='POST':
        form = UserRegistrationPhaseTwo(request.POST)
        if form.is_valid():
           user =  User(
                first_name = session_data['first_name'],
                last_name = session_data['last_name'],
                username = session_data['username'],
                email = session_data['email'],
                phone_number = form.cleaned_data['phone_number'],
                department = form.cleaned_data['department'],
                date_of_birth = form.cleaned_data['date_of_birth'],
                gender = form.cleaned_data['gender']

              )
           user.set_password(session_data['password'])
           user.save()
           del request.session['user_data']
           request.session.flush()

           login(request,user)
           return redirect('feed:feed')
        return render(request,'auth/register_2.html',{'form':form})
    form = UserRegistrationPhaseTwo()
    return render(request,'auth/register_2.html',{'form':form})

def Resend_Token(request):
    new_token = get_otp()
    email = request.session['user_data'].get('email')
    first_name = request.session['user_data'].get('first_name')
    last_name = request.session['user_data'].get('last_name')

    request.session['otp'] = new_token
    send_Email(otp=new_token,email=email,first_name=first_name,last_name=last_name)
    #send_notification(email=email,token=new_token)
    print(request.session.get('otp'))
    return redirect('authuser:verify')

def Cancel_Registration(request):
    request.session.flush()
    return redirect("authuser:signup")

def LoginView(request):
    return render(request,'auth/login.html',{'form':LogginUser()})

@require_POST
def LogUserIn(request):
    url = reverse_lazy('feed:feed')
    identifier = request.POST.get('identifier')
    password = request.POST.get('password')
    user = authenticate(username=identifier, password=password)
    if user is not None:
        login(request,user)
        return JsonResponse({'detail':'Logging user in.....',
                             'url':url,
                             'success':True
                             },status = 200
                        )
    else:
        try:
          username = User.objects.get(phone_number = identifier).username
        except User.DoesNotExist:
            return JsonResponse({'detail':'Invalid credentials. Try again','success':False})
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return JsonResponse({
                'detail':'Logging user in.....',
                'url':url,
                'success':True
                },status = 200)
        
        return JsonResponse({'detail':'Invalid credentials. Try again','sucess':False},status=400)

@login_required
def Logout(request):
    logout(request)
    return redirect('authuser:loginview')