from django.urls import path
from posts import views

app_name = 'posts'

urlpatterns = [
    path('like_post/',views.Like_Post,name='like_post'),
    path('comment/',views.PostComments, name='comment_post'),
    path('create_postview/',views.CreatePostView,name='create_postview'),
    path('create_post/',views.CreatePost,name='create_post'),
    path('delete_post/',views.Delete_Post, name='delete_post'),
    path('delete_comment/',views.Delete_Comment,name='delete_comment'),
    path('search_db/',views.SearchDB,name='search_db'),
    path('posts_by_user/',views.Posts_Posted_By_User,name='posts_by_user'),
    path('get_comments/',views.GetComments,name='get_comments')
    
]
