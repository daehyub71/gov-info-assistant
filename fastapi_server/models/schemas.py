"""
Pydantic 데이터 모델 정의
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union, Literal
from uuid import UUID, uuid4
import re


from enum import Enum
from pydantic import (
    BaseModel, Field, validator, root_validator, 
    field_validator, model_validator
)

class MessageRole(str, Enum):
    """메시지 역할 열거형"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SessionStatus(str, Enum):
    """세션 상태 열거형"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class DifficultyLevel(str, Enum):
    """난이도 수준 열거형"""
    BEGINNER = "초급"
    INTERMEDIATE = "중급"
    ADVANCED = "고급"


class AgentStep(str, Enum):
    """Agent 처리 단계 열거형"""
    QUERY_ANALYSIS = "query_analysis"
    DOCUMENT_RETRIEVAL = "document_retrieval"
    CONTENT_PROCESSING = "content_processing"
    RESPONSE_GENERATION = "response_generation"
    COMPLETED = "completed"
    ERROR = "error"


class SortBy(str, Enum):
    """정렬 기준 열거형"""
    RELEVANCE = "relevance"
    DATE = "date"
    POPULARITY = "popularity"


# === 검색 관련 모델 ===

class SearchRequest(BaseModel):
    """검색 요청 모델"""
    
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="검색 질의"
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="문서 카테고리 필터"
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="최대 검색 결과 수"
    )
    session_id: Optional[str] = Field(
        None,
        max_length=100,
        description="세션 ID"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="추가 필터"
    )
    sort_by: SortBy = Field(
        default=SortBy.RELEVANCE,
        description="정렬 기준"
    )
    
    @field_validator('query')
    def normalize_query(cls, v):
        """질의 정규화"""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        
        # 공백 정규화
        normalized = re.sub(r'\s+', ' ', v.strip())
        
        # 길이 검증
        if len(normalized) < 2:
            raise ValueError("Query must be at least 2 characters long")
        
        return normalized
    
    @field_validator('category')
    def validate_category(cls, v):
        """카테고리 검증"""
        if v is not None:
            valid_categories = [
                "법령", "행정서비스", "세무", "복지", "교육", 
                "보건", "환경", "교통", "주거", "고용"
            ]
            if v not in valid_categories:
                # 유연한 카테고리 허용 (경고 로그만)
                pass
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "query": "주민등록등본 발급 방법",
                "category": "행정서비스",
                "max_results": 5,
                "session_id": "session-123",
                "filters": {"difficulty": "초급"},
                "sort_by": "relevance"
            }
        }


class DocumentResult(BaseModel):
    """문서 검색 결과 모델"""
    
    id: str = Field(..., description="문서 고유 ID")
    title: str = Field(..., min_length=1, max_length=200, description="문서 제목")
    content: str = Field(..., min_length=1, description="문서 내용")
    category: str = Field(..., max_length=50, description="문서 카테고리")
    published_date: str = Field(..., description="발행일 (YYYY-MM-DD)")
    difficulty: DifficultyLevel = Field(..., description="난이도 수준")
    score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="관련성 점수 (0-1)"
    )
    highlights: List[str] = Field(
        default_factory=list,
        description="하이라이트된 키워드"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="추가 메타데이터"
    )
    
    @field_validator('published_date')
    def validate_date_format(cls, v):
        """날짜 형식 검증"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v
    
    @field_validator('content')
    def validate_content_length(cls, v):
        """내용 길이 검증"""
        if len(v) > 10000:  # 10KB 제한
            return v[:10000] + "..."
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "doc_001",
                "title": "주민등록등본 발급 안내",
                "content": "주민등록등본은 온라인 또는 주민센터에서 발급받을 수 있습니다...",
                "category": "행정서비스",
                "published_date": "2024-01-15",
                "difficulty": "초급",
                "score": 0.95,
                "highlights": ["주민등록등본", "발급", "온라인"],
                "metadata": {
                    "author": "행정안전부",
                    "document_type": "안내서"
                }
            }
        }


class SearchResponse(BaseModel):
    """검색 응답 모델"""
    
    results: List[DocumentResult] = Field(
        default_factory=list,
        description="검색 결과 문서 목록"
    )
    summary: str = Field(
        ..., 
        min_length=1,
        max_length=1000,
        description="검색 결과 요약"
    )
    total_count: int = Field(
        ..., 
        ge=0,
        description="총 검색 결과 수"
    )
    processing_time: float = Field(
        ..., 
        ge=0.0,
        description="처리 시간 (초)"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        max_items=10,
        description="추천 검색어"
    )
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="전체 신뢰도 점수"
    )
    session_id: Optional[str] = Field(
        None,
        description="세션 ID"
    )
    
    @field_validator('results')
    def validate_results_consistency(cls, v, values):
        """결과 일관성 검증"""
        if 'total_count' in values:
            actual_count = len(v)
            # total_count는 전체 개수, results는 현재 페이지
            if actual_count > values['total_count']:
                raise ValueError("Results count cannot exceed total_count")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "id": "doc_001",
                        "title": "주민등록등본 발급 안내",
                        "content": "발급 방법 상세 안내...",
                        "category": "행정서비스",
                        "published_date": "2024-01-15",
                        "difficulty": "초급",
                        "score": 0.95,
                        "highlights": ["주민등록등본", "발급"],
                        "metadata": {}
                    }
                ],
                "summary": "주민등록등본은 온라인 또는 주민센터에서 발급 가능합니다.",
                "total_count": 1,
                "processing_time": 1.5,
                "suggestions": ["주민등록초본 발급", "가족관계증명서"],
                "confidence_score": 0.9,
                "session_id": "session-123"
            }
        }


# === 채팅 관련 모델 ===

class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="메시지 고유 ID"
    )
    role: MessageRole = Field(..., description="메시지 역할")
    content: str = Field(
        ..., 
        min_length=1,
        max_length=10000,
        description="메시지 내용"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="메시지 시간"
    )
    session_id: str = Field(..., description="세션 ID")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="메시지 메타데이터"
    )
    
    @field_validator('content')
    def validate_content(cls, v):
        """메시지 내용 검증"""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        
        # HTML 태그 제거 (보안)
        cleaned = re.sub(r'<[^>]+>', '', v.strip())
        if not cleaned:
            raise ValueError("Content cannot contain only HTML tags")
        
        return v.strip()
    
    @field_validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "msg-123",
                "role": "user",
                "content": "주민등록등본은 어떻게 발급받나요?",
                "timestamp": "2024-01-15T10:30:00Z",
                "session_id": "session-123",
                "metadata": {}
            }
        }


class ChatSession(BaseModel):
    """채팅 세션 모델"""
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="세션 고유 ID"
    )
    user_id: Optional[str] = Field(None, description="사용자 ID")
    title: str = Field(
        default="새로운 대화",
        max_length=100,
        description="세션 제목"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="마지막 업데이트 시간"
    )
    status: SessionStatus = Field(
        default=SessionStatus.ACTIVE,
        description="세션 상태"
    )
    message_count: int = Field(
        default=0,
        ge=0,
        description="메시지 수"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="세션 메타데이터"
    )
    
    @field_validator('updated_at')
    def validate_updated_at(cls, v, values):
        """업데이트 시간 검증"""
        if 'created_at' in values and v < values['created_at']:
            raise ValueError("Updated time cannot be before created time")
        return v
    
    @field_validator('title')
    def validate_title(cls, v):
        """제목 검증"""
        if not v or not v.strip():
            return "새로운 대화"
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "id": "session-123",
                "user_id": "user-456",
                "title": "주민등록 관련 문의",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "status": "active",
                "message_count": 4,
                "metadata": {
                    "category": "행정서비스",
                    "language": "ko"
                }
            }
        }


# === Agent 상태 관리 모델 ===

class AgentState(BaseModel):
    """Agent 워크플로우 상태 모델"""
    
    session_id: str = Field(..., description="세션 ID")
    user_query: str = Field(
        ..., 
        min_length=1,
        description="사용자 원본 질의"
    )
    processed_query: Optional[str] = Field(
        None,
        description="처리된 질의"
    )
    search_results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="검색 결과 데이터"
    )
    current_step: AgentStep = Field(
        default=AgentStep.QUERY_ANALYSIS,
        description="현재 처리 단계"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="컨텍스트 정보"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="처리 메타데이터"
    )
    error: Optional[str] = Field(
        None,
        description="에러 메시지"
    )
    
    @field_validator('user_query')
    def validate_user_query(cls, v):
        """사용자 질의 검증"""
        if not v or not v.strip():
            raise ValueError("User query is required")
        return v.strip()
    
    @field_validator('current_step')
    def validate_step_transition(cls, v, values):
        """단계 전환 검증"""
        # 에러 상태에서는 어떤 단계로든 전환 가능
        if v == AgentStep.ERROR:
            return v
        
        # 일반적인 단계 순서 검증 (선택적)
        valid_transitions = {
            AgentStep.QUERY_ANALYSIS: [AgentStep.DOCUMENT_RETRIEVAL, AgentStep.ERROR],
            AgentStep.DOCUMENT_RETRIEVAL: [AgentStep.CONTENT_PROCESSING, AgentStep.ERROR],
            AgentStep.CONTENT_PROCESSING: [AgentStep.RESPONSE_GENERATION, AgentStep.ERROR],
            AgentStep.RESPONSE_GENERATION: [AgentStep.COMPLETED, AgentStep.ERROR],
            AgentStep.COMPLETED: [AgentStep.QUERY_ANALYSIS, AgentStep.ERROR],  # 새 질의 시작 가능
            AgentStep.ERROR: list(AgentStep)  # 에러에서는 모든 단계로 복구 가능
        }
        
        return v
    
    @model_validator(mode='before')
    def validate_error_state(cls, values):
        """에러 상태 검증"""
        if values.get('current_step') == AgentStep.ERROR and not values.get('error'):
            raise ValueError("Error message is required when step is ERROR")
        return values
    
    def is_completed(self) -> bool:
        """완료 상태 확인"""
        return self.current_step == AgentStep.COMPLETED
    
    def is_error(self) -> bool:
        """에러 상태 확인"""
        return self.current_step == AgentStep.ERROR
    
    def add_context(self, key: str, value: Any) -> None:
        """컨텍스트 정보 추가"""
        self.context[key] = value
    
    def add_metadata(self, key: str, value: Any) -> None:
        """메타데이터 추가"""
        self.metadata[key] = value
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session-123",
                "user_query": "주민등록등본 발급 방법",
                "processed_query": "주민등록등본 발급",
                "search_results": [
                    {
                        "id": "doc_001",
                        "title": "주민등록등본 발급 안내",
                        "score": 0.95
                    }
                ],
                "current_step": "document_retrieval",
                "context": {
                    "category": "행정서비스",
                    "intent": "정보조회"
                },
                "metadata": {
                    "start_time": "2024-01-15T10:30:00Z",
                    "processing_times": {
                        "query_analysis": 0.5,
                        "document_search": 1.2
                    }
                },
                "error": None
            }
        }


# === 응답 모델 ===

class ChatMessageCreate(BaseModel):
    """채팅 메시지 생성 요청"""
    
    content: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "content": "주민등록등본은 어떻게 발급받나요?",
                "session_id": "session-123"
            }
        }


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    
    message: ChatMessage = Field(..., description="응답 메시지")
    session: ChatSession = Field(..., description="세션 정보")
    processing_time: float = Field(..., description="처리 시간")
    confidence: float = Field(..., ge=0.0, le=1.0, description="응답 신뢰도")
    
    class Config:
        schema_extra = {
            "example": {
                "message": {
                    "id": "msg-456",
                    "role": "assistant",
                    "content": "주민등록등본은 온라인 또는 주민센터에서 발급받을 수 있습니다.",
                    "timestamp": "2024-01-15T10:30:05Z",
                    "session_id": "session-123",
                    "metadata": {"sources": ["doc_001"]}
                },
                "session": {
                    "id": "session-123",
                    "title": "주민등록 관련 문의",
                    "status": "active",
                    "message_count": 2
                },
                "processing_time": 2.3,
                "confidence": 0.9
            }
        }


# === 에러 응답 모델 ===

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    
    error: str = Field(..., description="에러 유형")
    message: str = Field(..., description="에러 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="상세 정보")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="에러 발생 시간"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "요청 데이터가 유효하지 않습니다",
                "details": {"field": "query", "reason": "empty"},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# === 헬스체크 모델 (기존 health.py에서 이동) ===

class HealthStatus(BaseModel):
    """기본 헬스체크 응답"""
    status: str
    timestamp: str
    version: str
    uptime: float
    environment: str


class DetailedHealthStatus(BaseModel):
    """상세 헬스체크 응답"""
    status: str
    timestamp: str
    version: str
    uptime: float
    environment: str
    system: Dict[str, Any]
    services: Dict[str, Any]
    database: Dict[str, Any]
    disk_usage: Dict[str, Any]