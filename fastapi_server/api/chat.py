"""
채팅 API 라우터

대화형 상담 관련 API 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
import uuid
from datetime import datetime

# 로컬 모듈 import
from fastapi_server.models.chat import ChatRequest, ChatResponse, ChatSession, ChatMessage

router = APIRouter()
logger = logging.getLogger(__name__)

# 임시 세션 저장소 (추후 SQLite로 대체)
temp_sessions = {}

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    채팅 메시지 전송 및 AI 응답 생성
    
    시민의 질문에 대해 AI Agent가 친화적인 답변을 제공합니다.
    """
    try:
        logger.info(f"채팅 메시지: {request.message}")
        
        # 세션 ID 처리
        session_id = request.session_id or str(uuid.uuid4())
        
        # TODO: 실제 Multi-Agent 워크플로우 실행
        # response = await workflow_service.process_chat(request)
        
        # 임시 AI 응답 생성
        ai_response = generate_mock_ai_response(request.message)
        
        # 세션에 메시지 저장
        if session_id not in temp_sessions:
            temp_sessions[session_id] = []
        
        temp_sessions[session_id].extend([
            {
                "role": "user",
                "content": request.message,
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant", 
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            }
        ])
        
        response = ChatResponse(
            response=ai_response,
            session_id=session_id,
            message_id=str(uuid.uuid4()),
            processing_time=2.1,
            confidence_score=0.89,
            related_questions=[
                "이 정책의 신청 자격은 무엇인가요?",
                "신청 방법을 자세히 알려주세요",
                "비슷한 다른 정책도 있나요?"
            ],
            sources=[
                {
                    "title": "관련 정책 문서",
                    "url": "https://example.gov.kr/policy",
                    "type": "document"
                }
            ]
        )
        
        logger.info(f"채팅 응답 생성 완료: {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"채팅 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}")

@router.post("/session", response_model=dict)
async def create_chat_session():
    """
    새로운 채팅 세션 생성
    """
    try:
        session_id = str(uuid.uuid4())
        temp_sessions[session_id] = []
        
        logger.info(f"새 세션 생성: {session_id}")
        
        return {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"세션 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 생성 중 오류가 발생했습니다.")

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    채팅 히스토리 조회
    """
    try:
        if session_id not in temp_sessions:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        messages = temp_sessions[session_id]
        
        return {
            "session_id": session_id,
            "messages": messages,
            "total_count": len(messages),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"히스토리 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="히스토리 조회 중 오류가 발생했습니다.")

@router.delete("/session/{session_id}")
async def delete_chat_session(session_id: str):
    """
    채팅 세션 삭제
    """
    try:
        if session_id in temp_sessions:
            del temp_sessions[session_id]
            logger.info(f"세션 삭제: {session_id}")
        
        return {
            "message": "세션이 삭제되었습니다.",
            "session_id": session_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"세션 삭제 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 삭제 중 오류가 발생했습니다.")

def generate_mock_ai_response(user_message: str) -> str:
    """
    임시 AI 응답 생성 함수
    
    Args:
        user_message: 사용자 메시지
        
    Returns:
        AI 응답 텍스트
    """
    # 키워드 기반 간단한 응답 생성
    if "주택" in user_message or "집" in user_message:
        return """
        안녕하세요! 주택 관련 정책에 대해 문의해주셨네요. 😊
        
        현재 다양한 주택 지원 정책이 있습니다:
        
        **주요 주택 정책:**
        1. 청년 전세임대 주택
        2. 신혼부부 특별공급
        3. 생애최초 주택구입 지원
        4. 주택청약 종합저축
        
        더 구체적인 정보가 필요하시면 어떤 부분이 궁금하신지 알려주세요!
        """
    
    elif "창업" in user_message or "사업" in user_message:
        return """
        창업 지원 정책에 관심이 있으시군요! 🚀
        
        **주요 창업 지원 프로그램:**
        1. 청년창업 사관학교
        2. 창업기업 세액감면
        3. 신용보증기금 지원
        4. K-Startup 그랜드 챌린지
        
        어떤 분야의 창업을 계획하고 계신가요? 더 맞춤형 정보를 드릴 수 있습니다.
        """
    
    elif "실업" in user_message or "구직" in user_message:
        return """
        구직활동 지원에 대해 문의해주셨네요. 💼
        
        **고용 지원 제도:**
        1. 구직급여 (실업급여)
        2. 국민취업지원제도
        3. 청년구직활동지원금
        4. 직업훈련 지원
        
        현재 상황을 좀 더 알려주시면 적합한 지원제도를 안내해드릴게요!
        """
    
    else:
        return f"""
        '{user_message}'에 대해 문의해주셨네요.
        
        관련 정보를 찾아보고 있습니다. 좀 더 구체적으로 어떤 부분이 궁금하신지 
        알려주시면 더 정확한 정보를 제공해드릴 수 있습니다.
        
        예를 들어:
        - 신청 자격이 궁금하신가요?
        - 신청 방법을 알고 싶으신가요?
        - 필요한 서류가 궁금하신가요?
        
        언제든 편하게 물어보세요! 😊
        """

@router.get("/health")
async def chat_health_check():
    """채팅 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "chat",
        "active_sessions": len(temp_sessions),
        "timestamp": datetime.now().isoformat()
    }
