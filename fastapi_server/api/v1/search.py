"""
정부 공문서 검색 API 라우터

이 모듈은 정부 공문서 검색 관련 API 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from fastapi_server.models.search import (
    SearchRequest, 
    SearchResponse, 
    DocumentResult,
    CategoryResponse
)
from fastapi_server.core.services.search_service import SearchService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

# SearchService 의존성 주입
def get_search_service() -> SearchService:
    """검색 서비스 인스턴스를 반환합니다."""
    return SearchService()


@router.post("/query", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service)
) -> SearchResponse:
    """
    정부 공문서 검색을 수행합니다.
    
    Args:
        request: 검색 요청 정보
        search_service: 검색 서비스 인스턴스
        
    Returns:
        SearchResponse: 검색 결과
        
    Raises:
        HTTPException: 검색 실패 시
    """
    try:
        logger.info(f"검색 요청: query='{request.query}', category={request.category}")
        
        # TODO: 실제 검색 로직 구현 (Day 2-3에서)
        # 현재는 더미 응답 반환
        dummy_results = [
            DocumentResult(
                id="doc_001",
                title="샘플 정부 공문서",
                content="이것은 샘플 문서 내용입니다.",
                category="정책안내",
                confidence_score=0.95,
                source_url="https://example.gov.kr/doc001",
                publish_date="2024-01-15"
            )
        ]
        
        response = SearchResponse(
            results=dummy_results,
            summary="검색 요청에 대한 샘플 응답입니다.",
            total_count=1,
            processing_time=0.5,
            suggestions=["관련 검색어 1", "관련 검색어 2"],
            confidence_score=0.95
        )
        
        logger.info(f"검색 완료: {len(response.results)}개 결과")
        return response
        
    except Exception as e:
        logger.error(f"검색 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories() -> List[CategoryResponse]:
    """
    사용 가능한 문서 카테고리 목록을 반환합니다.
    
    Returns:
        List[CategoryResponse]: 카테고리 목록
    """
    try:
        # TODO: 실제 카테고리 데이터 로드 (Day 5에서)
        categories = [
            CategoryResponse(id="policy", name="정책안내", count=150),
            CategoryResponse(id="procedure", name="행정절차", count=320),
            CategoryResponse(id="welfare", name="복지혜택", count=89),
            CategoryResponse(id="tax", name="세금정보", count=156),
            CategoryResponse(id="business", name="사업지원", count=203),
        ]
        
        logger.info(f"카테고리 목록 반환: {len(categories)}개")
        return categories
        
    except Exception as e:
        logger.error(f"카테고리 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="카테고리 정보를 가져올 수 없습니다.")


@router.get("/popular", response_model=List[str])
async def get_popular_queries() -> List[str]:
    """
    인기 검색어 목록을 반환합니다.
    
    Returns:
        List[str]: 인기 검색어 목록
    """
    try:
        # TODO: 실제 인기 검색어 통계 (Day 6에서)
        popular_queries = [
            "주민등록 발급",
            "출산 지원금",
            "사업자 등록",
            "건강보험 혜택",
            "교육 지원 프로그램"
        ]
        
        logger.info(f"인기 검색어 반환: {len(popular_queries)}개")
        return popular_queries
        
    except Exception as e:
        logger.error(f"인기 검색어 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="인기 검색어를 가져올 수 없습니다.")


@router.get("/health")
async def search_health_check():
    """검색 서비스 헬스체크"""
    return {"status": "healthy", "service": "search"}
