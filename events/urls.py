from django.urls import path
from events import views
from events import api
from events import auth
from events import dashboard
from django.contrib.auth.views import LoginView

app_name = 'events'

urlpatterns = [
    path('',views.Events,name='events'),
    path('get_events/',api.GetEvents,name='get_events'),
    path('buy_ticket/<int:event_id>/',views.Tickets,name='buy_ticket'),
    path('verify/<str:code>/', views.verify_ticket, name='verify_ticket'),
    path('get_event/<int:event_id>/',api.Get_EventId.as_view(),name='get_event'),
    path('purchase_ticket/',api.Buy_Tickets.as_view(),name='purchase_ticket'),
    path('create-organizer/',auth.CreateOrganizer,name='create-organizer'),
    path('organizer/',views.organizers,name='organizers'),
    path('questions/',api.HandleQuestions.as_view(),name='questions'),
    path('send_questions',api.SendQuestion.as_view(),name='send_questions'),
    path('login/',views.Loggin,name='login'),
    path('login_validate/',auth.LogginCredential,name='login_validate'),
    path('verify-api/',api.Verify_Ticket.as_view(),name='verify-api'),
    path('createuser/',views.create_User_account,name='createuser'),
    path('create_user_account/',auth.CreateUser,name='create_user_account'),
    path('dashboard/',views.Dashboard,name='dashboard'),
    path('logout/',views.LogoutUser,name='logout'),
    path('await-ticket/',views.ticket_await,name='await-ticket'),
    

    #create event
    path('create_event_form/',views.Create_Event,name='create_event_form'),

    # Dashboard AJAX endpoints
    path("ajax/dashboard/", dashboard.Dasboard_Data.as_view(), name="dashboard_data"),
    path("ajax/events/",  dashboard.Organizer_Events.as_view(),     name="organizer_events"),
    path("ajax/tickets/",  dashboard.Organizer_Tickets.as_view(),    name="organizer_tickets"),
    path("ajax/attendees/",  dashboard.organizer_attendees,  name="organizer_attendees"),
    path("ajax/questions/",    dashboard.Organizer_Questions.as_view(),  name="organizer_questions"),
    path("ajax/answer-question/",dashboard.Answer_Question.as_view(),      name="answer_question"),
    path("delete/<int:pk>/",    dashboard.Delete_Event.as_view(),         name="delete_event"),
]