from django.shortcuts import render
from posts.models import Post, PostLikes, Comments
from django.contrib.auth import get_user_model
from usermanager.models import UserFollowingModel
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Cast
from django.db.models import (
    Exists, OuterRef, Count, Q, F, IntegerField, FloatField, ExpressionWrapper
)
from notifications.models import Notification
from django.db.models.functions import Cast
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Case, When, Value, FloatField
from django.http import JsonResponse


User = get_user_model()

@login_required  
def FeedView(request):
    return render(request, template_name='pages/feed.html')

@login_required
def Get_Posts(request):
    user = request.user
    current_time = now()

    # 🔥 Pagination (optional but READY)
    page = int(request.POST.get('page', 1))
    limit = 3
    start = (page - 1) * limit
    end = start + limit

    posts = Post.objects.annotate(
        # 🔥 Relationships
        is_following=Exists(
            UserFollowingModel.objects.filter(
                follower=user,
                followed=OuterRef('poster')
            )
        ),

        is_liked=Exists(
            PostLikes.objects.filter(
                liker=user,
                post=OuterRef('pk')
            )
        ),

        is_same_department=Q(poster__department=user.department),

        # 🔥 Counts
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),

    ).annotate(
        # 🔥 Convert to numbers
        following_score=Cast('is_following', IntegerField()),
        dept_score=Cast('is_same_department', IntegerField()),

        # 🔥 Base score
        base_score=(
            (F('total_likes') * 2.0) +
            (F('total_comments') * 3.0) +
            (F('following_score') * 5.0) +
            (F('dept_score') * 2.0)
        ),

        # 🔥 Time decay
        decay_factor=Case(
            When(date_created__gte=current_time - timedelta(hours=1), then=Value(1.0)),
            When(date_created__gte=current_time - timedelta(hours=6), then=Value(1.5)),
            When(date_created__gte=current_time - timedelta(hours=24), then=Value(2.5)),
            default=Value(4.0),
            output_field=FloatField()
        )

    ).annotate(
        
        final_score=ExpressionWrapper(
            F('base_score') / F('decay_factor'),
            output_field=FloatField()
        )
    ).order_by('-final_score')

    posts = posts.select_related('poster').prefetch_related('photos')


    posts = posts[start:end]


    posts_data = []

    for post in posts:
        posts_data.append({
            "id": post.id,
            "content": post.content,
            "posted_at": post.date_created.strftime("%b %d,%Y"),

            "total_likes": post.total_likes,
            "total_comments": post.total_comments,

            "is_liked": post.is_liked,
            "is_following": post.is_following,

            "poster": {
                "id": post.poster.id,
                "first_name": post.poster.first_name,
                "last_name": post.poster.last_name,
                "photo": post.poster.photo.url if post.poster.photo else "/media/default.png",
            },

            "photos": [
                photo.image.url for photo in post.photos.all() 
            ]
        })

    # 🔥 Notifications
    unread_count = Notification.objects.filter(
        receiver=user,
        is_read=False
    ).count()

    return JsonResponse({
        "posts": posts_data,
        "unread_count": unread_count
    })

@login_required
def Profile(request):
    return render(request,'pages/prof.html')
