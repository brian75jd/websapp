from django.shortcuts import render
from posts.models import PostLikes, Post,Comments,PostPhoto
from usermanager.models import UserFollowingModel
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from posts.forms import HandleComments
from django.contrib.auth import get_user_model
from django.db.models import F, Q ,Exists,OuterRef
from notifications.services import send_notification

User = get_user_model()

@login_required
@require_http_methods(['POST'])
def Like_Post(request):   
    try:
       
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        target_user = post.poster

        like, created = PostLikes.objects.get_or_create(
            liker=request.user,
            post=post
        )

        if not created:
            like.delete()
            total_likes = post.likes.count()  

            return JsonResponse({
                'detail': 'unliked',
                'total_likes': total_likes
            }, status=200)
        
        send_notification(sender=request.user,receiver=target_user,notification_type='Like',
                    message=f'{request.user.first_name} {request.user.last_name} has Likes your post')

        total_likes = post.likes.count()  

        return JsonResponse({
            'detail': 'Liked',
            'total_likes': total_likes
        }, status=200)

    except Exception as exp:
        print(str(exp))
        return JsonResponse({'error': str(exp)})
@login_required
@require_http_methods(['POST'])
def PostComments(request):
    try:
        post_id = request.POST.get('post_id')
        content = request.POST.get('content')
        post = Post.objects.get(id=post_id)
        target_user = post.poster
        comment = Comments.objects.create(
            user = request.user,
            comment = content,
            post = post
        )
        send_notification(sender=request.user,receiver=target_user,notification_type='Like',
                    message=f'{request.user.first_name} {request.user.last_name} has commented on your post')

        return JsonResponse({
            'first_name':request.user.first_name,
            'last_name':request.user.last_name,
            'comment':comment.comment,
            'data_created':comment.created_at,
            'comments':post.comments.count()
        })
    except Exception as exp:
        return JsonResponse({'error':str(exp)})

def CreatePostView(request):
    posts = []
    images = []
    
    posts = Post.objects.filter(
        poster = request.user
    ).annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),
    ).select_related('poster')[:10]

    post_data = [
        {
            'id':post.id,
            'content':post.content,
            'first_name':post.poster.first_name,
            'image':post.poster.photo.url if post.poster.photo else None,
            'last_name':post.poster.last_name,
            'time':post.date_created.strftime('%Y-%m-%d'),
            'likes':post.total_likes,
            'comments':post.total_comments
        }

        for post in posts 
    ]
    return render(request,'pages/post_creation.html',{'posts':posts})


@require_http_methods(['POST'])
def CreatePost(request):
    post_content = request.POST.get('post', '')
    photos = request.FILES.getlist('images')

    if not post_content and not photos:
        return JsonResponse({'error': 'Post cannot be empty'}, status=400)

    post = Post.objects.create(
        poster=request.user,
        content=post_content
    )

    for img in photos:
        PostPhoto.objects.create(
            post=post,
            image=img
        )

    return JsonResponse({
        'detail': "Post created successfully"
    }, status=200)

@login_required
@require_http_methods(['POST'])
def Delete_Post(request):
    try:
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        post.delete()
        return JsonResponse({
            'detail':'Post deleted successfully',
            'success':True},status=200)
    except Exception as exp:
        return JsonResponse({'detail':str(exp),'success':False},status=404)

@login_required
@require_http_methods(['POST'])
def Delete_Comment(request):
    try:
        comment_id = request.POST.get('comment_id')
        comment = Comments.objects.get(id=comment_id)
        if comment:
            comment.delete()
            return JsonResponse({'success':True,},status=200)
        return JsonResponse({'success':False})
    except Exception as exp:
        return JsonResponse({'success':False},status=400)


@login_required
@require_http_methods(['POST'])
def SearchDB(request):
    query = request.POST.get('value')
    users = []
    posts = []
    user_id = request.user.id

    users = User.objects.filter(
        Q(first_name__icontains = query)|Q(last_name__icontains=query)|
        Q(username__icontains=query)
    ).annotate(
        isFollowing = Exists(UserFollowingModel.objects.filter(
            follower = request.user,
            followed = OuterRef('id')
        ))
    ).exclude(id=user_id)[:10]

    posts = Post.objects.filter(
        Q(content__icontains=query)
    ).annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),
    ).select_related('poster')[:10]

    user_data =[ {
        'id':user.id,
        'username':user.username,
        'first_name':user.first_name,
        'last_name':user.last_name,
        'isFollowing':user.isFollowing,
        'mutual':10,
        'profile': user.photo.url if user.photo else None,
    }
      for user in users
    ]
    post_data = [
        {
            'id':post.id,
            'content':post.content,
            'first_name':post.poster.first_name,
            'image':post.poster.photo.url if post.poster.photo else None,
            'last_name':post.poster.last_name,
            'time':post.date_created.strftime('%Y-%m-%d'),
            'likes':post.total_likes,
            'comments':post.total_comments
        }

        for post in posts 
    ]
    return JsonResponse({'users':user_data,'posts':post_data})

@login_required
def Posts_Posted_By_User(request):
    posts = []
    images = []
    
    posts = Post.objects.filter(
        poster = request.user
    ).annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),
    ).select_related('poster')[:10]

    post_data = [
        {
            'id':post.id,
            'content':post.content,
            'first_name':post.poster.first_name,
            'image':post.poster.photo.url if post.poster.photo else None,
            'last_name':post.poster.last_name,
            'time':post.date_created.strftime('%Y-%m-%d'),
            'likes':post.total_likes,
            'comments':post.total_comments
        }

        for post in posts 
    ]

    return JsonResponse({'data':post_data})

@login_required
@require_http_methods(['POST'])  
def GetComments(request):
    post_id = request.POST.get('post_id')
    comments = Comments.objects.filter(post__id = post_id)\
               .select_related('user')\
               .order_by('created_at')
    data = []
    for comment in comments:
        data.append({
            'id':comment.id,
            'text':comment.comment,
            'created_at':comment.created_at.strftime('%b:%d'),
            'user':{
                'id':comment.user.id,
                'first_name':comment.user.first_name,
                'last_name':comment.user.last_name,
                'photo': comment.user.photo.url if comment.user.photo else ''
            },
            'is_owner':comment.user == request.user
        }) 
    return JsonResponse({'comments':data})
    
