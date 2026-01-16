from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Post
from .forms import PostForm
from .services import NutritionOCRService, NutritionExtractor
import os
from .services.hashtag_service import HashtagService

# Create your views here.
def main(request):
    posts = Post.objects.all()

    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    hashtag = request.GET.get('hashtag')

    if search_txt:
        posts = posts.filter(title__icontains=search_txt)
    
    if hashtag:
        posts = posts.filter(hashtags__icontains=hashtag)
    
    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
        'hashtag': hashtag,
    }
    return render(request, 'posts/list.html', context=context)

def create(request):
    if request.method == 'GET':
        form = PostForm()
        context = { 'form': form }
        return render(request, 'posts/create.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('/')

@csrf_exempt
def analyze_nutrition(request):
    """영양성분 분석 AJAX"""
    print("=" * 50)
    print("analyze_nutrition 함수 시작!")
    print("=" * 50)
    
    if request.method == 'POST' and request.FILES.get('nutrition_image'):
        try:
            print("✅ 1단계: 이미지 파일 받음")
            
            # 이미지 임시 저장
            nutrition_image = request.FILES['nutrition_image']
            temp_dir = 'media/temp'
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, nutrition_image.name)
            
            print(f"✅ 2단계: 저장 경로 생성 - {temp_path}")
            
            with open(temp_path, 'wb+') as f:
                for chunk in nutrition_image.chunks():
                    f.write(chunk)
            
            print("✅ 3단계: 이미지 저장 완료")
            
            # OCR 실행
            try:
                print("✅ 4단계: OCR 서비스 초기화 시작...")
                ocr_service = NutritionOCRService()
                print("✅ 4-1: OCR 서비스 초기화 완료!")
                
                print("✅ 5단계: 텍스트 추출 시작...")
                text = ocr_service.extract_text(temp_path)
                print(f"✅ 5-1: 추출된 텍스트: {text[:100]}...")  # 처음 100자만
                
            except Exception as ocr_error:
                print(f"❌ OCR 에러 발생: {ocr_error}")
                import traceback
                traceback.print_exc()
                return JsonResponse({
                    'success': False,
                    'error': f'OCR 실행 실패: {str(ocr_error)}'
                }, status=500)
            
            # 영양성분 추출
            print("✅ 6단계: 영양성분 추출 시작...")
            nutrition = NutritionExtractor.extract_all(text)
            print(f"✅ 6-1: 추출된 영양성분: {nutrition}")
            
            # 임시 파일 삭제
            try:
                os.remove(temp_path)
                print("✅ 7단계: 임시 파일 삭제 완료")
            except:
                print("⚠️ 임시 파일 삭제 실패 (무시)")
            
            print("✅ 8단계: 성공 응답 반환!")
            return JsonResponse({
                'success': True,
                'nutrition': nutrition
            })
        
        except Exception as e:
            print(f"❌❌❌ 전체 에러: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    print("❌ POST 요청이 아니거나 이미지가 없음")
    return JsonResponse({'success': False, 'error': '이미지가 없습니다.'}, status=400)

def detail(request, pk):
    target_post = Post.objects.get(id = pk)
    context = { 'post': target_post }
    return render(request, 'posts/detail.html', context=context)

def update(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'GET':
        form = PostForm(instance=post)
        context = {
            'form': form, 
            'post': post
        }
        return render(request, 'posts/update.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:detail', pk=pk)

def delete(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('/')

@csrf_exempt
def generate_hashtags(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image = request.FILES['image']
            temp_dir = 'media/temp'
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, image.name)
            
            with open(temp_path, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            
            hashtag_service = HashtagService()
            hashtags = hashtag_service.extract_hashtags(temp_path)
            
            try:
                os.remove(temp_path)
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'hashtags': hashtags
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': '이미지가 없습니다.'}, status=400)