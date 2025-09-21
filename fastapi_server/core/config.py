"""
애플리케이션 설정 관리

환경변수 및 설정 정보를 관리합니다.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # Azure OpenAI 설정
    AOAI_ENDPOINT: str = Field(..., env="AOAI_ENDPOINT")
    AOAI_API_KEY: str = Field(..., env="AOAI_API_KEY")
    AOAI_DEPLOY_GPT4O_MINI: str = Field(default="gpt-4o-mini", env="AOAI_DEPLOY_GPT4O_MINI")
    AOAI_DEPLOY_GPT4O: str = Field(default="gpt-4o", env="AOAI_DEPLOY_GPT4O")
    AOAI_DEPLOY_EMBED_3_LARGE: str = Field(default="text-embedding-3-large", env="AOAI_DEPLOY_EMBED_3_LARGE")
    
    # 애플리케이션 설정
    CLIENT_URL: Optional[str] = Field(default="http://localhost:8501", env="CLIENT_URL")
    SERVER_URL: Optional[str] = Field(default="http://localhost:8000", env="SERVER_URL")
    
    # 데이터베이스 설정
    VECTOR_DB_PATH: str = Field(default="./data/vector_db", env="VECTOR_DB_PATH")
    SESSION_DB_PATH: str = Field(default="./data/sessions.db", env="SESSION_DB_PATH")
    
    # 로깅 설정
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # API 설정
    API_RATE_LIMIT: int = Field(default=30, env="API_RATE_LIMIT")  # 분당 요청 수
    MAX_REQUEST_SIZE: int = Field(default=1048576, env="MAX_REQUEST_SIZE")  # 1MB
    
    # 검색 설정
    DEFAULT_MAX_RESULTS: int = Field(default=5, env="DEFAULT_MAX_RESULTS")
    SEARCH_TIMEOUT: float = Field(default=30.0, env="SEARCH_TIMEOUT")
    
    # 세션 설정
    SESSION_TIMEOUT: int = Field(default=7200, env="SESSION_TIMEOUT")  # 2시간 (초)
    MAX_SESSIONS: int = Field(default=1000, env="MAX_SESSIONS")
    
    # 캐시 설정
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1시간 (초)
    MAX_CACHE_SIZE: int = Field(default=100, env="MAX_CACHE_SIZE")
    
    # 개발/프로덕션 설정
    DEBUG: bool = Field(default=True, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스 반환 (캐시됨)"""
    return Settings()

def get_azure_openai_config() -> dict:
    """Azure OpenAI 설정 반환"""
    settings = get_settings()
    return {
        "endpoint": settings.AOAI_ENDPOINT,
        "api_key": settings.AOAI_API_KEY,
        "deployments": {
            "gpt4o_mini": settings.AOAI_DEPLOY_GPT4O_MINI,
            "gpt4o": settings.AOAI_DEPLOY_GPT4O,
            "embedding": settings.AOAI_DEPLOY_EMBED_3_LARGE
        }
    }

def get_database_config() -> dict:
    """데이터베이스 설정 반환"""
    settings = get_settings()
    return {
        "vector_db_path": settings.VECTOR_DB_PATH,
        "session_db_path": settings.SESSION_DB_PATH
    }

def get_logging_config() -> dict:
    """로깅 설정 반환"""
    settings = get_settings()
    return {
        "level": settings.LOG_LEVEL,
        "format": settings.LOG_FORMAT,
        "handlers": ["console", "file"] if settings.DEBUG else ["file"]
    }

def ensure_directories() -> None:
    """필요한 디렉토리 생성"""
    settings = get_settings()
    
    directories = [
        os.path.dirname(settings.VECTOR_DB_PATH),
        os.path.dirname(settings.SESSION_DB_PATH),
        "./logs"
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

# 애플리케이션 시작 시 디렉토리 생성
ensure_directories()
