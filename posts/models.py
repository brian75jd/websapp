from django.db import models
from django.contrib.auth import get_user_model
import uuid
from PIL import Image
from io import BytesIO
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.base import ContentFile

User  = get_user_model()

class Post(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    poster = models.ForeignKey(User, on_delete=models.CASCADE,related_name='posts', db_index=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def posted_at(self):
        return naturaltime(self.date_created)
    
    def __str__(self):
        return f"{self.content}"
    

class PostPhoto(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='post_photos/')
    
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)

            output = BytesIO()

            img = img.convert('RGB')  # important for JPEG
            img.save(output, format='JPEG', quality=70)

            output.seek(0)
            self.image = ContentFile(output.read(), name=self.image.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Photo for post {self.post.id}"


class PostLikes(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE,related_name='likes')
    liker = models.ForeignKey(User,on_delete=models.CASCADE)
    liked_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-liked_date']
        constraints = [
            models.UniqueConstraint(fields=['liker','post'],name='unique_post_like')
        ]
    
    def __str__(self):
        return f"{self.liker} likes {self.post.content[:50]}"

class Comments(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='comments/',blank=True,null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user','post'])
        ]

    def commented_time(self):
        return naturaltime(self.created_at)
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post.id}"
    
