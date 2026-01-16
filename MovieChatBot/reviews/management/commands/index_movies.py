from django.core.management.base import BaseCommand
from pathlib import Path
from dotenv import load_dotenv
from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from reviews.models import Review
import shutil

class Command(BaseCommand):
    help = "영화 데이터를 벡터 DB에 인덱싱 (FAISS)"

    def handle(self, *args, **options):
        BASE_DIR = Path(__file__).resolve().parents[3]
        load_dotenv(BASE_DIR / ".env")
        VS_DIR = BASE_DIR / "vector_store"

        movies = Review.objects.all()
        if not movies.exists():
            self.stdout.write(self.style.ERROR("❌ DB에 영화가 없습니다!"))
            return

        self.stdout.write(f"📚 {movies.count()}개 영화 로딩...")

        # 문서 생성
        docs = []
        for movie in movies:
            text = f"""제목: {movie.title}
장르: {movie.genre}
감독: {movie.director}
출연: {movie.actors}
평점: {movie.rating}/5
줄거리: {movie.content or movie.overview or '정보 없음'}"""

            docs.append(
                Document(
                    page_content=text,
                    metadata={"movie_id": movie.id, "title": movie.title},
                )
            )

        self.stdout.write(f"📄 {len(docs)}개 문서 생성")

        # 기존 벡터 DB 삭제
        if VS_DIR.exists():
            shutil.rmtree(VS_DIR)
        VS_DIR.mkdir(parents=True, exist_ok=True)

        # FAISS 임베딩 & 저장
        self.stdout.write("🔄 임베딩 중...")
        embeddings = UpstageEmbeddings(model="solar-embedding-1-large")

        # FAISS로 벡터 DB 생성 
        vectorstore = FAISS.from_documents(
            documents=docs,
            embedding=embeddings
        )

        # 저장
        vectorstore.save_local(str(VS_DIR))

        self.stdout.write(self.style.SUCCESS(f"✨ 완료! {VS_DIR}"))