from django.db import models
from django.contrib.auth.models import User

# Create your models here.  

# Implementing the Topic Category to group them.
class ForumCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Forum Categories'

    def __str__(self):
        return self.name


class ForumTopic(models.Model):
    category = models.ForeignKey(ForumCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='topics')
    title = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class ForumPost(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.author.username} in {self.topic.title}"
    
    