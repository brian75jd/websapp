from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.views.decorators.http import require_GET, require_POST
from events.models import Event, EventAttendance, TicketType, Ticket, Question
from authuser.utils import send_Email_Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


def _event_dict(event):
    return {
        "id":                 event.pk,
        "title":              event.title,
        "description":        event.description,
        "location":           event.location,
        "is_paid":            event.is_paid,
        "is_promoted":        event.is_promoted,
        "event_type":         event.event_type,
        "event_type_display": event.get_event_type_display(),
        "date":               event.start_datetime.strftime("%b %d, %Y"),
        "start_time":         event.start_datetime.strftime("%H:%M"),
        "end_time":           event.end_datetime.strftime("%H:%M"),
        "poster":             event.poster.url     if event.poster     else None,
        "thumbnail":          event.thumbnail.url  if event.thumbnail  else None,
    }


class Dasboard_Data(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        events = Event.objects.filter(created_by=request.user).order_by("-start_datetime")

        total_tickets_sold = (
            Ticket.objects
            .filter(event__created_by=request.user)
            .aggregate(total=Sum("quantity"))["total"] or 0
        )
        total_revenue = (
            Ticket.objects
            .filter(event__created_by=request.user, is_paid=True)
            .aggregate(total=Sum("amount_paid"))["total"] or 0
        )
        total_attendees = (
            EventAttendance.objects
            .filter(event__created_by=request.user)
            .count()
        )
        unanswered_count = (
            Question.objects
            .filter(event__created_by=request.user, is_answered=False)
            .count()
        )

        return Response({
            "total_events":       events.count(),
            "total_tickets_sold": total_tickets_sold,
            "total_revenue":      total_revenue,
            "total_attendees":    total_attendees,
            "unanswered_count":   unanswered_count,
            "events":             [_event_dict(e) for e in events],
        },status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 2. MY EVENTS (full list)
#    GET /events/ajax/events/
# ─────────────────────────────────────────

class Organizer_Events(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        events = Event.objects.filter(created_by=request.user).order_by("-start_datetime")
        return Response({"events": [_event_dict(e) for e in events]},status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 3. TICKETS
#    GET /events/ajax/tickets/
# ─────────────────────────────────────────
class Organizer_Tickets(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        events = (
            Event.objects
            .filter(created_by=request.user, is_paid=True)
            .prefetch_related("ticket_types")
            .order_by("-start_datetime")
        )

        data = []
        for event in events:
            tts = event.ticket_types.all()
            if not tts.exists():
                continue
            data.append({
                "id":    event.pk,
                "title": event.title,
                "date":  event.start_datetime.strftime("%b %d"),
                "ticket_types": [
                    {
                        "type":         tt.type,
                        "type_display": tt.get_type_display(),
                        "price":        tt.price,
                        "capacity":     tt.capacity,
                        "tickets_sold": tt.tickets_sold(),
                        "tickets_left": tt.tickets_left(),
                    }
                    for tt in tts
                ],
            })

        return Response({"events": data},status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 4. ATTENDEES
#    GET /events/ajax/attendees/
# ─────────────────────────────────────────
@login_required
@require_GET
def organizer_attendees(request):
    attendances = (
        EventAttendance.objects
        .filter(event__created_by=request.user)
        .select_related("user", "event")
        .order_by("-created_at")
    )

    data = []
    for att in attendances:
        user = att.user
        name = user.get_full_name() or user.username
        profile_pic = None
        if hasattr(user, "profile_pic") and user.profile_pic:
            profile_pic = user.profile_pic.url

        data.append({
            "name":        name,
            "event_title": att.event.title,
            "is_paid":     att.event.is_paid,
            "profile_pic": profile_pic,
        })

    return Response({"attendees": data})


# ─────────────────────────────────────────
# 5. Q&A
#    GET /events/ajax/questions/
# ─────────────────────────────────────────
class Organizer_Questions(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        questions = (
            Question.objects
            .filter(event__created_by=request.user)
            .select_related("event")
            .order_by("-created_at")
        )

        data = [
            {
                "id":          q.pk,
                "question":    q.question,
                "answer":      q.answer,
                "is_answered": q.is_answered,
                "event_title": q.event.title,
                "created_at":  q.created_at.strftime("%b %d"),
                "answered_at": q.answered_at.strftime("%b %d") if q.answered_at else None,
            }
            for q in questions
        ]

        return Response({"questions": data},status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 6. ANSWER A QUESTION
#    POST /events/ajax/answer-question/
# ─────────────────────────────────────────
def do_nothing():
    pass

class Answer_Question(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        question_id = request.data.get("question_id")
        answer      = request.data.get("answer", "").strip()

        if not question_id or not answer:
            return Response({"success": False, "error": "Missing fields."}, status=400)

        try:
            from django.utils import timezone
            q = Question.objects.get(pk=question_id, event__created_by=request.user)
            q.answer      = answer
            q.is_answered = True
            q.answered_at = timezone.now()
            q.save()
            send_Email_Response(response=q.answer,
                                question=q.question,event=q.event.title,
                                email=q.sender_email) if q.sender_email else do_nothing()
            return Response({"success": True})
        except Question.DoesNotExist:
            return Response({"success": False, "error": "Not found."}, status=404)


# ─────────────────────────────────────────
# 7. DELETE AN EVENT
#    POST /events/delete/<id>/
# ─────────────────────────────────────────
class Delete_Event(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request, pk):
        try:
            event = Event.objects.get(pk=pk, created_by=request.user)
            event.delete()
            return Response({"success": True})
        except Event.DoesNotExist:
            return Response({"success": False, "error": "Not found."}, status=404)


