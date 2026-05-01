from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()

class Notification(models.Model):
    class Notification_Type(models.TextChoices):
        FOLLOW = 'Follow','Follow'
        LIKE = 'Like','Like'
        COMMENT = 'Comment','Comment'
        EVENT = 'Event','Event'
        
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications',null=True,blank=True)
    receiver = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    notification_type = models.CharField(max_length=50,choices=Notification_Type)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True,blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_content(self):
        if self.notification_type =='Follow':
            return f"{self.sender.first_name} {self.sender.last_name} Follows you!"
        
        if self.notification_type =='Like':
            return f"{self.sender.first_name} {self.sender.last_name} liked your Post!"
        
        if self.notification_type =='Comment':
            return f"{self.sender.first_name} {self.sender.last_name} commented on your Post!"
        if self.notification_type =='Event':
            return "New event that you might be interested in was  uploaded. Check now"

    def __str__(self):
        return f"{self.receiver.username} received a notification "

