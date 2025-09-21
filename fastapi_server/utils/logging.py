"""
로깅 유틸리티

구조화된 로깅 시스템을 제공합니다.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """JSON 형태로 로그를 포맷팅하는 클래스"""
    
    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON으로 포맷팅"""
        
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 예외 정보 추가
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # 추가 컨텍스트 정보
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data
        
        # 요청 ID (있는 경우)
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        # 세션 ID (있는 경우)
        if hasattr(record, "session_id"):
            log_entry["session_id"] = record.session_id
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None
) -> None:
    """
    로깅 시스템 설정
    
    Args:
        log_level: 로그 레벨
        log_format: 로그 포맷 (json/text)
        log_file: 로그 파일 경로
    """
    
    # 로그 레벨 설정
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 포맷터 선택
    if log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 파일 핸들러 (설정된 경우)
    if log_file:
        # 로그 디렉토리 생성
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logging.info(f"로깅 시스템 초기화 완료 - Level: {log_level}, Format: {log_format}")

def get_logger(name: str) -> logging.Logger:
    """
    이름으로 로거 인스턴스 반환
    
    Args:
        name: 로거 이름
        
    Returns:
        로거 인스턴스
    """
    return logging.getLogger(name)

def log_request(
    method: str,
    path: str,
    status_code: int,
    response_time: float,
    request_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> None:
    """
    HTTP 요청 로깅
    
    Args:
        method: HTTP 메서드
        path: 요청 경로
        status_code: 응답 상태 코드
        response_time: 응답 시간
        request_id: 요청 ID
        user_agent: 사용자 에이전트
        ip_address: IP 주소
    """
    
    logger = get_logger("api.request")
    
    extra_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "response_time": response_time,
        "user_agent": user_agent,
        "ip_address": ip_address
    }
    
    # None 값 제거
    extra_data = {k: v for k, v in extra_data.items() if v is not None}
    
    # 로그 레코드에 추가 데이터 설정
    log_record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg=f"{method} {path} - {status_code} ({response_time:.3f}s)",
        args=(),
        exc_info=None
    )
    
    log_record.extra_data = extra_data
    if request_id:
        log_record.request_id = request_id
    
    logger.handle(log_record)

def log_agent_activity(
    agent_name: str,
    action: str,
    session_id: Optional[str] = None,
    processing_time: Optional[float] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Agent 활동 로깅
    
    Args:
        agent_name: Agent 이름
        action: 수행한 액션
        session_id: 세션 ID
        processing_time: 처리 시간
        success: 성공 여부
        error_message: 에러 메시지
        extra_data: 추가 데이터
    """
    
    logger = get_logger(f"agent.{agent_name}")
    
    log_data = {
        "agent": agent_name,
        "action": action,
        "success": success,
        "processing_time": processing_time
    }
    
    if extra_data:
        log_data.update(extra_data)
    
    message = f"[{agent_name}] {action}"
    if processing_time:
        message += f" ({processing_time:.3f}s)"
    
    if success:
        level = logging.INFO
        message += " - SUCCESS"
    else:
        level = logging.ERROR
        message += f" - FAILED: {error_message}"
        log_data["error"] = error_message
    
    # 로그 레코드 생성
    log_record = logging.LogRecord(
        name=logger.name,
        level=level,
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    
    log_record.extra_data = log_data
    if session_id:
        log_record.session_id = session_id
    
    logger.handle(log_record)

def log_search_activity(
    query: str,
    results_count: int,
    processing_time: float,
    session_id: Optional[str] = None,
    category: Optional[str] = None,
    success: bool = True
) -> None:
    """
    검색 활동 로깅
    
    Args:
        query: 검색 쿼리
        results_count: 결과 수
        processing_time: 처리 시간
        session_id: 세션 ID
        category: 카테고리
        success: 성공 여부
    """
    
    logger = get_logger("search.activity")
    
    extra_data = {
        "query": query,
        "results_count": results_count,
        "processing_time": processing_time,
        "category": category,
        "success": success
    }
    
    message = f"검색: '{query}' - {results_count}개 결과 ({processing_time:.3f}s)"
    
    log_record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    
    log_record.extra_data = extra_data
    if session_id:
        log_record.session_id = session_id
    
    logger.handle(log_record)

def log_chat_activity(
    message: str,
    response_length: int,
    processing_time: float,
    session_id: str,
    confidence_score: Optional[float] = None,
    intent: Optional[str] = None
) -> None:
    """
    채팅 활동 로깅
    
    Args:
        message: 사용자 메시지
        response_length: 응답 길이
        processing_time: 처리 시간
        session_id: 세션 ID
        confidence_score: 신뢰도 점수
        intent: 감지된 의도
    """
    
    logger = get_logger("chat.activity")
    
    extra_data = {
        "message_length": len(message),
        "response_length": response_length,
        "processing_time": processing_time,
        "confidence_score": confidence_score,
        "intent": intent
    }
    
    message_preview = message[:50] + "..." if len(message) > 50 else message
    log_message = f"채팅: '{message_preview}' -> {response_length}자 응답 ({processing_time:.3f}s)"
    
    log_record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg=log_message,
        args=(),
        exc_info=None
    )
    
    log_record.extra_data = extra_data
    log_record.session_id = session_id
    
    logger.handle(log_record)

# 기본 로깅 설정 (개발용)
if __name__ != "__main__":
    setup_logging()
