"""
테스트 설정 및 픽스처

pytest 설정과 공통 테스트 픽스처를 정의합니다.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock
from typing import Generator

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 테스트용 환경변수 설정
import os
os.environ.update({
    "AOAI_ENDPOINT": "https://test.openai.azure.com/",
    "AOAI_API_KEY": "test_api_key",
    "AOAI_DEPLOY_GPT4O_MINI": "test-gpt-4o-mini",
    "AOAI_DEPLOY_GPT4O": "test-gpt-4o",
    "AOAI_DEPLOY_EMBED_3_LARGE": "test-embedding",
    "VECTOR_DB_PATH": "./tests/data/test_vector_db",
    "SESSION_DB_PATH": "./tests/data/test_sessions.db",
    "LOG_LEVEL": "DEBUG",
    "DEBUG": "True",
    "ENVIRONMENT": "test"
})

@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_azure_openai():
    """Azure OpenAI 클라이언트 모킹"""
    mock = Mock()
    
    # 채팅 완성 모킹
    mock.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="테스트 응답입니다."))
    ]
    
    # 임베딩 모킹
    mock.embeddings.create.return_value.data = [
        Mock(embedding=[0.1, 0.2, 0.3] * 256)  # 768차원 벡터
    ]
    
    return mock

@pytest.fixture
def sample_search_request():
    """샘플 검색 요청"""
    from fastapi_server.models.search import SearchRequest
    
    return SearchRequest(
        query="청년 주택 지원 정책",
        category="주택 정책",
        max_results=5
    )

@pytest.fixture
def sample_chat_request():
    """샘플 채팅 요청"""
    from fastapi_server.models.chat import ChatRequest
    
    return ChatRequest(
        message="청년 주택 지원에 대해 알려주세요",
        session_id="test_session_123"
    )

@pytest.fixture
def sample_documents():
    """샘플 문서 데이터"""
    return [
        {
            "id": "doc_001",
            "title": "청년 주택 지원 정책 안내",
            "content": "청년을 위한 다양한 주택 지원 정책을 안내합니다.",
            "category": "주택 정책",
            "date": "2024-01-15",
            "keywords": ["청년", "주택", "지원"]
        },
        {
            "id": "doc_002", 
            "title": "창업 지원 제도 개요",
            "content": "창업을 원하는 청년을 위한 지원 제도입니다.",
            "category": "창업 지원",
            "date": "2024-01-20",
            "keywords": ["창업", "청년", "지원"]
        }
    ]

@pytest.fixture
def test_agent_state():
    """테스트용 Agent 상태"""
    from fastapi_server.core.agents.base import AgentState
    
    return AgentState(
        user_query="청년 주택 정책에 대해 알려주세요",
        session_id="test_session"
    )

@pytest.fixture
def temp_test_dir(tmp_path):
    """임시 테스트 디렉토리"""
    # 테스트용 데이터 디렉토리 생성
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    vector_db_dir = data_dir / "vector_db"
    vector_db_dir.mkdir()
    
    return tmp_path

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, temp_test_dir):
    """테스트 환경 자동 설정"""
    # 테스트용 경로 설정
    monkeypatch.setenv("VECTOR_DB_PATH", str(temp_test_dir / "data" / "vector_db"))
    monkeypatch.setenv("SESSION_DB_PATH", str(temp_test_dir / "data" / "sessions.db"))

# pytest 설정
def pytest_configure(config):
    """pytest 설정"""
    # 커스텀 마커 등록
    config.addinivalue_line("markers", "slow: 느린 테스트 마킹")
    config.addinivalue_line("markers", "integration: 통합 테스트 마킹")
    config.addinivalue_line("markers", "unit: 단위 테스트 마킹")
    config.addinivalue_line("markers", "asyncio: 비동기 테스트 마킹")

# 테스트 유틸리티 함수
def assert_valid_response(response_data: dict, required_fields: list):
    """응답 데이터 유효성 검사"""
    assert isinstance(response_data, dict)
    for field in required_fields:
        assert field in response_data
        assert response_data[field] is not None

def create_mock_vector_db():
    """Mock Vector DB 생성"""
    mock_db = Mock()
    mock_db.search.return_value = [
        {
            "id": "doc_001",
            "score": 0.95,
            "metadata": {
                "title": "테스트 문서",
                "category": "테스트"
            }
        }
    ]
    return mock_db

def create_test_session():
    """테스트 세션 생성"""
    return {
        "id": "test_session_123",
        "created_at": "2024-01-15T10:00:00Z",
        "status": "active"
    }
