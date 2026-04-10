from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from usermanager.models import UserFollowingModel
from notifications.services import send_notification

User = get_user_model()

@login_required
@require_http_methods(['POST'])
def ToggleBtn(request):
    user_id = request.POST.get('user_id')
    target_user = User.objects.get(id=user_id)
    follow, created = UserFollowingModel.objects.get_or_create(
        followed = target_user,
        follower = request.user
    )
    if not created:
        follow.delete()
        return JsonResponse({'detail':'Unfollowed'},status = 200)
    
    send_notification(sender=request.user,receiver=target_user,notification_type='Follow',
                    message=f'{request.user.first_name} {request.user.last_name} has Followed you')
    return JsonResponse({'detail':'Followed'},status = 200)

def Toggle(request,user_id):
    pass

        
