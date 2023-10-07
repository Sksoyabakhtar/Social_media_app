from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.TextField()
    age = models.PositiveIntegerField()
    dob = models.DateField(default="2000-01-01")
    phone_number = models.CharField(max_length=15, default='')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_name = models.CharField(max_length=100)
    post_description = models.TextField()
    post_image = models.ImageField(upload_to='post_image/')
    category_choices = [
        ('cricket', 'Cricket'),
        ('social', 'Social'),
        ('science', 'Science'),
        ('article', 'Article'),
        ('art', 'Art'),
        ('news', 'News'),
    ]
    category = models.CharField(max_length=20, choices=category_choices)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.post_name

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.post_name}"


