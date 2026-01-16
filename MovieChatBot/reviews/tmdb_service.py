import os
import requests
from typing import List, Dict, Optional

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB_API_KEY가 .env 파일에 설정되지 않았습니다.")
    
    def get_popular_movies(self, page: int = 1, language: str = 'ko-KR') -> List[Dict]:
        # 인기 영화 목록 가져오기
        url = f"{self.BASE_URL}/movie/popular"
        params = {'api_key': self.api_key, 'language': language, 'page': page}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            print(f"TMDB API 요청 실패: {e}")
            return []
    
    def get_movie_details(self, movie_id: int, language: str = 'ko-KR') -> Optional[Dict]:
        # 영화 상세 정보 + 출연진/스태프
        url = f"{self.BASE_URL}/movie/{movie_id}"
        params = {'api_key': self.api_key, 'language': language, 'append_to_response': 'credits'}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"영화 상세 정보 요청 실패 (ID: {movie_id}): {e}")
            return None
    
    def get_poster_url(self, poster_path: Optional[str]) -> Optional[str]:
        # 포스터 전체 URL 생성
        return f"{self.IMAGE_BASE_URL}{poster_path}" if poster_path else None