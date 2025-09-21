"""
API v1 라우터 집합

모든 v1 API 라우터를 통합하여 관리합니다.
"""

from fastapi import APIRouter
from .search import router as search_router
from .chat import router as chat_router

# v1 API 라우터 생성
router = APIRouter(prefix="/v1")

# 개별 라우터들을 메인 라우터에 등록
router.include_router(search_router)
router.include_router(chat_router)

# 헬스체크 엔드포인트
@router.get("/health")
async def api_health_check():
    """API v1 헬스체크"""
    return {
        "status": "healthy",
        "version": "v1",
        "services": ["search", "chat"]
    }
