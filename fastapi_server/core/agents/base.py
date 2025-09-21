"""
Agent 기본 인터페이스

모든 Agent가 구현해야 하는 기본 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    """Agent 간 데이터 전달을 위한 상태 클래스"""
    
    # 사용자 입력
    user_query: str = ""
    session_id: Optional[str] = None
    
    # 질의 분석 결과
    analyzed_query: Dict[str, Any] = None
    query_intent: str = ""
    extracted_keywords: list = None
    category: Optional[str] = None
    confidence_score: float = 0.0
    
    # 검색 결과
    search_results: list = None
    total_documents: int = 0
    search_time: float = 0.0
    
    # 처리된 콘텐츠
    processed_content: str = ""
    citizen_friendly_text: str = ""
    structured_info: Dict[str, Any] = None
    
    # 최종 응답
    final_response: str = ""
    related_questions: list = None
    sources: list = None
    
    # 메타데이터
    processing_steps: list = None
    errors: list = None
    warnings: list = None
    
    def __post_init__(self):
        """초기화 후 기본값 설정"""
        if self.analyzed_query is None:
            self.analyzed_query = {}
        if self.extracted_keywords is None:
            self.extracted_keywords = []
        if self.search_results is None:
            self.search_results = []
        if self.structured_info is None:
            self.structured_info = {}
        if self.related_questions is None:
            self.related_questions = []
        if self.sources is None:
            self.sources = []
        if self.processing_steps is None:
            self.processing_steps = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class BaseAgent(ABC):
    """모든 Agent가 상속해야 하는 기본 클래스"""
    
    def __init__(self, name: str):
        """
        Agent 초기화
        
        Args:
            name: Agent 이름
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Agent 초기화 (Azure OpenAI 연결, 모델 로드 등)
        
        Returns:
            초기화 성공 여부
        """
        pass
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """
        Agent의 핵심 처리 로직
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태
        """
        pass
    
    async def validate_input(self, state: AgentState) -> bool:
        """
        입력 유효성 검사
        
        Args:
            state: 현재 상태
            
        Returns:
            유효성 여부
        """
        return True
    
    def log_step(self, state: AgentState, step_info: str) -> None:
        """
        처리 단계 로깅
        
        Args:
            state: 현재 상태
            step_info: 단계 정보
        """
        self.logger.info(f"[{self.name}] {step_info}")
        state.processing_steps.append({
            "agent": self.name,
            "step": step_info,
            "timestamp": "2024-01-15T10:00:00Z"  # TODO: 실제 timestamp
        })
    
    def log_error(self, state: AgentState, error: str) -> None:
        """
        에러 로깅
        
        Args:
            state: 현재 상태
            error: 에러 메시지
        """
        self.logger.error(f"[{self.name}] Error: {error}")
        state.errors.append({
            "agent": self.name,
            "error": error,
            "timestamp": "2024-01-15T10:00:00Z"  # TODO: 실제 timestamp
        })
    
    def log_warning(self, state: AgentState, warning: str) -> None:
        """
        경고 로깅
        
        Args:
            state: 현재 상태
            warning: 경고 메시지
        """
        self.logger.warning(f"[{self.name}] Warning: {warning}")
        state.warnings.append({
            "agent": self.name,
            "warning": warning,
            "timestamp": "2024-01-15T10:00:00Z"  # TODO: 실제 timestamp
        })
    
    def get_status(self) -> Dict[str, Any]:
        """
        Agent 상태 정보 반환
        
        Returns:
            상태 정보 딕셔너리
        """
        return {
            "name": self.name,
            "initialized": self.is_initialized,
            "status": "ready" if self.is_initialized else "not_initialized"
        }

class AgentError(Exception):
    """Agent 처리 중 발생하는 예외"""
    
    def __init__(self, agent_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Agent 에러 초기화
        
        Args:
            agent_name: Agent 이름
            message: 에러 메시지
            details: 추가 상세 정보
        """
        self.agent_name = agent_name
        self.details = details or {}
        super().__init__(f"[{agent_name}] {message}")

class AgentTimeoutError(AgentError):
    """Agent 처리 시간 초과 예외"""
    pass

class AgentInitializationError(AgentError):
    """Agent 초기화 실패 예외"""
    pass
