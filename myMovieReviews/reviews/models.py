from django.db import models

# Create your models here.
class Review(models.Model):
    GENRE_CHOICES = [
        ('액션', '액션'),
        ('코미디', '코미디'),
        ('드라마', '드라마'),
        ('SF', 'SF'),
        ('스릴러', '스릴러'),
        ('로맨스', '로맨스'),
        ('애니메이션', '애니메이션'),
        ('다큐멘터리', '다큐멘터리'),
        ('호러', '호러'),
        ('판타지', '판타지'),
    ]
    
    title = models.CharField(max_length=100)
    release_year = models.IntegerField()
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    rating = models.FloatField()
    director = models.CharField(max_length=50)
    actors = models.CharField(max_length=200)
    running_time = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)