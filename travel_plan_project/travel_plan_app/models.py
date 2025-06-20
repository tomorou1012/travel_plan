from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class Member(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    about_me = models.TextField(max_length=500, blank=True)
    member_image = models.ImageField(upload_to="profile_pics", blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    def __str__(self):
        return self.username

class Prefecture(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Post(models.Model):#migrationした後にCategoryからPrefectureに変えた
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    place = models.CharField(max_length=50)

    def __str__(self):
        return self.place   

class Weather(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name
        
class Day(models.Model):
    date = models.CharField(max_length=20)
    weather = models.ForeignKey(Weather, on_delete=models.SET_NULL, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='days')

    def __str__(self):
        return self.date
    
class Schedule(models.Model):
    time = models.TimeField()
    activity = models.CharField(max_length=100)
    day = models.ForeignKey(Day, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.activity

class Like(models.Model):
    member = models.ForeignKey(Member, related_name='liked', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        unique_together = ('member', 'post')  

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f'Comment by {self.member} on {self.post}'

class Notification(models.Model):
        NOTIFICATION_TYPES = (
            ('like', 'Like'),
            ('follow', 'Follow'),
            ('comment', 'Comment'),
        )

        sender = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='sent_notifications')
        recipient = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='notifications')
        notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
        post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
        is_read = models.BooleanField(default=False)
        created_at = models.DateTimeField(default=timezone.now)

        def __str__(self):
            return f'{self.sender} to {self.recipient}: {self.notification_type}'