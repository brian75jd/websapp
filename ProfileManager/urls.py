from ProfileManager import views
from django.urls import path

app_name = 'profile'

urlpatterns = [
    path('',views.ProfileManager,name='profile'),
    path('poster_detail/<int:user_id>/',views.PostProfileManager,name='poster_detail'),
    path('update_cover/',views.Update_Cover,name='update_cover'),
    path('followers/',views.Followers_Display,name='followers')
]
