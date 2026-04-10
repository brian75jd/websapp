from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFollowingModel(models.Model):
    followed = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'followers')
    follower = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'following')
    date_followed = models.DateTimeField(auto_now_add = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['followed','follower'],name='unique_following')
        ]
    
    def __str__(self):
        return f"{self.follower} follows {self.followed}"
