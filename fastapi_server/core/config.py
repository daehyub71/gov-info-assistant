"""
환경변수 관리 및 애플리케이션 설정
"""
import os
from typing import Optional, List
# 수정
from pydantic_settings import BaseSettings
from pydantic import validator
from pathlib import Path


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 애플리케이션 기본 설정
    APP_NAME: str = "정부 공문서 AI 검색 서비스"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "일반시민을 위한 정부 공문서 AI 검색 서비스"
    DEBUG: bool = False
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # URL 설정
    CLIENT_URL: str = "http://localhost:8501"
    SERVER_URL: str = "http://localhost:8000"
    API_V1_PREFIX: str = "/api/v1"
    
    # Azure OpenAI 설정
    AOAI_ENDPOINT: str
    AOAI_API_KEY: str
    AOAI_DEPLOY_GPT4O_MINI: str = "gpt-4o-mini"
    AOAI_DEPLOY_GPT4O: str = "gpt-4o"
    AOAI_DEPLOY_EMBED_3_LARGE: str = "text-embedding-3-large"
    AOAI_API_VERSION: str = "2024-02-01"
    
    # 데이터베이스 설정
    VECTOR_DB_PATH: str = "./data/vector_db"
    SESSION_DB_PATH: str = "./data/sessions.db"
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "JSON"
    LOG_FILE_PATH: str = "./logs/app.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # 보안 설정
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS 설정
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://localhost:3000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000"
    ]
    
    # API 제한 설정
    RATE_LIMIT_PER_MINUTE: int = 30
    MAX_REQUEST_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Vector DB 설정
    VECTOR_DIMENSION: int = 3072  # text-embedding-3-large dimension
    FAISS_INDEX_TYPE: str = "IVF"
    FAISS_NLIST: int = 100
    MAX_SEARCH_RESULTS: int = 10
    
    # 캐시 설정
    CACHE_TTL: int = 3600  # 1시간
    CACHE_MAX_SIZE: int = 1000
    
    # 세션 설정
    SESSION_EXPIRE_HOURS: int = 2
    MAX_SESSIONS_PER_USER: int = 5
    
    # LLM 설정
    DEFAULT_TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 4096
    TIMEOUT_SECONDS: int = 30
    
    # 검색 설정
    DEFAULT_SEARCH_LIMIT: int = 5
    MIN_SIMILARITY_SCORE: float = 0.7
    
    @validator("AOAI_ENDPOINT")
    def validate_aoai_endpoint(cls, v):
        if not v:
            raise ValueError("AOAI_ENDPOINT는 필수 설정입니다")
        if not v.startswith("https://"):
            raise ValueError("AOAI_ENDPOINT는 https://로 시작해야 합니다")
        return v
    
    @validator("AOAI_API_KEY")
    def validate_aoai_api_key(cls, v):
        if not v:
            raise ValueError("AOAI_API_KEY는 필수 설정입니다")
        if len(v) < 32:
            raise ValueError("AOAI_API_KEY가 너무 짧습니다")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL은 {valid_levels} 중 하나여야 합니다")
        return v.upper()
    
    @validator("VECTOR_DB_PATH", "SESSION_DB_PATH")
    def validate_db_paths(cls, v):
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    @validator("LOG_FILE_PATH")
    def validate_log_path(cls, v):
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    @property
    def database_url(self) -> str:
        """SQLite 데이터베이스 URL 생성"""
        return f"sqlite:///{self.SESSION_DB_PATH}"
    
    @property
    def is_development(self) -> bool:
        """개발 환경 여부 확인"""
        return self.DEBUG or self.LOG_LEVEL == "DEBUG"
    
    @property
    def cors_origins(self) -> List[str]:
        """CORS 허용 오리진 목록"""
        if self.DEBUG:
            return ["*"]
        return self.ALLOWED_ORIGINS
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class TestSettings(Settings):
    """테스트용 설정 클래스"""
    
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # 테스트용 데이터베이스
    VECTOR_DB_PATH: str = "./tests/data/vector_db"
    SESSION_DB_PATH: str = "./tests/data/test_sessions.db"
    LOG_FILE_PATH: str = "./tests/logs/test.log"
    
    # 테스트용 Azure OpenAI (Mock 사용)
    AOAI_ENDPOINT: str = "https://test.openai.azure.com/"
    AOAI_API_KEY: str = "test-api-key-32-characters-long"
    
    # 캐시 비활성화
    CACHE_TTL: int = 0
    
    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """환경에 따른 설정 반환"""
    if os.getenv("TESTING"):
        return TestSettings()
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()