from django.urls import path
from APIS import views

app_name = 'apis'

urlpatterns = [
    path('get_matches/',views.Sports_Update.as_view(),name='get_matches'),
    path('settings/developer/',views.developer_page,name='developer')
]
