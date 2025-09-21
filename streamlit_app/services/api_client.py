"""
API 클라이언트 서비스

FastAPI 서버와의 HTTP 통신을 담당합니다.
"""

import httpx
import streamlit as st
from typing import Dict, List, Any, Optional
import asyncio
import json
from datetime import datetime

class APIClient:
    """FastAPI 서버와의 통신을 담당하는 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        API 클라이언트 초기화
        
        Args:
            base_url: FastAPI 서버 기본 URL
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 30.0
    
    async def search_documents(
        self, 
        query: str, 
        category: Optional[str] = None,
        max_results: int = 5,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        문서 검색 API 호출
        
        Args:
            query: 검색 쿼리
            category: 카테고리 필터
            max_results: 최대 결과 수
            session_id: 세션 ID
            
        Returns:
            검색 결과 딕셔너리
        """
        search_data = {
            "query": query,
            "max_results": max_results
        }
        
        if category:
            search_data["category"] = category
        if session_id:
            search_data["session_id"] = session_id
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/search/query",
                    json=search_data
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.TimeoutException:
            return {"error": "요청 시간이 초과되었습니다. 다시 시도해주세요."}
        except httpx.RequestError as e:
            return {"error": f"연결 오류가 발생했습니다: {str(e)}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"서버 오류가 발생했습니다: {e.response.status_code}"}
    
    async def send_chat_message(
        self, 
        message: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        채팅 메시지 전송 API 호출
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID
            
        Returns:
            AI 응답 딕셔너리
        """
        chat_data = {"message": message}
        if session_id:
            chat_data["session_id"] = session_id
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/chat/message",
                    json=chat_data
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            return {"error": f"채팅 서비스 오류: {str(e)}"}
    
    async def get_categories(self) -> List[str]:
        """
        사용 가능한 카테고리 목록 조회
        
        Returns:
            카테고리 리스트
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/search/categories")
                response.raise_for_status()
                data = response.json()
                return data.get("categories", [])
        
        except Exception as e:
            st.error(f"카테고리 조회 실패: {str(e)}")
            return ["복지 정책", "교육 정책", "주택 정책", "창업 지원", "세금 혜택", "기타"]
    
    async def create_session(self) -> Optional[str]:
        """
        새로운 채팅 세션 생성
        
        Returns:
            세션 ID 또는 None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/v1/chat/session")
                response.raise_for_status()
                data = response.json()
                return data.get("session_id")
        
        except Exception as e:
            st.error(f"세션 생성 실패: {str(e)}")
            return None
    
    async def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        채팅 히스토리 조회
        
        Args:
            session_id: 세션 ID
            
        Returns:
            채팅 히스토리 리스트
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/chat/history/{session_id}"
                )
                response.raise_for_status()
                data = response.json()
                return data.get("messages", [])
        
        except Exception as e:
            st.error(f"히스토리 조회 실패: {str(e)}")
            return []
    
    async def health_check(self) -> bool:
        """
        서버 상태 확인
        
        Returns:
            서버 정상 여부
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/health")
                return response.status_code == 200
        except:
            return False

# 싱글톤 클라이언트 인스턴스
@st.cache_resource
def get_api_client() -> APIClient:
    """API 클라이언트 싱글톤 인스턴스 반환"""
    # 환경변수에서 서버 URL 가져오기
    import os
    server_url = os.getenv("SERVER_URL", "http://localhost:8000")
    return APIClient(server_url)

# 비동기 함수를 동기적으로 실행하는 헬퍼 함수
def run_async(coro):
    """비동기 함수를 동기적으로 실행"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)
