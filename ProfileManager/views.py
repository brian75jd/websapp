from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from usermanager.models import UserFollowingModel
from ProfileManager.forms import Edit_ProfileForm

User = get_user_model()

@login_required
def ProfileManager(request):
    return render(request, template_name='pages/profile.html')

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
    data = []
    followers = User.objects.filter(
        following__followed=request.user
    )
    for follower in followers:
        data.append({
            'id':follower.id,
            'photo':follower.photo.url if follower.photo else "",
            'first_name':follower.first_name,
            'last_name':follower.last_name[:1]
        })
    return JsonResponse({'followers': data})

@login_required
@require_http_methods(['POST'])
def Edit_Profile(request):
    form = Edit_ProfileForm(request.POST, current_user = request.user)
    try:
        if form.is_valid():
            name = form.cleaned_data['name']
            first_name = name[0] if len(name) > 0 else ''
            last_name = name[1] if len(name) > 1 else ''

            user = User.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.phone_number = form.cleaned_data['phone']
            user.save()
            return JsonResponse({'detail':'changes applied. Refresh to see changes'})
        
        return JsonResponse({'detail':str(error for error in form.errors)})
    
    except Exception as exp:
        return JsonResponse({'detail':str(exp)})
    