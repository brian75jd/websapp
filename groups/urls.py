from groups import views
from django.urls import path

app_name = 'groups'

urlpatterns = [
    path('',views.GroupView, name='group')
]
