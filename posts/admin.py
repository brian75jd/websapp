from django.contrib import admin

from posts.models import Post,PostLikes, Comments,PostPhoto

admin.site.register(PostLikes)
admin.site.register(Post)
admin.site.register(Comments)
admin.site.register(PostPhoto)