from django.core.management.base import BaseCommand
from reviews.models import Review
from reviews.tmdb_service import TMDBService

class Command(BaseCommand):
    help = 'TMDB에서 인기 영화 가져오기'
    
    def add_arguments(self, parser):
        parser.add_argument('--pages', type=int, default=2, help='가져올 페이지 수')
    
    def handle(self, *args, **options):
        pages = options['pages']
        tmdb = TMDBService()
        total_created = 0
        total_skipped = 0
        
        self.stdout.write(f"📡 TMDB에서 {pages}페이지 영화 가져오는 중...\n")
        
        for page in range(1, pages + 1):
            self.stdout.write(f"  페이지 {page}/{pages} 처리 중...")
            movies = tmdb.get_popular_movies(page=page)
            
            for movie in movies:
                tmdb_id = movie.get('id')
                
                # 중복 확인
                if Review.objects.filter(tmdb_id=tmdb_id).exists():
                    total_skipped += 1
                    continue
                
                # 상세 정보 가져오기
                details = tmdb.get_movie_details(tmdb_id)
                if not details:
                    continue
                
                # 감독 추출
                director = "정보 없음"
                if details.get('credits') and details['credits'].get('crew'):
                    directors = [c['name'] for c in details['credits']['crew'] if c['job'] == 'Director']
                    director = ', '.join(directors[:2]) if directors else "정보 없음"
                
                # 배우 추출 (최대 3명)
                actors = "정보 없음"
                if details.get('credits') and details['credits'].get('cast'):
                    cast_list = [a['name'] for a in details['credits']['cast'][:3]]
                    actors = ', '.join(cast_list) if cast_list else "정보 없음"
                
                # 장르 매핑
                genre_map = {
                    28: '액션', 35: '코미디', 18: '드라마', 878: 'SF',
                    53: '스릴러', 10749: '로맨스', 16: '애니메이션',
                    99: '다큐멘터리', 27: '호러', 14: '판타지'
                }
                genre_ids = details.get('genre_ids', []) or [g['id'] for g in details.get('genres', [])]
                genre = genre_map.get(genre_ids[0] if genre_ids else 18, '드라마')
                
                # 개봉년도
                release_date = details.get('release_date', '')
                release_year = int(release_date[:4]) if release_date else 2024
                
                # DB 저장
                Review.objects.create(
                    title=details.get('title', '제목 없음'),
                    release_year=release_year,
                    genre=genre,
                    rating=round(details.get('vote_average', 0) / 2, 1),  # 10점 → 5점
                    director=director,
                    actors=actors,
                    running_time=details.get('runtime', 120),
                    content=details.get('overview', '줄거리 정보 없음'),
                    tmdb_id=tmdb_id,
                    poster_path=details.get('poster_path'),
                    overview=details.get('overview'),
                    vote_average=details.get('vote_average'),
                    is_tmdb=True
                )
                
                total_created += 1
                self.stdout.write(f"    ✅ {details.get('title')}")
        
        self.stdout.write(self.style.SUCCESS(f"\n✨ 완료! 추가: {total_created}개 | 건너뜀: {total_skipped}개"))