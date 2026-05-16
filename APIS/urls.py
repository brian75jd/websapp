from django.urls import path
from APIS import views

app_name = 'apis'

urlpatterns = [
    path('get_matches/',views.Sports_Update.as_view(),name='get_matches'),
    path('settings/developer/',views.developer_page,name='developer'),
    path('internal/matches/',views.App_Sports_Update.as_view(),name='int_matches'),
    path('vacancy/',views.VacancyManager.as_view(),name='vacancy'),
    path('view_vacancy/<int:vac_id>/',views.vacancy_view,name='view_vacancy')
]
