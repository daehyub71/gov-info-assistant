"""
API 라우터 단위 테스트

FastAPI 라우터들의 기본 동작을 테스트합니다.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch
import json
from datetime import datetime

# 테스트할 라우터들 import
from fastapi_server.api.v1.search import router as search_router
from fastapi_server.api.v1.chat import router as chat_router


@pytest.fixture
def app():
    """테스트용 FastAPI 앱 생성"""
    app = FastAPI()
    app.include_router(search_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    return app


@pytest.fixture
def client(app):
    """테스트 클라이언트 생성"""
    return TestClient(app)


class TestSearchRouter:
    """검색 API 라우터 테스트"""
    
    def test_search_health_check(self, client):
        """검색 서비스 헬스체크 테스트"""
        response = client.get("/api/v1/search/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "search"
    
    @patch('fastapi_server.api.v1.search.get_search_service')
    def test_search_query_success(self, mock_search_service, client):
        """문서 검색 성공 테스트"""
        # Mock 검색 서비스 설정
        mock_service = Mock()
        mock_search_service.return_value = mock_service
        
        # 검색 요청 데이터
        search_data = {
            "query": "주민등록등본 발급",
            "category": "행정절차",
            "max_results": 5
        }
        
        response = client.post("/api/v1/search/query", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 검증
        assert "results" in data
        assert "summary" in data
        assert "total_count" in data
        assert "processing_time" in data
        assert "confidence_score" in data
        assert "suggestions" in data
        
        # 기본 더미 데이터 검증
        assert len(data["results"]) >= 1
        assert data["confidence_score"] > 0
    
    def test_search_query_invalid_data(self, client):
        """잘못된 검색 요청 테스트"""
        # 빈 쿼리
        response = client.post("/api/v1/search/query", json={})
        assert response.status_code == 422  # Validation error
        
        # 잘못된 max_results
        response = client.post("/api/v1/search/query", json={
            "query": "test",
            "max_results": -1
        })
        assert response.status_code == 422
    
    def test_get_categories(self, client):
        """카테고리 목록 조회 테스트"""
        response = client.get("/api/v1/search/categories")
        
        assert response.status_code == 200
        data = response.json()
        
        # 리스트 형태의 응답 확인
        assert isinstance(data, list)
        assert len(data) > 0
        
        # 카테고리 구조 확인
        category = data[0]
        assert "id" in category
        assert "name" in category
        assert "count" in category
    
    def test_get_popular_queries(self, client):
        """인기 검색어 조회 테스트"""
        response = client.get("/api/v1/search/popular")
        
        assert response.status_code == 200
        data = response.json()
        
        # 리스트 형태의 응답 확인
        assert isinstance(data, list)
        assert len(data) > 0
        
        # 모든 요소가 문자열인지 확인
        assert all(isinstance(query, str) for query in data)


class TestChatRouter:
    """채팅 API 라우터 테스트"""
    
    def test_chat_health_check(self, client):
        """채팅 서비스 헬스체크 테스트"""
        response = client.get("/api/v1/chat/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "chat"
    
    @patch('fastapi_server.api.v1.chat.get_chat_service')
    def test_send_message_success(self, mock_chat_service, client):
        """메시지 전송 성공 테스트"""
        # Mock 채팅 서비스 설정
        mock_service = Mock()
        mock_chat_service.return_value = mock_service
        
        # 메시지 요청 데이터
        message_data = {
            "message": "안녕하세요",
            "session_id": "test_session_123"
        }
        
        response = client.post("/api/v1/chat/message", json=message_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 검증
        assert "message" in data
        assert "session_id" in data
        assert "message_id" in data
        assert "timestamp" in data
        assert "confidence_score" in data
        assert "suggested_questions" in data
        assert "processing_time" in data
        
        # 데이터 타입 검증
        assert isinstance(data["suggested_questions"], list)
        assert data["confidence_score"] >= 0
        assert data["processing_time"] >= 0
    
    def test_send_message_invalid_data(self, client):
        """잘못된 메시지 요청 테스트"""
        # 빈 메시지
        response = client.post("/api/v1/chat/message", json={})
        assert response.status_code == 422
        
        # 메시지 없음
        response = client.post("/api/v1/chat/message", json={
            "session_id": "test"
        })
        assert response.status_code == 422
    
    @patch('fastapi_server.api.v1.chat.get_chat_service')
    def test_create_session_success(self, mock_chat_service, client):
        """세션 생성 성공 테스트"""
        mock_service = Mock()
        mock_chat_service.return_value = mock_service
        
        # 세션 생성 요청
        session_data = {
            "user_id": "test_user"
        }
        
        response = client.post("/api/v1/chat/session", json=session_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 검증
        assert "session_id" in data
        assert "created_at" in data
        
        # 세션 ID가 유효한 형태인지 확인
        assert data["session_id"].startswith("session_")
        assert len(data["session_id"]) > 10
    
    def test_create_session_no_user_id(self, client):
        """사용자 ID 없이 세션 생성 테스트"""
        response = client.post("/api/v1/chat/session", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
    
    @patch('fastapi_server.api.v1.chat.get_chat_service')
    def test_get_chat_history(self, mock_chat_service, client):
        """채팅 히스토리 조회 테스트"""
        mock_service = Mock()
        mock_chat_service.return_value = mock_service
        
        session_id = "test_session_123"
        response = client.get(f"/api/v1/chat/history/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 검증
        assert "session_id" in data
        assert "messages" in data
        assert "total_count" in data
        assert "created_at" in data
        
        # 데이터 타입 검증
        assert isinstance(data["messages"], list)
        assert isinstance(data["total_count"], int)
        assert data["session_id"] == session_id
    
    def test_get_chat_history_with_limit(self, client):
        """제한된 메시지 수로 히스토리 조회 테스트"""
        session_id = "test_session_123"
        limit = 10
        
        response = client.get(f"/api/v1/chat/history/{session_id}?limit={limit}")
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
    
    @patch('fastapi_server.api.v1.chat.get_chat_service')
    def test_delete_session(self, mock_chat_service, client):
        """세션 삭제 테스트"""
        mock_service = Mock()
        mock_chat_service.return_value = mock_service
        
        session_id = "test_session_123"
        response = client.delete(f"/api/v1/chat/session/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 검증
        assert "message" in data
        assert "session_id" in data
        assert data["session_id"] == session_id


class TestAPIIntegration:
    """API 통합 테스트"""
    
    def test_v1_health_check(self, client):
        """API v1 전체 헬스체크 테스트"""
        # v1 라우터가 포함되지 않았으므로 개별 서비스 헬스체크만 테스트
        
        # 검색 서비스 헬스체크
        response = client.get("/api/v1/search/health")
        assert response.status_code == 200
        
        # 채팅 서비스 헬스체크
        response = client.get("/api/v1/chat/health")
        assert response.status_code == 200
    
    def test_api_error_handling(self, client):
        """API 오류 처리 테스트"""
        # 존재하지 않는 엔드포인트
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # 잘못된 HTTP 메서드
        response = client.put("/api/v1/search/query")
        assert response.status_code == 405
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """동시 요청 처리 테스트"""
        import asyncio
        import httpx
        
        async def make_request():
            async with httpx.AsyncClient(app=client.app, base_url="http://test") as ac:
                response = await ac.get("/api/v1/search/health")
                return response.status_code
        
        # 10개의 동시 요청
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 모든 요청이 성공했는지 확인
        assert all(status_code == 200 for status_code in results)


# 픽스처 및 헬퍼 함수들
@pytest.fixture
def sample_search_request():
    """샘플 검색 요청 데이터"""
    return {
        "query": "주민등록등본 발급 방법",
        "category": "행정절차",
        "max_results": 5
    }


@pytest.fixture
def sample_chat_message():
    """샘플 채팅 메시지 데이터"""
    return {
        "message": "안녕하세요. 출산 지원금에 대해 알고 싶습니다.",
        "session_id": "test_session_123"
    }


def test_data_models_validation():
    """데이터 모델 유효성 검사 테스트"""
    # TODO: Day 1에서 생성한 Pydantic 모델들의 유효성 검사
    # 실제 모델이 구현되면 테스트 추가
    pass


if __name__ == "__main__":
    pytest.main([__file__])
