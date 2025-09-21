"""
LangGraph 상태 관리 시스템
"""
from typing import TypedDict, Dict, List, Any, Optional, Literal, Union
from typing_extensions import NotRequired
from datetime import datetime
import json

from fastapi_server.models.schemas import DocumentResult, ChatMessage, DifficultyLevel


# === 상태 타입 정의 ===

class AgentStateDict(TypedDict):
    """LangGraph용 Agent 상태 TypedDict"""
    
    # 필수 필드
    session_id: str
    user_query: str
    current_step: Literal[
        "query_analysis", "document_retrieval", 
        "content_processing", "response_generation", 
        "completed", "error"
    ]
    
    # 선택적 필드 (NotRequired 사용)
    processed_query: NotRequired[Optional[str]]
    query_intent: NotRequired[Optional[str]]
    query_category: NotRequired[Optional[str]]
    query_keywords: NotRequired[List[str]]
    query_entities: NotRequired[Dict[str, List[str]]]
    query_confidence: NotRequired[float]
    
    # 문서 검색 결과
    search_results: NotRequired[List[Dict[str, Any]]]
    total_results_count: NotRequired[int]
    search_strategy: NotRequired[Optional[str]]
    
    # 처리된 내용
    simplified_content: NotRequired[Optional[str]]
    key_points: NotRequired[List[str]]
    step_by_step_guide: NotRequired[List[str]]
    terminology_explanations: NotRequired[Dict[str, str]]
    target_difficulty: NotRequired[Optional[str]]
    readability_score: NotRequired[float]
    
    # 최종 응답
    final_response: NotRequired[Optional[str]]
    follow_up_questions: NotRequired[List[str]]
    related_links: NotRequired[List[Dict[str, str]]]
    confidence_score: NotRequired[float]
    
    # 메타데이터
    chat_history: NotRequired[List[Dict[str, Any]]]
    context: NotRequired[Dict[str, Any]]
    metadata: NotRequired[Dict[str, Any]]
    error_message: NotRequired[Optional[str]]
    processing_times: NotRequired[Dict[str, float]]
    
    # 상태 관리
    created_at: NotRequired[str]
    updated_at: NotRequired[str]
    retry_count: NotRequired[int]


class WorkflowDecision(TypedDict):
    """워크플로우 라우팅 결정"""
    next_step: str
    reason: str
    confidence: float
    metadata: NotRequired[Dict[str, Any]]


# === 상태 관리 클래스 ===

class StateManager:
    """상태 관리 유틸리티"""
    
    @staticmethod
    def create_initial_state(session_id: str, user_query: str) -> AgentStateDict:
        """초기 상태 생성"""
        now = datetime.utcnow().isoformat()
        
        return AgentStateDict(
            session_id=session_id,
            user_query=user_query,
            current_step="query_analysis",
            query_keywords=[],
            query_entities={},
            query_confidence=0.0,
            search_results=[],
            total_results_count=0,
            key_points=[],
            step_by_step_guide=[],
            terminology_explanations={},
            readability_score=0.0,
            follow_up_questions=[],
            related_links=[],
            confidence_score=0.0,
            chat_history=[],
            context={},
            metadata={},
            processing_times={},
            created_at=now,
            updated_at=now,
            retry_count=0
        )
    
    @staticmethod
    def update_state(
        state: AgentStateDict, 
        updates: Dict[str, Any]
    ) -> AgentStateDict:
        """상태 업데이트"""
        new_state = state.copy()
        new_state.update(updates)
        new_state["updated_at"] = datetime.utcnow().isoformat()
        return new_state
    
    @staticmethod
    def set_step(state: AgentStateDict, step: str) -> AgentStateDict:
        """처리 단계 변경"""
        return StateManager.update_state(state, {
            "current_step": step,
            "updated_at": datetime.utcnow().isoformat()
        })
    
    @staticmethod
    def set_error(state: AgentStateDict, error_message: str) -> AgentStateDict:
        """에러 상태 설정"""
        return StateManager.update_state(state, {
            "current_step": "error",
            "error_message": error_message,
            "retry_count": state.get("retry_count", 0) + 1
        })
    
    @staticmethod
    def add_processing_time(
        state: AgentStateDict, 
        step_name: str, 
        duration: float
    ) -> AgentStateDict:
        """처리 시간 추가"""
        processing_times = state.get("processing_times", {}).copy()
        processing_times[step_name] = duration
        
        return StateManager.update_state(state, {
            "processing_times": processing_times
        })
    
    @staticmethod
    def add_context(
        state: AgentStateDict, 
        key: str, 
        value: Any
    ) -> AgentStateDict:
        """컨텍스트 정보 추가"""
        context = state.get("context", {}).copy()
        context[key] = value
        
        return StateManager.update_state(state, {
            "context": context
        })
    
    @staticmethod
    def validate_state(state: AgentStateDict) -> bool:
        """상태 유효성 검증"""
        required_fields = ["session_id", "user_query", "current_step"]
        
        for field in required_fields:
            if field not in state or not state[field]:
                return False
        
        valid_steps = [
            "query_analysis", "document_retrieval", 
            "content_processing", "response_generation", 
            "completed", "error"
        ]
        
        return state["current_step"] in valid_steps
    
    @staticmethod
    def is_completed(state: AgentStateDict) -> bool:
        """완료 상태 확인"""
        return state.get("current_step") == "completed"
    
    @staticmethod
    def is_error(state: AgentStateDict) -> bool:
        """에러 상태 확인"""
        return state.get("current_step") == "error"
    
    @staticmethod
    def can_retry(state: AgentStateDict, max_retries: int = 3) -> bool:
        """재시도 가능 여부"""
        return state.get("retry_count", 0) < max_retries
    
    @staticmethod
    def get_total_processing_time(state: AgentStateDict) -> float:
        """총 처리 시간 계산"""
        return sum(state.get("processing_times", {}).values())
    
    @staticmethod
    def serialize_state(state: AgentStateDict) -> str:
        """상태 직렬화"""
        return json.dumps(state, ensure_ascii=False, default=str)
    
    @staticmethod
    def deserialize_state(state_json: str) -> AgentStateDict:
        """상태 역직렬화"""
        return json.loads(state_json)


# === 워크플로우 노드 정의 ===

class WorkflowNodes:
    """워크플로우 노드 정의"""
    
    # 노드 이름 상수
    QUERY_ANALYSIS = "query_analysis"
    DOCUMENT_RETRIEVAL = "document_retrieval"
    CONTENT_PROCESSING = "content_processing"
    RESPONSE_GENERATION = "response_generation"
    COMPLETED = "completed"
    ERROR = "error"
    
    # 조건부 라우팅 노드
    ROUTE_AFTER_ANALYSIS = "route_after_analysis"
    ROUTE_AFTER_RETRIEVAL = "route_after_retrieval"
    ROUTE_AFTER_PROCESSING = "route_after_processing"
    
    @staticmethod
    def get_all_nodes() -> List[str]:
        """모든 노드 목록 반환"""
        return [
            WorkflowNodes.QUERY_ANALYSIS,
            WorkflowNodes.DOCUMENT_RETRIEVAL,
            WorkflowNodes.CONTENT_PROCESSING,
            WorkflowNodes.RESPONSE_GENERATION,
            WorkflowNodes.COMPLETED,
            WorkflowNodes.ERROR,
            WorkflowNodes.ROUTE_AFTER_ANALYSIS,
            WorkflowNodes.ROUTE_AFTER_RETRIEVAL,
            WorkflowNodes.ROUTE_AFTER_PROCESSING,
        ]
    
    @staticmethod
    def get_processing_nodes() -> List[str]:
        """처리 노드만 반환"""
        return [
            WorkflowNodes.QUERY_ANALYSIS,
            WorkflowNodes.DOCUMENT_RETRIEVAL,
            WorkflowNodes.CONTENT_PROCESSING,
            WorkflowNodes.RESPONSE_GENERATION,
        ]
    
    @staticmethod
    def get_routing_nodes() -> List[str]:
        """라우팅 노드만 반환"""
        return [
            WorkflowNodes.ROUTE_AFTER_ANALYSIS,
            WorkflowNodes.ROUTE_AFTER_RETRIEVAL,
            WorkflowNodes.ROUTE_AFTER_PROCESSING,
        ]


# === 조건부 라우팅 로직 ===

class WorkflowRouter:
    """워크플로우 라우팅 로직"""
    
    @staticmethod
    def route_after_analysis(state: AgentStateDict) -> WorkflowDecision:
        """질의 분석 후 라우팅"""
        
        # 에러 상태 확인
        if state.get("current_step") == "error":
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="Analysis failed",
                confidence=1.0
            )
        
        # 질의 신뢰도 확인
        confidence = state.get("query_confidence", 0.0)
        
        if confidence < 0.3:
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="Query confidence too low",
                confidence=1.0,
                metadata={"min_confidence": 0.3, "actual_confidence": confidence}
            )
        
        # 정상적인 경우 문서 검색으로
        return WorkflowDecision(
            next_step=WorkflowNodes.DOCUMENT_RETRIEVAL,
            reason="Analysis successful, proceeding to document retrieval",
            confidence=confidence
        )
    
    @staticmethod
    def route_after_retrieval(state: AgentStateDict) -> WorkflowDecision:
        """문서 검색 후 라우팅"""
        
        # 에러 상태 확인
        if state.get("current_step") == "error":
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="Document retrieval failed",
                confidence=1.0
            )
        
        # 검색 결과 확인
        results_count = state.get("total_results_count", 0)
        
        if results_count == 0:
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="No documents found",
                confidence=1.0,
                metadata={"results_count": results_count}
            )
        
        # 결과가 너무 적은 경우 (< 2개)
        if results_count < 2:
            return WorkflowDecision(
                next_step=WorkflowNodes.CONTENT_PROCESSING,
                reason="Limited results found, proceeding with caution",
                confidence=0.6,
                metadata={"results_count": results_count, "warning": "limited_results"}
            )
        
        # 정상적인 경우
        return WorkflowDecision(
            next_step=WorkflowNodes.CONTENT_PROCESSING,
            reason="Sufficient documents found",
            confidence=0.9,
            metadata={"results_count": results_count}
        )
    
    @staticmethod
    def route_after_processing(state: AgentStateDict) -> WorkflowDecision:
        """내용 처리 후 라우팅"""
        
        # 에러 상태 확인
        if state.get("current_step") == "error":
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="Content processing failed",
                confidence=1.0
            )
        
        # 처리된 내용 확인
        simplified_content = state.get("simplified_content")
        
        if not simplified_content or len(simplified_content.strip()) < 10:
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="Processed content is insufficient",
                confidence=1.0,
                metadata={"content_length": len(simplified_content) if simplified_content else 0}
            )
        
        # 가독성 점수 확인
        readability = state.get("readability_score", 0.0)
        
        if readability < 0.3:
            return WorkflowDecision(
                next_step=WorkflowNodes.RESPONSE_GENERATION,
                reason="Low readability but proceeding",
                confidence=0.6,
                metadata={"readability_score": readability, "warning": "low_readability"}
            )
        
        # 정상적인 경우
        return WorkflowDecision(
            next_step=WorkflowNodes.RESPONSE_GENERATION,
            reason="Content processing successful",
            confidence=0.9,
            metadata={"readability_score": readability}
        )
    
    @staticmethod
    def route_after_response(state: AgentStateDict) -> WorkflowDecision:
        """응답 생성 후 라우팅"""
        
        # 에러 상태 확인
        if state.get("current_step") == "error":
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="Response generation failed",
                confidence=1.0
            )
        
        # 최종 응답 확인
        final_response = state.get("final_response")
        
        if not final_response or len(final_response.strip()) < 10:
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="Generated response is insufficient",
                confidence=1.0,
                metadata={"response_length": len(final_response) if final_response else 0}
            )
        
        # 신뢰도 점수 확인
        confidence_score = state.get("confidence_score", 0.0)
        
        if confidence_score < 0.5:
            return WorkflowDecision(
                next_step=WorkflowNodes.COMPLETED,
                reason="Response generated with low confidence",
                confidence=confidence_score,
                metadata={"confidence_score": confidence_score, "warning": "low_confidence"}
            )
        
        # 정상적인 완료
        return WorkflowDecision(
            next_step=WorkflowNodes.COMPLETED,
            reason="Workflow completed successfully",
            confidence=confidence_score,
            metadata={"confidence_score": confidence_score}
        )
    
    @staticmethod
    def route_from_error(state: AgentStateDict) -> WorkflowDecision:
        """에러 상태에서의 라우팅 (재시도 로직)"""
        
        if not StateManager.can_retry(state):
            return WorkflowDecision(
                next_step=WorkflowNodes.ERROR,
                reason="Maximum retries exceeded",
                confidence=1.0,
                metadata={"retry_count": state.get("retry_count", 0)}
            )
        
        # 에러 원인에 따른 재시도 위치 결정
        error_message = state.get("error_message", "")
        
        if "analysis" in error_message.lower():
            return WorkflowDecision(
                next_step=WorkflowNodes.QUERY_ANALYSIS,
                reason="Retrying from query analysis",
                confidence=0.5,
                metadata={"retry_from": "analysis"}
            )
        elif "retrieval" in error_message.lower():
            return WorkflowDecision(
                next_step=WorkflowNodes.DOCUMENT_RETRIEVAL,
                reason="Retrying from document retrieval",
                confidence=0.5,
                metadata={"retry_from": "retrieval"}
            )
        elif "processing" in error_message.lower():
            return WorkflowDecision(
                next_step=WorkflowNodes.CONTENT_PROCESSING,
                reason="Retrying from content processing",
                confidence=0.5,
                metadata={"retry_from": "processing"}
            )
        else:
            return WorkflowDecision(
                next_step=WorkflowNodes.QUERY_ANALYSIS,
                reason="Retrying from the beginning",
                confidence=0.3,
                metadata={"retry_from": "beginning"}
            )


# === 상태 전환 규칙 ===

class StateTransitionRules:
    """상태 전환 규칙 정의"""
    
    # 허용된 상태 전환 매핑
    VALID_TRANSITIONS = {
        "query_analysis": ["document_retrieval", "error"],
        "document_retrieval": ["content_processing", "error"],
        "content_processing": ["response_generation", "error"],
        "response_generation": ["completed", "error"],
        "error": ["query_analysis", "document_retrieval", "content_processing", "response_generation"],
        "completed": ["query_analysis"],  # 새로운 질의 시작
    }
    
    @staticmethod
    def is_valid_transition(from_step: str, to_step: str) -> bool:
        """유효한 상태 전환인지 확인"""
        return to_step in StateTransitionRules.VALID_TRANSITIONS.get(from_step, [])
    
    @staticmethod
    def get_possible_next_steps(current_step: str) -> List[str]:
        """현재 단계에서 가능한 다음 단계들"""
        return StateTransitionRules.VALID_TRANSITIONS.get(current_step, [])
    
    @staticmethod
    def validate_state_transition(
        state: AgentStateDict, 
        new_step: str
    ) -> tuple[bool, str]:
        """상태 전환 유효성 검증"""
        current_step = state.get("current_step")
        
        if not current_step:
            return False, "Current step is not defined"
        
        if not StateTransitionRules.is_valid_transition(current_step, new_step):
            return False, f"Invalid transition from {current_step} to {new_step}"
        
        # 특별한 조건 검증
        if new_step == "completed" and not state.get("final_response"):
            return False, "Cannot complete without final response"
        
        if new_step == "error" and state.get("retry_count", 0) >= 3:
            return False, "Maximum retry limit reached"
        
        return True, "Valid transition"


# === 워크플로우 설정 ===

class WorkflowConfig:
    """워크플로우 설정"""
    
    # 기본 설정값
    DEFAULT_CONFIG = {
        "max_retries": 3,
        "timeout_seconds": 300,  # 5분
        "min_confidence_threshold": 0.3,
        "min_results_count": 1,
        "min_readability_score": 0.3,
        "min_response_length": 10,
        "enable_parallel_processing": False,
        "enable_caching": True,
        "log_level": "INFO"
    }
    
    @staticmethod
    def get_config(custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """설정 반환"""
        config = WorkflowConfig.DEFAULT_CONFIG.copy()
        if custom_config:
            config.update(custom_config)
        return config
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """설정 유효성 검증"""
        required_keys = ["max_retries", "timeout_seconds", "min_confidence_threshold"]
        
        for key in required_keys:
            if key not in config:
                return False
        
        # 범위 검증
        if not (0 <= config.get("min_confidence_threshold", 0) <= 1):
            return False
        
        if config.get("max_retries", 0) < 0:
            return False
        
        return True