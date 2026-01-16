from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Review
import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pathlib import Path
from langchain_upstage import ChatUpstage, UpstageEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Review, Comment 
from .forms import CommentForm 
from .models import Review, Comment, Like

# 회원가입
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('reviews:review_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# 로그인
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('reviews:review_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# 로그아웃
def logout_view(request):
    logout(request)
    return redirect('reviews:review_list')

def review_list(request):
    sort = request.GET.get('sort', '-created_at')
    filter_type = request.GET.get('filter', 'all')  
    
    if filter_type == 'tmdb':
        reviews = Review.objects.filter(is_tmdb=True)
    elif filter_type == 'user':
        reviews = Review.objects.filter(is_tmdb=False)
    else:  
        reviews = Review.objects.all()
    
    if sort == 'title':
        reviews = reviews.order_by('title')
    elif sort == 'rating':
        reviews = reviews.order_by('-rating')
    elif sort == 'running_time':
        reviews = reviews.order_by('running_time')
    elif sort == 'release_year':
        reviews = reviews.order_by('-release_year')
    else:
        reviews = reviews.order_by('-created_at')
    
    total_count = Review.objects.count()
    tmdb_count = Review.objects.filter(is_tmdb=True).count()
    user_count = Review.objects.filter(is_tmdb=False).count()
    
    paginator = Paginator(reviews, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    for review in page_obj:
        review.hours = review.running_time // 60
        review.minutes = review.running_time % 60
    
    context = {
        'reviews': page_obj,
        'page_obj': page_obj,
        'filter_type': filter_type,  
        'total_count': total_count,  
        'tmdb_count': tmdb_count,    
        'user_count': user_count,    
    }
    return render(request, 'review_list.html', context)

def search(request):
    query = request.GET.get('q', '').strip()
    
    if query:
        reviews = Review.objects.filter(
            Q(title__icontains=query) |
            Q(director__icontains=query) |
            Q(actors__icontains=query)
        ).distinct()
    else:
        reviews = Review.objects.none()
    
    paginator = Paginator(reviews, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    for review in page_obj:
        review.hours = review.running_time // 60
        review.minutes = review.running_time % 60
    
    context = {
        'reviews': page_obj,
        'page_obj': page_obj,
        'query': query,
        'total': reviews.count()
    }
    return render(request, 'search_results.html', context)

def review_detail(request, pk):
    review = Review.objects.get(id=pk)
    comments = review.comments.all()
    comment_form = CommentForm()
    
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(review=review, user=request.user).exists()
    
    hours = review.running_time // 60
    minutes = review.running_time % 60
    
    context = {
        'review': review,
        'hours': hours,
        'minutes': minutes,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,  
    }
    return render(request, 'review_detail.html', context)

@login_required
def review_create(request):
    if request.method == "POST":
        poster = request.FILES.get('poster')
        Review.objects.create(
            title=request.POST['title'],
            release_year=request.POST['release_year'],
            genre=request.POST['genre'],
            rating=request.POST['rating'],
            director=request.POST['director'],
            actors=request.POST['actors'],
            running_time=request.POST['running_time'],
            content=request.POST['content'],
            poster=poster,
            author=request.user,
        )
        return redirect('reviews:review_list')
    return render(request, 'review_form.html')

@login_required
def review_update(request, pk):
    review = Review.objects.get(id=pk)
    if review.author != request.user:
        return redirect('reviews:detail', pk=pk)
    
    if request.method == "POST":
        review.title = request.POST['title']
        review.release_year = request.POST['release_year']
        review.genre = request.POST['genre']
        review.rating = request.POST['rating']
        review.director = request.POST['director']
        review.actors = request.POST['actors']
        review.running_time = request.POST['running_time']
        review.content = request.POST['content']

        if request.FILES.get('poster'):  
            review.poster = request.FILES['poster']

        review.save()
        return redirect('reviews:detail', pk=pk)
    context = {'review': review}
    return render(request, 'review_form.html', context)

@login_required
def review_delete(request, pk):
    if request.method == "POST":
        review = Review.objects.get(id=pk)
        if review.author == request.user:
            review.delete()
    return redirect('reviews:review_list')

# 댓글 작성
@login_required
def comment_create(request, pk):
    review = Review.objects.get(id=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.review = review
            comment.author = request.user
            comment.save()
            return redirect('reviews:detail', pk=review.pk)
    
    return redirect('reviews:detail', pk=review.pk)

# 댓글 삭제
@login_required
def comment_delete(request, pk):
    comment = Comment.objects.get(pk=pk)
    review_pk = comment.review.pk
    
    if request.user == comment.author:
        comment.delete()
    
    return redirect('reviews:detail', pk=review_pk)

@login_required
def like_toggle(request, pk):
    review = Review.objects.get(id=pk)
    
    # 이미 좋아요를 눌렀는지 확인
    like = Like.objects.filter(review=review, user=request.user).first()
    
    if like:
        # 좋아요 취소
        like.delete()
    else:
        # 좋아요 추가
        Like.objects.create(review=review, user=request.user)
    
    return redirect('reviews:detail', pk=pk)

def ping(request):
    return HttpResponse("ok")

# 벡터스토어 & 리트리버 로드
VS_DIR = str(settings.BASE_DIR / "vector_store")
_embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
_vectorstore = FAISS.load_local(VS_DIR, _embeddings, allow_dangerous_deserialization=True)
_retriever = _vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 20, "lambda_mult": 0.5}
)

# 프롬프트
SYSTEM = """너는 영화 추천 전문 챗봇이야. 주어진 영화 정보를 바탕으로 사용자에게 적절한 영화를 추천해줘.
추천할 때는 영화 제목, 장르, 감독을 포함해서 친근하게 답변해. 
정보에 없는 내용은 추측하지 말고, 모른다고 솔직하게 말해. 답변은 5문장 이내로."""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "질문: {q}\n\n영화 정보:\n{ctx}")
])

llm = ChatUpstage(model="solar-mini", temperature=0.7)

@csrf_exempt
def chatbot(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    
    # JSON 파싱
    body = {}
    ctype = (request.headers.get("Content-Type") or "").lower()
    if "application/json" in ctype:
        try:
            body = json.loads(request.body.decode("utf-8"))
        except:
            body = {}
    if not body:
        body = request.POST.dict() or request.GET.dict()
    
    q = (body.get("question") or "").strip()
    if not q:
        return HttpResponseBadRequest("question required")
    
    # Retrieve: 관련 영화 검색
    docs = _retriever.invoke(q)
    if not docs:
        return JsonResponse({"answer": "관련 영화를 찾지 못했어요.", "movies": []})
    
    # Augmentation: 컨텍스트 구성
    ctx_parts = []
    for d in docs:
        text = (d.page_content or "").strip()
        if text:
            ctx_parts.append(text)
    ctx = "\n\n".join(ctx_parts[:4])
    
    # Generation: LLM 답변 생성
    messages = prompt.format_messages(q=q, ctx=ctx)
    answer = llm.invoke(messages).content
    
    # 영화 정보 추출
    movies = []
    for d in docs[:3]:
        m = d.metadata
        movies.append({
            "id": m.get("movie_id"),
            "title": m.get("title"),
        })
    
    return JsonResponse({"answer": answer, "movies": movies})

def chatbot_page(request):
    return render(request, 'chatbot.html')