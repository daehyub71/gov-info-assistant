"""
채팅 관련 데이터 모델

채팅 API의 요청/응답 모델들을 정의합니다.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from .common import SourceInfo, BaseTimestampModel

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    
    message: str = Field(..., min_length=1, max_length=1000, description="사용자 메시지")
    session_id: Optional[str] = Field(None, description="세션 ID")
    context: Optional[Dict[str, Any]] = Field(None, description="추가 컨텍스트")
    
    @validator('message')
    def validate_message(cls, v):
        """메시지 유효성 검사"""
        if not v or not v.strip():
            raise ValueError('메시지를 입력해주세요.')
        return v.strip()

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    
    response: str = Field(..., description="AI 응답")
    session_id: str = Field(..., description="세션 ID")
    message_id: str = Field(..., description="메시지 고유 ID")
    processing_time: float = Field(..., ge=0, description="처리 시간(초)")
    confidence_score: float = Field(..., ge=0, le=1, description="응답 신뢰도")
    
    # 추가 정보
    related_questions: List[str] = Field(default_factory=list, description="관련 질문 제안")
    sources: List[SourceInfo] = Field(default_factory=list, description="참조 소스")
    intent: Optional[str] = Field(None, description="감지된 의도")
    sentiment: Optional[str] = Field(None, description="감정 분석 결과")
    
    # 메타데이터
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="응답 시간")

class ChatMessage(BaseTimestampModel):
    """채팅 메시지 모델"""
    
    id: str = Field(..., description="메시지 ID")
    session_id: str = Field(..., description="세션 ID")
    role: str = Field(..., description="역할 (user/assistant)")
    content: str = Field(..., description="메시지 내용")
    
    # 추가 정보
    intent: Optional[str] = Field(None, description="의도")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="신뢰도")
    processing_time: Optional[float] = Field(None, ge=0, description="처리 시간")
    feedback: Optional[str] = Field(None, description="사용자 피드백")

class ChatSession(BaseTimestampModel):
    """채팅 세션 모델"""
    
    id: str = Field(..., description="세션 ID")
    status: str = Field(default="active", description="세션 상태")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    
    # 세션 통계
    message_count: int = Field(default=0, ge=0, description="총 메시지 수")
    last_activity: str = Field(default_factory=lambda: datetime.now().isoformat(), description="마지막 활동 시간")
    
    # 메타데이터
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    ip_address: Optional[str] = Field(None, description="IP 주소")
    context: Optional[Dict[str, Any]] = Field(None, description="세션 컨텍스트")

class ConversationSummary(BaseModel):
    """대화 요약 모델"""
    
    session_id: str = Field(..., description="세션 ID")
    summary: str = Field(..., description="대화 요약")
    key_topics: List[str] = Field(default_factory=list, description="주요 토픽")
    user_intents: List[str] = Field(default_factory=list, description="사용자 의도")
    resolution_status: str = Field(..., description="해결 상태")
    satisfaction_score: Optional[float] = Field(None, ge=0, le=1, description="만족도 점수")

class ChatAnalytics(BaseModel):
    """채팅 분석 데이터 모델"""
    
    date: str = Field(..., description="날짜")
    total_sessions: int = Field(..., ge=0, description="총 세션 수")
    total_messages: int = Field(..., ge=0, description="총 메시지 수")
    avg_messages_per_session: float = Field(..., ge=0, description="세션당 평균 메시지 수")
    avg_response_time: float = Field(..., ge=0, description="평균 응답 시간")
    common_intents: List[str] = Field(default_factory=list, description="일반적인 의도")
    satisfaction_rate: float = Field(..., ge=0, le=1, description="만족도")

class ChatFeedback(BaseTimestampModel):
    """채팅 피드백 모델"""
    
    id: str = Field(..., description="피드백 ID")
    session_id: str = Field(..., description="세션 ID")
    message_id: str = Field(..., description="메시지 ID")
    rating: int = Field(..., ge=1, le=5, description="평점 (1-5)")
    comment: Optional[str] = Field(None, description="피드백 댓글")
    feedback_type: str = Field(..., description="피드백 타입")

class QuickReply(BaseModel):
    """빠른 답변 모델"""
    
    text: str = Field(..., description="답변 텍스트")
    action: Optional[str] = Field(None, description="실행할 액션")
    payload: Optional[Dict[str, Any]] = Field(None, description="추가 데이터")

class ChatIntent(BaseModel):
    """채팅 의도 모델"""
    
    name: str = Field(..., description="의도 이름")
    confidence: float = Field(..., ge=0, le=1, description="신뢰도")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="추출된 엔티티")
    context: Optional[Dict[str, Any]] = Field(None, description="의도 컨텍스트")
