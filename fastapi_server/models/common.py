"""
공통 데이터 모델

여러 모듈에서 공통으로 사용되는 데이터 모델들을 정의합니다.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CategoryResponse(BaseModel):
    """카테고리 목록 응답 모델"""
    categories: List[str] = Field(..., description="사용 가능한 카테고리 목록")
    total_count: int = Field(..., description="총 카테고리 수")

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 메시지")
    error_code: Optional[str] = Field(None, description="에러 코드")
    details: Optional[Dict[str, Any]] = Field(None, description="에러 상세 정보")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="에러 발생 시간")

class SuccessResponse(BaseModel):
    """성공 응답 모델"""
    message: str = Field(..., description="성공 메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="추가 데이터")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="응답 시간")

class HealthStatus(Enum):
    """서비스 상태 열거형"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

class ProcessingStatus(Enum):
    """처리 상태 열거형"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DocumentType(Enum):
    """문서 타입 열거형"""
    POLICY = "policy"
    REGULATION = "regulation"
    GUIDE = "guide"
    FAQ = "faq"
    FORM = "form"
    OTHER = "other"

class SourceInfo(BaseModel):
    """소스 정보 모델"""
    title: str = Field(..., description="소스 제목")
    url: Optional[str] = Field(None, description="소스 URL")
    type: str = Field(..., description="소스 타입")
    reliability: Optional[float] = Field(None, ge=0, le=1, description="신뢰도 점수")

class MetricData(BaseModel):
    """메트릭 데이터 모델"""
    name: str = Field(..., description="메트릭 이름")
    value: float = Field(..., description="메트릭 값")
    unit: Optional[str] = Field(None, description="단위")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="측정 시간")

class PaginationInfo(BaseModel):
    """페이지네이션 정보 모델"""
    page: int = Field(default=1, ge=1, description="현재 페이지")
    page_size: int = Field(default=10, ge=1, le=100, description="페이지 크기")
    total_count: int = Field(..., ge=0, description="전체 항목 수")
    total_pages: int = Field(..., ge=0, description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_previous: bool = Field(..., description="이전 페이지 존재 여부")

class BaseTimestampModel(BaseModel):
    """타임스탬프가 포함된 기본 모델"""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="생성 시간")
    updated_at: Optional[str] = Field(None, description="수정 시간")

class ValidationError(BaseModel):
    """유효성 검사 에러 모델"""
    field: str = Field(..., description="에러가 발생한 필드")
    message: str = Field(..., description="에러 메시지")
    value: Optional[Any] = Field(None, description="잘못된 값")

class BulkResponse(BaseModel):
    """대량 처리 응답 모델"""
    total_processed: int = Field(..., ge=0, description="처리된 총 항목 수")
    successful: int = Field(..., ge=0, description="성공한 항목 수")
    failed: int = Field(..., ge=0, description="실패한 항목 수")
    errors: List[ValidationError] = Field(default_factory=list, description="발생한 에러 목록")
    processing_time: float = Field(..., ge=0, description="처리 시간(초)")
