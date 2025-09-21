"""
검색 API 라우터

문서 검색 관련 API 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

# 로컬 모듈 import 
from fastapi_server.models.search import SearchRequest, SearchResponse, DocumentResult
from fastapi_server.models.common import CategoryResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    문서 검색 API
    
    시민의 자연어 질의를 받아 관련 정부 공문서를 검색합니다.
    """
    try:
        logger.info(f"검색 요청: {request.query}")
        
        # TODO: 실제 Multi-Agent 워크플로우 실행
        # result = await workflow_service.process_search(request)
        
        # 임시 목 데이터
        mock_results = [
            DocumentResult(
                id="doc_001",
                title=f"'{request.query}' 관련 정부 정책 문서",
                content="이 문서는 관련 정책에 대한 상세한 정보를 담고 있습니다.",
                summary="정책 요약 정보입니다.",
                category=request.category or "복지 정책",
                score=0.95,
                date="2024-01-15",
                source_url="https://example.gov.kr/policy/001"
            ),
            DocumentResult(
                id="doc_002", 
                title=f"'{request.query}' 신청 방법 안내",
                content="신청 절차와 필요 서류에 대한 안내입니다.",
                summary="신청 방법 요약입니다.",
                category=request.category or "행정 서비스",
                score=0.87,
                date="2024-02-10",
                source_url="https://example.gov.kr/service/002"
            )
        ]
        
        response = SearchResponse(
            results=mock_results[:request.max_results],
            summary=f"'{request.query}'에 대한 {len(mock_results)} 개의 관련 문서를 찾았습니다.",
            total_count=len(mock_results),
            processing_time=1.2,
            suggestions=[
                f"{request.query} 신청 방법",
                f"{request.query} 자격 요건", 
                f"{request.query} 관련 법령"
            ],
            confidence_score=0.91
        )
        
        logger.info(f"검색 완료: {len(response.results)}개 결과")
        return response
        
    except Exception as e:
        logger.error(f"검색 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"검색 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/categories", response_model=CategoryResponse)
async def get_categories():
    """
    사용 가능한 카테고리 목록 조회
    """
    try:
        categories = [
            "복지 정책",
            "교육 정책",
            "주택 정책", 
            "창업 지원",
            "세금 혜택",
            "건강보험",
            "고용 정책",
            "문화 정책",
            "환경 정책",
            "기타"
        ]
        
        return CategoryResponse(
            categories=categories,
            total_count=len(categories)
        )
        
    except Exception as e:
        logger.error(f"카테고리 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="카테고리 조회 중 오류가 발생했습니다.")

@router.get("/popular")
async def get_popular_searches():
    """
    인기 검색어 조회
    """
    try:
        popular_queries = [
            "청년 주택 지원",
            "창업 정책",
            "실업급여 신청",
            "육아휴직 혜택",
            "세금 감면",
            "의료비 지원",
            "교육비 지원",
            "노인 복지"
        ]
        
        return {
            "popular_searches": popular_queries,
            "updated_at": "2024-01-15T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"인기 검색어 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="인기 검색어 조회 중 오류가 발생했습니다.")

@router.get("/health")
async def search_health_check():
    """검색 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "search",
        "timestamp": "2024-01-15T10:00:00Z"
    }
