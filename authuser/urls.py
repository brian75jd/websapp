from authuser import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


app_name = 'authuser'

urlpatterns = [
    path('',views.LoginView,name='loginview'),
    path('login/',views.LogUserIn,name='login'),
    path('signup/',views.SignUp, name='signup'),
    path('register_2/',views.SignInPhaseTwo,name='register_2'),
    path('verify/',views.Verify_otp, name='verify'),
    path('cancel/',views.Cancel_Registration,name='cancel'),
    path('resend_token/',views.Resend_Token, name='resend_token'),
    path('logout/',views.Logout,name='logout')
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

