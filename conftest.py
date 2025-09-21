"""
pytest 전역 설정 및 픽스처
"""
import os
import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 테스트 환경 설정
os.environ["TESTING"] = "true"
os.environ["AOAI_ENDPOINT"] = "https://test.openai.azure.com/"
os.environ["AOAI_API_KEY"] = "test-api-key-12345678901234567890"  # 32글자 이상

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi_server.main import app
from fastapi_server.core.config import TestSettings
from fastapi_server.core.logging_config import get_logger

# 테스트 로거
logger = get_logger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 설정"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> TestSettings:
    """테스트 설정 픽스처"""
    return TestSettings()


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """임시 디렉토리 생성"""
    temp_path = Path(tempfile.mkdtemp())
    logger.info(f"Created temporary directory: {temp_path}")
    
    yield temp_path
    
    # 정리
    if temp_path.exists():
        shutil.rmtree(temp_path)
        logger.info(f"Cleaned up temporary directory: {temp_path}")


@pytest.fixture(scope="session")
def test_data_dir(temp_dir: Path) -> Path:
    """테스트 데이터 디렉토리 생성"""
    data_dir = temp_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 서브 디렉토리 생성
    (data_dir / "vector_db").mkdir(exist_ok=True)
    (data_dir / "documents").mkdir(exist_ok=True)
    
    return data_dir


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """FastAPI 테스트 클라이언트"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """비동기 HTTP 클라이언트"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def mock_azure_openai():
    """Azure OpenAI 모킹"""
    with patch("openai.AzureOpenAI") as mock_client:
        # ChatCompletion 모킹
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message=Mock(content="테스트 응답입니다."))
        ]
        mock_completion.usage = Mock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
        
        mock_client.return_value.chat.completions.create.return_value = mock_completion
        
        # Embedding 모킹
        mock_embedding = Mock()
        mock_embedding.data = [
            Mock(embedding=[0.1] * 3072)  # text-embedding-3-large dimension
        ]
        mock_embedding.usage = Mock(total_tokens=8)
        
        mock_client.return_value.embeddings.create.return_value = mock_embedding
        
        logger.info("Azure OpenAI client mocked")
        yield mock_client


@pytest.fixture(scope="function")
def mock_faiss_index():
    """FAISS 인덱스 모킹"""
    with patch("faiss.IndexIVFFlat") as mock_index:
        mock_instance = Mock()
        mock_instance.is_trained = True
        mock_instance.ntotal = 100
        
        # 검색 결과 모킹
        mock_instance.search.return_value = (
            [[0.8, 0.7, 0.6]],  # scores
            [[0, 1, 2]]         # indices
        )
        
        mock_index.return_value = mock_instance
        logger.info("FAISS index mocked")
        yield mock_instance


@pytest.fixture(scope="function")
def sample_documents():
    """샘플 문서 데이터"""
    return [
        {
            "id": "doc_001",
            "title": "정부 조직법 개정안",
            "content": "정부 조직법 개정안에 대한 내용입니다.",
            "category": "법령",
            "published_date": "2024-01-15",
            "difficulty": "중급"
        },
        {
            "id": "doc_002", 
            "title": "주민등록 발급 절차",
            "content": "주민등록등본 발급 절차에 대한 안내입니다.",
            "category": "행정서비스",
            "published_date": "2024-01-20",
            "difficulty": "초급"
        },
        {
            "id": "doc_003",
            "title": "세금 신고 방법",
            "content": "개인소득세 신고 방법에 대한 상세 안내입니다.",
            "category": "세무",
            "published_date": "2024-02-01",
            "difficulty": "고급"
        }
    ]


@pytest.fixture(scope="function")
def sample_chat_messages():
    """샘플 채팅 메시지"""
    return [
        {
            "role": "user",
            "content": "주민등록등본은 어떻게 발급받나요?",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "role": "assistant", 
            "content": "주민등록등본은 온라인 또는 주민센터에서 발급받을 수 있습니다.",
            "timestamp": "2024-01-15T10:00:05Z"
        }
    ]


@pytest.fixture(scope="function")
def mock_session_db(test_data_dir: Path):
    """테스트용 세션 데이터베이스"""
    db_path = test_data_dir / "test_sessions.db"
    
    # SQLite 인메모리 데이터베이스 사용
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 테이블 생성 (실제 모델이 구현되면 수정)
    # Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal
    
    # 정리
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(autouse=True)
def setup_test_logging():
    """테스트 로깅 설정"""
    logger.info("Starting test execution")
    yield
    logger.info("Test execution completed")


@pytest.fixture(scope="function")
def mock_vector_store():
    """벡터 저장소 모킹"""
    mock_store = Mock()
    mock_store.search.return_value = [
        {
            "id": "doc_001",
            "score": 0.85,
            "metadata": {"title": "테스트 문서", "category": "테스트"}
        }
    ]
    mock_store.add_documents.return_value = True
    return mock_store


@pytest.fixture(scope="function")
def auth_headers():
    """인증 헤더"""
    return {"Authorization": "Bearer test-token"}


# 테스트 데이터 생성 헬퍼
class TestDataFactory:
    """테스트 데이터 생성 팩토리"""
    
    @staticmethod
    def create_search_request(query: str = "테스트 질의") -> dict:
        """검색 요청 데이터 생성"""
        return {
            "query": query,
            "category": None,
            "max_results": 5,
            "session_id": "test-session-123"
        }
    
    @staticmethod
    def create_chat_message(content: str = "안녕하세요") -> dict:
        """채팅 메시지 데이터 생성"""
        return {
            "content": content,
            "session_id": "test-session-123",
            "user_id": "test-user"
        }
    
    @staticmethod
    def create_document_metadata() -> dict:
        """문서 메타데이터 생성"""
        return {
            "title": "테스트 문서",
            "category": "테스트",
            "published_date": "2024-01-01",
            "difficulty": "초급",
            "keywords": ["테스트", "문서"]
        }


@pytest.fixture(scope="session")
def test_data_factory():
    """테스트 데이터 팩토리 픽스처"""
    return TestDataFactory


# 마커 정의
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow

# 테스트 설정
def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line("markers", "unit: 단위 테스트")
    config.addinivalue_line("markers", "integration: 통합 테스트") 
    config.addinivalue_line("markers", "e2e: End-to-End 테스트")
    config.addinivalue_line("markers", "slow: 느린 테스트")


def pytest_collection_modifyitems(config, items):
    """테스트 항목 수정"""
    for item in items:
        # 비동기 테스트 마킹
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


# 테스트 실행 전후 훅
def pytest_runtest_setup(item):
    """각 테스트 실행 전"""
    logger.info(f"Starting test: {item.name}")


def pytest_runtest_teardown(item, nextitem):
    """각 테스트 실행 후"""
    logger.info(f"Finished test: {item.name}")


# 테스트 실패 시 정보 수집
@pytest.fixture(autouse=True)
def capture_test_info(request):
    """테스트 정보 캡처"""
    test_name = request.node.name
    start_time = pytest.current_time = __import__('time').time()
    
    yield
    
    end_time = __import__('time').time()
    duration = end_time - start_time
    
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        logger.error(f"Test failed: {test_name}, Duration: {duration:.2f}s")
    else:
        logger.info(f"Test passed: {test_name}, Duration: {duration:.2f}s")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 리포트 생성"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)