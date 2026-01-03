from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Idea, DevTool, IdeaStar



def idea_list(request):
    ideas = Idea.objects.all()
    
    sort = request.GET.get('sort', '') 
    
    if sort == 'latest':
        ideas = ideas.order_by('-created_at')
    elif sort == 'name':
        ideas = ideas.order_by('title')
    elif sort == 'interest':
        ideas = ideas.order_by('-interest')
    elif sort == 'star':
        from django.db.models import Count
        ideas = ideas.annotate(star_count=Count('stars')).order_by('-star_count')
    else:
        ideas = ideas.order_by('-created_at')
    
    search = request.GET.get('search', '')
    if search:
        ideas = ideas.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search)
        )
    
    starred_ideas = []
    if request.user.is_authenticated:
        starred_ideas = IdeaStar.objects.filter(
            user=request.user
        ).values_list('idea_id', flat=True)
    
    paginator = Paginator(ideas, 4)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'sort': sort,
        'search': search,
        'starred_ideas': list(starred_ideas),
    }
    
    return render(request, 'ideas/idea_list.html', context)


@login_required
def idea_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        content = request.POST.get('content')
        interest = request.POST.get('interest', 0)
        devtool_id = request.POST.get('devtool')
        
        devtool = get_object_or_404(DevTool, id=devtool_id)
        
        idea = Idea.objects.create(
            title=title,
            image=image,
            content=content,
            interest=interest,
            devtool=devtool
        )
        
        return redirect('idea_detail', idea_id=idea.id)
    
    devtools = DevTool.objects.all()
    return render(request, 'ideas/idea_create.html', {'devtools': devtools})


def idea_detail(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    
    is_starred = False
    if request.user.is_authenticated:
        is_starred = IdeaStar.objects.filter(user=request.user, idea=idea).exists()
    
    context = {
        'idea': idea,
        'is_starred': is_starred,
    }
    return render(request, 'ideas/idea_detail.html', context)


@login_required
def idea_update(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    
    if request.method == 'POST':
        idea.title = request.POST.get('title')
        idea.content = request.POST.get('content')
        idea.interest = request.POST.get('interest', idea.interest)
        devtool_id = request.POST.get('devtool')
        
        if devtool_id:
            idea.devtool = get_object_or_404(DevTool, id=devtool_id)
        
        if request.FILES.get('image'):
            idea.image = request.FILES.get('image')
        
        idea.save()
        return redirect('idea_detail', idea_id=idea.id)
    
    devtools = DevTool.objects.all()
    context = {
        'idea': idea,
        'devtools': devtools,
    }
    return render(request, 'ideas/idea_update.html', context)


@login_required
def idea_delete(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    if request.method == 'POST':
        idea.delete()
        return redirect('idea_list')
    return redirect('idea_detail', idea_id=idea_id)



@login_required
@require_POST
def idea_toggle_star(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    
    star, created = IdeaStar.objects.get_or_create(user=request.user, idea=idea)
    
    if not created:  
        star.delete()
        is_starred = False
    else: 
        is_starred = True
    
    star_count = idea.stars.count()
    
    return JsonResponse({
        'is_starred': is_starred,
        'star_count': star_count
    })


@login_required
@require_POST
def idea_change_interest(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    action = request.POST.get('action')
    
    if action == 'increase':
        idea.interest += 1
    elif action == 'decrease' and idea.interest > 0:
        idea.interest -= 1
    
    idea.save()
    
    return JsonResponse({
        'interest': idea.interest
    })



def devtool_list(request):
    devtools = DevTool.objects.all()
    return render(request, 'ideas/devtool_list.html', {'devtools': devtools})


@login_required
def devtool_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        kind = request.POST.get('kind')
        content = request.POST.get('content')
        
        devtool = DevTool.objects.create(
            name=name,
            kind=kind,
            content=content
        )
        
        return redirect('devtool_detail', devtool_id=devtool.id)
    
    return render(request, 'ideas/devtool_create.html', {'kinds': DevTool.KIND_CHOICES})


def devtool_detail(request, devtool_id):
    devtool = get_object_or_404(DevTool, id=devtool_id)
    ideas = devtool.ideas.all() 
    
    context = {
        'devtool': devtool,
        'ideas': ideas,
    }
    return render(request, 'ideas/devtool_detail.html', context)


@login_required
def devtool_update(request, devtool_id):
    devtool = get_object_or_404(DevTool, id=devtool_id)
    
    if request.method == 'POST':
        devtool.name = request.POST.get('name')
        devtool.kind = request.POST.get('kind')
        devtool.content = request.POST.get('content')
        devtool.save()
        
        return redirect('devtool_detail', devtool_id=devtool.id)
    
    context = {
        'devtool': devtool,
        'kinds': DevTool.KIND_CHOICES,
    }
    return render(request, 'ideas/devtool_update.html', context)


@login_required
def devtool_delete(request, devtool_id):
    devtool = get_object_or_404(DevTool, id=devtool_id)
    if request.method == 'POST':
        devtool.delete()
        return redirect('devtool_list')
    return redirect('devtool_detail', devtool_id=devtool_id)