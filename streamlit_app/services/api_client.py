"""
API 클라이언트 서비스

FastAPI 서버와 통신하는 클라이언트 서비스를 제공합니다.
"""

import httpx
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import streamlit as st
import os

# 환경변수에서 서버 URL 가져오기
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

logger = logging.getLogger(__name__)


class APIClient:
    """FastAPI 서버와 통신하는 클라이언트 클래스"""
    
    def __init__(self, base_url: str = SERVER_URL, timeout: float = 30.0):
        """
        API 클라이언트 초기화
        
        Args:
            base_url: API 서버 기본 URL
            timeout: 요청 타임아웃 (초)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
        
        logger.info(f"API 클라이언트 초기화: {self.base_url}")
    
    async def _get_session(self) -> httpx.AsyncClient:
        """비동기 HTTP 세션 반환"""
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "GovInfoAssistant-Client/1.0"
                }
            )
        return self.session
    
    async def close(self):
        """세션 정리"""
        if self.session and not self.session.is_closed:
            await self.session.aclose()
    
    # 검색 관련 API
    async def search_documents(
        self, 
        query: str, 
        category: Optional[str] = None,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        문서 검색 API 호출
        
        Args:
            query: 검색 질의
            category: 카테고리 필터
            max_results: 최대 결과 수
            
        Returns:
            Dict: 검색 결과
        """
        try:
            session = await self._get_session()
            
            payload = {
                "query": query,
                "category": category,
                "max_results": max_results
            }
            
            logger.info(f"문서 검색 요청: {query}")
            
            response = await session.post("/api/v1/search/query", json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"검색 완료: {result.get('total_count', 0)}개 결과")
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 오류: {e.response.status_code} - {e.response.text}")
            raise Exception(f"검색 요청 실패: {e.response.status_code}")
        except Exception as e:
            logger.error(f"검색 중 오류: {str(e)}")
            raise Exception(f"검색 중 오류가 발생했습니다: {str(e)}")
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        카테고리 목록 조회
        
        Returns:
            List: 카테고리 목록
        """
        try:
            session = await self._get_session()
            
            response = await session.get("/api/v1/search/categories")
            response.raise_for_status()
            
            categories = response.json()
            logger.info(f"카테고리 조회 완료: {len(categories)}개")
            
            return categories
            
        except Exception as e:
            logger.error(f"카테고리 조회 중 오류: {str(e)}")
            raise Exception(f"카테고리 정보를 가져올 수 없습니다: {str(e)}")
    
    async def get_popular_queries(self) -> List[str]:
        """
        인기 검색어 조회
        
        Returns:
            List: 인기 검색어 목록
        """
        try:
            session = await self._get_session()
            
            response = await session.get("/api/v1/search/popular")
            response.raise_for_status()
            
            queries = response.json()
            logger.info(f"인기 검색어 조회 완료: {len(queries)}개")
            
            return queries
            
        except Exception as e:
            logger.error(f"인기 검색어 조회 중 오류: {str(e)}")
            return []  # 실패시 빈 목록 반환
    
    # 채팅 관련 API
    async def send_message(
        self, 
        message: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        채팅 메시지 전송
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID
            
        Returns:
            Dict: AI 응답
        """
        try:
            session = await self._get_session()
            
            payload = {
                "message": message,
                "session_id": session_id
            }
            
            logger.info(f"메시지 전송: session_id={session_id}")
            
            response = await session.post("/api/v1/chat/message", json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"응답 수신: message_id={result.get('message_id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"메시지 전송 중 오류: {str(e)}")
            raise Exception(f"메시지 전송에 실패했습니다: {str(e)}")
    
    async def create_session(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        새 채팅 세션 생성
        
        Args:
            user_id: 사용자 ID (선택적)
            
        Returns:
            Dict: 세션 정보
        """
        try:
            session = await self._get_session()
            
            payload = {"user_id": user_id} if user_id else {}
            
            response = await session.post("/api/v1/chat/session", json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"세션 생성 완료: session_id={result.get('session_id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"세션 생성 중 오류: {str(e)}")
            raise Exception(f"세션 생성에 실패했습니다: {str(e)}")
    
    async def get_chat_history(
        self, 
        session_id: str, 
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        채팅 히스토리 조회
        
        Args:
            session_id: 세션 ID
            limit: 조회할 메시지 수
            
        Returns:
            Dict: 채팅 히스토리
        """
        try:
            session = await self._get_session()
            
            response = await session.get(
                f"/api/v1/chat/history/{session_id}",
                params={"limit": limit}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"히스토리 조회 완료: {result.get('total_count', 0)}개 메시지")
            
            return result
            
        except Exception as e:
            logger.error(f"히스토리 조회 중 오류: {str(e)}")
            raise Exception(f"채팅 히스토리를 가져올 수 없습니다: {str(e)}")
    
    # 헬스체크
    async def health_check(self) -> bool:
        """
        API 서버 헬스체크
        
        Returns:
            bool: 서버 상태 (True: 정상, False: 비정상)
        """
        try:
            session = await self._get_session()
            
            response = await session.get("/api/v1/health", timeout=5.0)
            response.raise_for_status()
            
            result = response.json()
            return result.get("status") == "healthy"
            
        except Exception as e:
            logger.error(f"헬스체크 실패: {str(e)}")
            return False


# Streamlit에서 사용하기 위한 동기 래퍼 함수들
class SyncAPIClient:
    """동기식 API 클라이언트 (Streamlit용)"""
    
    def __init__(self):
        self.async_client = APIClient()
    
    def _run_async(self, coro):
        """비동기 함수를 동기적으로 실행"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def search_documents(self, query: str, category: Optional[str] = None, max_results: int = 5) -> Dict[str, Any]:
        """동기식 문서 검색"""
        return self._run_async(
            self.async_client.search_documents(query, category, max_results)
        )
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """동기식 카테고리 조회"""
        return self._run_async(self.async_client.get_categories())
    
    def get_popular_queries(self) -> List[str]:
        """동기식 인기 검색어 조회"""
        return self._run_async(self.async_client.get_popular_queries())
    
    def send_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """동기식 메시지 전송"""
        return self._run_async(
            self.async_client.send_message(message, session_id)
        )
    
    def create_session(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """동기식 세션 생성"""
        return self._run_async(self.async_client.create_session(user_id))
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> Dict[str, Any]:
        """동기식 채팅 히스토리 조회"""
        return self._run_async(
            self.async_client.get_chat_history(session_id, limit)
        )
    
    def health_check(self) -> bool:
        """동기식 헬스체크"""
        return self._run_async(self.async_client.health_check())
    
    def close(self):
        """세션 정리"""
        self._run_async(self.async_client.close())


# Streamlit에서 사용할 API 클라이언트 인스턴스 생성 함수
@st.cache_resource
def get_api_client() -> SyncAPIClient:
    """캐시된 API 클라이언트 인스턴스 반환"""
    return SyncAPIClient()


# 편의 함수들
def safe_api_call(func, *args, **kwargs):
    """
    안전한 API 호출 (에러 처리 포함)
    
    Args:
        func: 호출할 함수
        *args, **kwargs: 함수 인수
        
    Returns:
        결과 또는 None (에러 시)
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")
        logger.error(f"API 호출 오류: {str(e)}")
        return None


def check_server_connection() -> bool:
    """
    서버 연결 상태 확인
    
    Returns:
        bool: 연결 상태
    """
    client = get_api_client()
    return safe_api_call(client.health_check) or False
