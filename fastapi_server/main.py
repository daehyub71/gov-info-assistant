"""
정부 공문서 AI 검색 서비스 - FastAPI 메인 애플리케이션

Multi-Agent 시스템을 활용한 정부 공문서 검색 및 상담 API 서버입니다.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

# 프로젝트 루트 경로 설정
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 로컬 모듈 import
from fastapi_server.core.config import get_settings
from fastapi_server.api import search, chat, health

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    logger.info("🚀 정부 공문서 AI 검색 서비스 시작")
    
    # Vector DB 초기화 (추후 구현)
    # await initialize_vector_db()
    
    yield  # 애플리케이션 실행
    
    # 종료 시 실행
    logger.info("🛑 정부 공문서 AI 검색 서비스 종료")

def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성 및 설정"""
    
    settings = get_settings()
    
    app = FastAPI(
        title="정부 공문서 AI 검색 서비스",
        description="시민 친화적인 정부 공문서 검색 및 상담 API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",  # Streamlit 개발 서버
            "http://127.0.0.1:8501",
            settings.CLIENT_URL if settings.CLIENT_URL else "http://localhost:8501"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 신뢰할 수 있는 호스트 미들웨어
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*"]  # 개발용, 프로덕션에서는 제한 필요
    )
    
    # API 라우터 등록
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    
    return app

# 애플리케이션 인스턴스 생성
app = create_app()

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "정부 공문서 AI 검색 서비스",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드
        log_level="info"
    )
