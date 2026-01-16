from django.db import models
from django.contrib.auth.models import User

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

    tmdb_id = models.IntegerField(null=True, blank=True, unique=True) 
    poster_path = models.CharField(max_length=200, null=True, blank=True) 
    overview = models.TextField(null=True, blank=True)  
    vote_average = models.FloatField(null=True, blank=True)  
    is_tmdb = models.BooleanField(default=False) 

    poster = models.ImageField(upload_to='posters/', null=True, blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.author.username} - {self.review.title}"
    
    class Meta:
        ordering = ['-created_at']

class Like(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('review', 'user')  
    
    def __str__(self):
        return f"{self.user.username} likes {self.review.title}"