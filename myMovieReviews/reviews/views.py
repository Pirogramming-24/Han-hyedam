from django.shortcuts import render, redirect
from .models import Review

def review_list(request):
    sort = request.GET.get('sort', '-created_at')
    
    if sort == 'title':
        reviews = Review.objects.all().order_by('title')
    elif sort == 'rating':
        reviews = Review.objects.all().order_by('-rating')
    elif sort == 'running_time':
        reviews = Review.objects.all().order_by('running_time')
    elif sort == 'release_year':
        reviews = Review.objects.all().order_by('-release_year')
    else:
        reviews = Review.objects.all().order_by('-created_at')
    
    for review in reviews:
        review.hours = review.running_time // 60
        review.minutes = review.running_time % 60
    
    context = {'reviews': reviews}
    return render(request, 'review_list.html', context)

def review_detail(request, pk):
    review = Review.objects.get(id=pk)
    
    hours = review.running_time // 60
    minutes = review.running_time % 60
    
    context = {
        'review': review,
        'hours': hours,
        'minutes': minutes,
    }
    return render(request, 'review_detail.html', context)

def review_create(request):
    if request.method == "POST":
        Review.objects.create(
            title=request.POST['title'],
            release_year=request.POST['release_year'],
            genre=request.POST['genre'],
            rating=request.POST['rating'],
            director=request.POST['director'],
            actors=request.POST['actors'],
            running_time=request.POST['running_time'],
            content=request.POST['content'],
        )
        return redirect('reviews:review_list')
    return render(request, 'review_form.html')

def review_update(request, pk):
    review = Review.objects.get(id=pk)
    
    if request.method == "POST":
        review.title = request.POST['title']
        review.release_year = request.POST['release_year']
        review.genre = request.POST['genre']
        review.rating = request.POST['rating']
        review.director = request.POST['director']
        review.actors = request.POST['actors']
        review.running_time = request.POST['running_time']
        review.content = request.POST['content']
        review.save()
        return redirect('reviews:detail', pk=pk)
    
    context = {'review': review}
    return render(request, 'review_form.html', context)

def review_delete(request, pk):
    if request.method == "POST":
        review = Review.objects.get(id=pk)
        review.delete()
    return redirect('reviews:review_list')