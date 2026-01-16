from django import forms
from .models import Review, Comment

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'content', 'rating']  # poster 제거
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '영화 제목'}),
            'content': forms.Textarea(attrs={'placeholder': '리뷰 내용을 입력하세요...', 'rows': 5}),
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 10, 'step': 0.1}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': '댓글을 입력하세요...',
                'rows': 3,
                'class': 'comment-input'
            })
        }
        labels = {
            'content': ''
        }