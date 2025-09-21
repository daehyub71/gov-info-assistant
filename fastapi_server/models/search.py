"""
검색 관련 데이터 모델

검색 API의 요청/응답 모델들을 정의합니다.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from .common import SourceInfo, BaseTimestampModel

class SearchRequest(BaseModel):
    """검색 요청 모델"""
    
    query: str = Field(..., min_length=1, max_length=500, description="검색 쿼리")
    category: Optional[str] = Field(None, description="카테고리 필터")
    max_results: int = Field(default=5, ge=1, le=20, description="최대 결과 수")
    session_id: Optional[str] = Field(None, description="세션 ID")
    include_summary: bool = Field(default=True, description="요약 포함 여부")
    
    @validator('query')
    def validate_query(cls, v):
        """쿼리 유효성 검사"""
        if not v or not v.strip():
            raise ValueError('검색어를 입력해주세요.')
        
        # 특수 문자 제한 (기본적인 것만)
        if len(v.strip()) < 2:
            raise ValueError('검색어는 2글자 이상 입력해주세요.')
            
        return v.strip()

class DocumentResult(BaseModel):
    """문서 검색 결과 모델"""
    
    id: str = Field(..., description="문서 고유 ID")
    title: str = Field(..., description="문서 제목")
    content: str = Field(..., description="문서 내용")
    summary: Optional[str] = Field(None, description="문서 요약")
    category: str = Field(..., description="문서 카테고리")
    score: float = Field(..., ge=0, le=1, description="관련도 점수")
    date: Optional[str] = Field(None, description="문서 발행일")
    source_url: Optional[str] = Field(None, description="원본 문서 URL")
    
    # 추가 메타데이터
    keywords: List[str] = Field(default_factory=list, description="추출된 키워드")
    difficulty_level: Optional[str] = Field(None, description="난이도 (쉬움/보통/어려움)")
    document_type: Optional[str] = Field(None, description="문서 타입")
    tags: List[str] = Field(default_factory=list, description="태그 목록")

class SearchResponse(BaseModel):
    """검색 응답 모델"""
    
    results: List[DocumentResult] = Field(..., description="검색 결과 목록")
    summary: str = Field(..., description="검색 결과 요약")
    total_count: int = Field(..., ge=0, description="총 검색 결과 수")
    processing_time: float = Field(..., ge=0, description="처리 시간(초)")
    suggestions: List[str] = Field(default_factory=list, description="관련 검색어 제안")
    confidence_score: float = Field(..., ge=0, le=1, description="검색 신뢰도")
    
    # 메타데이터
    query_info: Optional[Dict[str, Any]] = Field(None, description="쿼리 분석 정보")
    filters_applied: List[str] = Field(default_factory=list, description="적용된 필터")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="검색 시간")

class SearchHistory(BaseTimestampModel):
    """검색 히스토리 모델"""
    
    id: str = Field(..., description="히스토리 ID")
    query: str = Field(..., description="검색 쿼리")
    session_id: Optional[str] = Field(None, description="세션 ID")
    results_count: int = Field(..., ge=0, description="결과 수")
    processing_time: float = Field(..., ge=0, description="처리 시간")
    user_feedback: Optional[str] = Field(None, description="사용자 피드백")

class PopularSearch(BaseModel):
    """인기 검색어 모델"""
    
    query: str = Field(..., description="검색어")
    count: int = Field(..., ge=1, description="검색 횟수")
    rank: int = Field(..., ge=1, description="순위")
    category: Optional[str] = Field(None, description="주요 카테고리")
    trend: Optional[str] = Field(None, description="트렌드 (상승/하락/유지)")

class SearchAnalytics(BaseModel):
    """검색 분석 데이터 모델"""
    
    date: str = Field(..., description="날짜")
    total_searches: int = Field(..., ge=0, description="총 검색 수")
    unique_queries: int = Field(..., ge=0, description="고유 쿼리 수")
    avg_results_per_search: float = Field(..., ge=0, description="검색당 평균 결과 수")
    avg_processing_time: float = Field(..., ge=0, description="평균 처리 시간")
    top_categories: List[str] = Field(default_factory=list, description="인기 카테고리")
    success_rate: float = Field(..., ge=0, le=1, description="성공률")

class SearchFilter(BaseModel):
    """검색 필터 모델"""
    
    categories: List[str] = Field(default_factory=list, description="카테고리 필터")
    date_range: Optional[Dict[str, str]] = Field(None, description="날짜 범위")
    difficulty_levels: List[str] = Field(default_factory=list, description="난이도 필터")
    document_types: List[str] = Field(default_factory=list, description="문서 타입 필터")
    min_score: Optional[float] = Field(None, ge=0, le=1, description="최소 관련도 점수")

class SearchSuggestion(BaseModel):
    """검색 제안 모델"""
    
    text: str = Field(..., description="제안 텍스트")
    type: str = Field(..., description="제안 타입 (autocomplete/related/popular)")
    score: float = Field(..., ge=0, le=1, description="제안 점수")
    context: Optional[str] = Field(None, description="제안 컨텍스트")
