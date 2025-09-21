"""
대화형 채팅 API 라우터

이 모듈은 시민과의 대화형 상담 관련 API 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from fastapi_server.models.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSession,
    ChatHistoryResponse,
    SessionCreateRequest,
    SessionCreateResponse
)
from fastapi_server.core.services.chat_service import ChatService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# ChatService 의존성 주입
def get_chat_service() -> ChatService:
    """채팅 서비스 인스턴스를 반환합니다."""
    return ChatService()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatMessageResponse:
    """
    사용자 메시지를 처리하고 AI 응답을 생성합니다.
    
    Args:
        request: 채팅 메시지 요청
        chat_service: 채팅 서비스 인스턴스
        
    Returns:
        ChatMessageResponse: AI 응답
        
    Raises:
        HTTPException: 메시지 처리 실패 시
    """
    try:
        logger.info(f"메시지 수신: session_id={request.session_id}, message='{request.message[:50]}...'")
        
        # TODO: 실제 LangGraph 워크플로우 연동 (Day 3에서)
        # 현재는 더미 응답 반환
        dummy_response = ChatMessageResponse(
            message="안녕하세요! 정부 공문서 관련 질문에 답변드리겠습니다. 어떤 도움이 필요하신가요?",
            session_id=request.session_id,
            message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            confidence_score=0.9,
            suggested_questions=[
                "주민등록등본 발급 방법을 알려주세요",
                "출산 지원금 신청 절차는 어떻게 되나요?",
                "사업자 등록 필요 서류가 무엇인가요?"
            ],
            processing_time=1.2
        )
        
        logger.info(f"응답 생성 완료: message_id={dummy_response.message_id}")
        return dummy_response
        
    except Exception as e:
        logger.error(f"메시지 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"메시지 처리 중 오류가 발생했습니다: {str(e)}")


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = 50,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatHistoryResponse:
    """
    특정 세션의 채팅 히스토리를 조회합니다.
    
    Args:
        session_id: 세션 ID
        limit: 조회할 메시지 수 제한
        chat_service: 채팅 서비스 인스턴스
        
    Returns:
        ChatHistoryResponse: 채팅 히스토리
        
    Raises:
        HTTPException: 히스토리 조회 실패 시
    """
    try:
        logger.info(f"채팅 히스토리 조회: session_id={session_id}, limit={limit}")
        
        # TODO: 실제 DB에서 히스토리 조회 (Day 4에서)
        # 현재는 더미 데이터 반환
        dummy_history = ChatHistoryResponse(
            session_id=session_id,
            messages=[],
            total_count=0,
            created_at=datetime.now()
        )
        
        logger.info(f"히스토리 조회 완료: {dummy_history.total_count}개 메시지")
        return dummy_history
        
    except Exception as e:
        logger.error(f"히스토리 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="채팅 히스토리를 가져올 수 없습니다.")


@router.post("/session", response_model=SessionCreateResponse)
async def create_session(
    request: SessionCreateRequest,
    chat_service: ChatService = Depends(get_chat_service)
) -> SessionCreateResponse:
    """
    새로운 채팅 세션을 생성합니다.
    
    Args:
        request: 세션 생성 요청
        chat_service: 채팅 서비스 인스턴스
        
    Returns:
        SessionCreateResponse: 생성된 세션 정보
        
    Raises:
        HTTPException: 세션 생성 실패 시
    """
    try:
        logger.info(f"새 세션 생성 요청: user_id={request.user_id}")
        
        # TODO: 실제 세션 생성 로직 (Day 4에서)
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        response = SessionCreateResponse(
            session_id=session_id,
            created_at=datetime.now(),
            expires_at=None  # 2시간 후 만료 설정은 실제 구현에서
        )
        
        logger.info(f"세션 생성 완료: session_id={session_id}")
        return response
        
    except Exception as e:
        logger.error(f"세션 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 생성에 실패했습니다.")


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    채팅 세션을 삭제합니다.
    
    Args:
        session_id: 삭제할 세션 ID
        chat_service: 채팅 서비스 인스턴스
        
    Returns:
        dict: 삭제 결과
        
    Raises:
        HTTPException: 세션 삭제 실패 시
    """
    try:
        logger.info(f"세션 삭제 요청: session_id={session_id}")
        
        # TODO: 실제 세션 삭제 로직 (Day 4에서)
        
        logger.info(f"세션 삭제 완료: session_id={session_id}")
        return {"message": "세션이 성공적으로 삭제되었습니다.", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"세션 삭제 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 삭제에 실패했습니다.")


@router.get("/health")
async def chat_health_check():
    """채팅 서비스 헬스체크"""
    return {"status": "healthy", "service": "chat"}
