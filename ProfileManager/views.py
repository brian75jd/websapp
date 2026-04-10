from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from usermanager.models import UserFollowingModel

User = get_user_model()

@login_required
def ProfileManager(request):
    followers = User.objects.filter(
        following__followed=request.user
    ).only('id', 'username', 'photo', 'gender').distinct()
    return render(request,'pages/profile.html',{'followers':followers})

@login_required
def PostProfileManager(request, user_id):
    user = User.objects.get(id=user_id)
    context = {
        'user':user
    }
    return render(request, 'pages/poster_detail.html',context)

@login_required
@require_POST
def Update_Cover(request):
    user = request.user
    updated = False

    photo = request.FILES.get('photo')
    cover_photo = request.FILES.get('cover_photo')

    if photo:
        user.photo = photo
        updated = True

    if cover_photo:
        user.cover_photo = cover_photo
        updated = True

    if updated:
        user.save()  

        return JsonResponse({
            'detail': 'Updated successfully',
            'photo_url': user.photo.url if user.photo else None,
            'cover_url': user.cover_photo.url if user.cover_photo else None
        })

    return JsonResponse({'error': 'No file uploaded'}, status=400)       

@login_required
def Followers_Display(request):
    user = request.user
    followers = user.following.all()
    return render(request,'pages/profile.html',{'followers':followers})