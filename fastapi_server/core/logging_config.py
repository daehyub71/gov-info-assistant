"""
로깅 설정 모듈 - JSON 포맷 로깅
"""
import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

from fastapi_server.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON 포맷 로그 포매터"""
    
    def __init__(self):
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 형태로 포맷팅"""
        
        # 기본 로그 정보
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # 예외 정보 추가
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 추가 컨텍스트 정보
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, 'session_id'):
            log_data["session_id"] = record.session_id
        
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, 'api_endpoint'):
            log_data["api_endpoint"] = record.api_endpoint
        
        if hasattr(record, 'response_time'):
            log_data["response_time"] = record.response_time
        
        if hasattr(record, 'status_code'):
            log_data["status_code"] = record.status_code
        
        # 성능 메트릭
        if hasattr(record, 'metrics'):
            log_data["metrics"] = record.metrics
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class ContextFilter(logging.Filter):
    """로그 컨텍스트 필터"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """로그 레코드에 컨텍스트 정보 추가"""
        
        # 애플리케이션 정보 추가
        record.app_name = settings.APP_NAME
        record.app_version = settings.APP_VERSION
        
        return True


def setup_logging() -> None:
    """로깅 시스템 설정"""
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # JSON 포매터 생성
    json_formatter = JSONFormatter()
    
    # 컨텍스트 필터 생성
    context_filter = ContextFilter()
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.addFilter(context_filter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 파일 핸들러 설정 (로테이션)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.LOG_FILE_PATH,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(json_formatter)
    file_handler.addFilter(context_filter)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 핸들러 추가
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # 개발 환경에서는 더 자세한 로그
    if settings.is_development:
        logging.getLogger("fastapi_server").setLevel(logging.DEBUG)
        logging.getLogger("uvicorn").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 반환"""
    return logging.getLogger(name)


class LoggerMixin:
    """로거 믹스인 클래스"""
    
    @property
    def logger(self) -> logging.Logger:
        """클래스별 로거 반환"""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)


def log_api_request(
    endpoint: str,
    method: str,
    status_code: int,
    response_time: float,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> None:
    """API 요청 로그 기록"""
    
    logger = get_logger("api")
    
    extra = {
        "api_endpoint": f"{method} {endpoint}",
        "status_code": status_code,
        "response_time": response_time,
        "user_id": user_id,
        "session_id": session_id,
        "request_id": request_id,
    }
    
    # 추가 메트릭
    if kwargs:
        extra["metrics"] = kwargs
    
    if status_code >= 400:
        logger.warning("API request failed", extra=extra)
    else:
        logger.info("API request completed", extra=extra)


def log_agent_execution(
    agent_name: str,
    execution_time: float,
    success: bool,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Agent 실행 로그 기록"""
    
    logger = get_logger("agent")
    
    extra = {
        "agent_name": agent_name,
        "execution_time": execution_time,
        "success": success,
        "session_id": session_id,
    }
    
    if kwargs:
        extra["metrics"] = kwargs
    
    if success:
        logger.info(f"Agent {agent_name} executed successfully", extra=extra)
    else:
        logger.error(f"Agent {agent_name} execution failed", extra=extra)


def log_search_operation(
    query: str,
    results_count: int,
    search_time: float,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """검색 작업 로그 기록"""
    
    logger = get_logger("search")
    
    extra = {
        "query_length": len(query),
        "results_count": results_count,
        "search_time": search_time,
        "session_id": session_id,
    }
    
    if kwargs:
        extra["metrics"] = kwargs
    
    logger.info("Search operation completed", extra=extra)


def log_error(
    error: Exception,
    context: Dict[str, Any],
    logger_name: str = "error"
) -> None:
    """에러 로그 기록"""
    
    logger = get_logger(logger_name)
    
    extra = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
    }
    
    logger.error("Application error occurred", exc_info=error, extra=extra)


# 로깅 시스템 초기화
setup_logging()