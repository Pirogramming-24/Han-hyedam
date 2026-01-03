from django.db import models
from django.contrib.auth.models import User


class DevTool(models.Model):
    KIND_CHOICES = [
        ('웹 프레임워크', '웹 프레임워크'),
        ('프론트엔드 프레임워크', '프론트엔드 프레임워크'),
        ('백엔드 프레임워크', '백엔드 프레임워크'),
        ('자바스크립트 실행 환경', '자바스크립트 실행 환경'),
        ('프로그래밍 언어', '프로그래밍 언어'),
    ]
    
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=50, choices=KIND_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Idea(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='idea_images/')
    content = models.TextField()
    interest = models.IntegerField(default=0) 
    devtool = models.ForeignKey(DevTool, on_delete=models.CASCADE, related_name='ideas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class IdeaStar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='stars')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'idea') 
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.idea.title}"
