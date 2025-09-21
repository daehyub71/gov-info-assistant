"""
LangGraph 상태 시스템 테스트
"""
import pytest
from datetime import datetime
from typing import Dict, Any
import json
import threading
import time

from fastapi_server.core.workflow.state import (
    AgentStateDict, StateManager, WorkflowNodes, WorkflowRouter,
    StateTransitionRules, WorkflowConfig, WorkflowDecision
)


@pytest.mark.unit
class TestAgentStateDict:
    """AgentStateDict TypedDict 테스트"""
    
    def test_minimal_state_creation(self):
        """최소 필수 필드로 상태 생성 테스트"""
        state: AgentStateDict = {
            "session_id": "test-session-123",
            "user_query": "주민등록등본 발급 방법",
            "current_step": "query_analysis"
        }
        
        assert state["session_id"] == "test-session-123"
        assert state["user_query"] == "주민등록등본 발급 방법"
        assert state["current_step"] == "query_analysis"
    
    def test_full_state_creation(self):
        """전체 필드로 상태 생성 테스트"""
        state: AgentStateDict = {
            "session_id": "test-session-123",
            "user_query": "주민등록등본 발급 방법",
            "current_step": "document_retrieval",
            "processed_query": "주민등록등본 발급",
            "query_intent": "정보조회",
            "query_category": "행정서비스",
            "query_keywords": ["주민등록", "발급"],
            "query_entities": {"서류": ["주민등록등본"]},
            "query_confidence": 0.9,
            "search_results": [
                {
                    "id": "doc_001",
                    "title": "주민등록등본 발급 안내",
                    "score": 0.95
                }
            ],
            "total_results_count": 1,
            "search_strategy": "hybrid_search",
            "simplified_content": "간단한 설명",
            "key_points": ["핵심 1", "핵심 2"],
            "step_by_step_guide": ["1단계", "2단계"],
            "terminology_explanations": {"용어": "설명"},
            "readability_score": 0.8,
            "final_response": "최종 응답",
            "follow_up_questions": ["추가 질문"],
            "related_links": [{"title": "관련", "url": "/link"}],
            "confidence_score": 0.85,
            "chat_history": [],
            "context": {"key": "value"},
            "metadata": {"info": "data"},
            "processing_times": {"analysis": 1.5},
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:01:00",
            "retry_count": 0
        }
        
        assert len(state["query_keywords"]) == 2
        assert state["confidence_score"] == 0.85
        assert "주민등록" in state["query_keywords"]


@pytest.mark.unit
class TestStateManager:
    """StateManager 테스트"""
    
    def test_create_initial_state(self):
        """초기 상태 생성 테스트"""
        session_id = "test-session-123"
        user_query = "주민등록등본 발급 방법"
        
        state = StateManager.create_initial_state(session_id, user_query)
        
        assert state["session_id"] == session_id
        assert state["user_query"] == user_query
        assert state["current_step"] == "query_analysis"
        assert state["retry_count"] == 0
        assert "created_at" in state
        assert "updated_at" in state
        assert isinstance(state["query_keywords"], list)
        assert isinstance(state["context"], dict)
    
    def test_update_state(self):
        """상태 업데이트 테스트"""
        initial_state = StateManager.create_initial_state("session", "query")
        
        updates = {
            "processed_query": "처리된 질의",
            "query_confidence": 0.9,
            "current_step": "document_retrieval"
        }
        
        updated_state = StateManager.update_state(initial_state, updates)
        
        assert updated_state["processed_query"] == "처리된 질의"
        assert updated_state["query_confidence"] == 0.9
        assert updated_state["current_step"] == "document_retrieval"
        assert updated_state["updated_at"] != initial_state["updated_at"]
    
    def test_set_error(self):
        """에러 상태 설정 테스트"""
        state = StateManager.create_initial_state("session", "query")
        error_message = "테스트 에러"
        
        error_state = StateManager.set_error(state, error_message)
        
        assert error_state["current_step"] == "error"
        assert error_state["error_message"] == error_message
        assert error_state["retry_count"] == 1
    
    def test_validate_state(self):
        """상태 유효성 검증 테스트"""
        valid_state = StateManager.create_initial_state("session", "query")
        assert StateManager.validate_state(valid_state) is True
        
        invalid_state = {
            "session_id": "session",
            "current_step": "query_analysis"
        }
        assert StateManager.validate_state(invalid_state) is False


@pytest.mark.unit
class TestWorkflowRouter:
    """WorkflowRouter 테스트"""
    
    def test_route_after_analysis_success(self):
        """질의 분석 후 성공 라우팅 테스트"""
        state = StateManager.create_initial_state("session", "query")
        state = StateManager.update_state(state, {
            "query_confidence": 0.8,
            "current_step": "query_analysis"
        })
        
        decision = WorkflowRouter.route_after_analysis(state)
        
        assert decision["next_step"] == WorkflowNodes.DOCUMENT_RETRIEVAL
        assert decision["confidence"] == 0.8
        assert "successful" in decision["reason"]
    
    def test_route_after_analysis_low_confidence(self):
        """질의 분석 후 신뢰도 낮음 라우팅 테스트"""
        state = StateManager.create_initial_state("session", "query")
        state = StateManager.update_state(state, {
            "query_confidence": 0.2,
            "current_step": "query_analysis"
        })
        
        decision = WorkflowRouter.route_after_analysis(state)
        
        assert decision["next_step"] == WorkflowNodes.ERROR
        assert "confidence too low" in decision["reason"]
    
    def test_route_after_retrieval_success(self):
        """문서 검색 후 성공 라우팅 테스트"""
        state = StateManager.create_initial_state("session", "query")
        state = StateManager.update_state(state, {
            "total_results_count": 5,
            "current_step": "document_retrieval"
        })
        
        decision = WorkflowRouter.route_after_retrieval(state)
        
        assert decision["next_step"] == WorkflowNodes.CONTENT_PROCESSING
        assert "Sufficient documents" in decision["reason"]
        assert decision["confidence"] == 0.9
    
    def test_route_after_retrieval_no_results(self):
        """문서 검색 후 결과 없음 라우팅 테스트"""
        state = StateManager.create_initial_state("session", "query")
        state = StateManager.update_state(state, {
            "total_results_count": 0,
            "current_step": "document_retrieval"
        })
        
        decision = WorkflowRouter.route_after_retrieval(state)
        
        assert decision["next_step"] == WorkflowNodes.ERROR
        assert "No documents found" in decision["reason"]
    
    def test_route_after_processing_success(self):
        """내용 처리 후 성공 라우팅 테스트"""
        state = StateManager.create_initial_state("session", "query")
        state = StateManager.update_state(state, {
            "simplified_content": "충분한 길이의 처리된 내용입니다.",
            "readability_score": 0.8,
            "current_step": "content_processing"
        })
        
        decision = WorkflowRouter.route_after_processing(state)
        
        assert decision["next_step"] == WorkflowNodes.RESPONSE_GENERATION
        assert "successful" in decision["reason"]
        assert decision["confidence"] == 0.9
    
    def test_route_after_response_success(self):
        """응답 생성 후 성공 라우팅 테스트"""
        state = StateManager.create_initial_state("session", "query")
        state = StateManager.update_state(state, {
            "final_response": "충분한 길이의 최종 응답입니다.",
            "confidence_score": 0.8,
            "current_step": "response_generation"
        })
        
        decision = WorkflowRouter.route_after_response(state)
        
        assert decision["next_step"] == WorkflowNodes.COMPLETED
        assert "successfully" in decision["reason"]
        assert decision["confidence"] == 0.8
    
    def test_route_after_response_low_confidence(self):
        """응답 생성 후 낮은 신뢰도 라우팅 테스트"""
        state = StateManager.create_initial_state("session", "query")
        state = StateManager.update_state(state, {
            "final_response": "충분한 길이의 최종 응답입니다.",
            "confidence_score": 0.3,
            "current_step": "response_generation"
        })
        
        decision = WorkflowRouter.route_after_response(state)
        
        assert decision["next_step"] == WorkflowNodes.COMPLETED
        assert "low confidence" in decision["reason"]
        assert decision["confidence"] == 0.3


@pytest.mark.unit
class TestStateTransitionRules:
    """StateTransitionRules 테스트"""
    
    def test_valid_transitions(self):
        """유효한 상태 전환 테스트"""
        assert StateTransitionRules.is_valid_transition("query_analysis", "document_retrieval") is True
        assert StateTransitionRules.is_valid_transition("document_retrieval", "content_processing") is True
        assert StateTransitionRules.is_valid_transition("content_processing", "response_generation") is True
        assert StateTransitionRules.is_valid_transition("response_generation", "completed") is True
        
        # 에러로 전환
        assert StateTransitionRules.is_valid_transition("query_analysis", "error") is True
        
        # 에러에서 복구
        assert StateTransitionRules.is_valid_transition("error", "query_analysis") is True
    
    def test_invalid_transitions(self):
        """유효하지 않은 상태 전환 테스트"""
        assert StateTransitionRules.is_valid_transition("query_analysis", "content_processing") is False
        assert StateTransitionRules.is_valid_transition("document_retrieval", "response_generation") is False
        assert StateTransitionRules.is_valid_transition("response_generation", "query_analysis") is False


@pytest.mark.unit
class TestWorkflowConfig:
    """WorkflowConfig 테스트"""
    
    def test_default_config(self):
        """기본 설정 테스트"""
        config = WorkflowConfig.get_config()
        
        assert config["max_retries"] == 3
        assert config["timeout_seconds"] == 300
        assert config["min_confidence_threshold"] == 0.3
        assert config["enable_caching"] is True
    
    def test_custom_config_override(self):
        """커스텀 설정 오버라이드 테스트"""
        custom_config = {
            "max_retries": 5,
            "timeout_seconds": 600,
            "custom_setting": "custom_value"
        }
        
        config = WorkflowConfig.get_config(custom_config)
        
        assert config["max_retries"] == 5
        assert config["timeout_seconds"] == 600
        assert config["min_confidence_threshold"] == 0.3
        assert config["custom_setting"] == "custom_value"


@pytest.mark.integration
class TestWorkflowIntegration:
    """워크플로우 통합 테스트"""
    
    def test_complete_workflow_state_progression(self):
        """완전한 워크플로우 상태 진행 테스트"""
        state = StateManager.create_initial_state("session-123", "주민등록등본 발급 방법")
        
        # 1. 질의 분석 단계
        state = StateManager.update_state(state, {
            "processed_query": "주민등록등본 발급",
            "query_intent": "정보조회",
            "query_confidence": 0.9,
            "current_step": "query_analysis"
        })
        
        decision = WorkflowRouter.route_after_analysis(state)
        assert decision["next_step"] == "document_retrieval"
        
        # 2. 문서 검색 단계
        state = StateManager.update_state(state, {
            "search_results": [{"id": "doc1", "title": "test", "score": 0.9}],
            "total_results_count": 3,
            "current_step": "document_retrieval"
        })
        
        decision = WorkflowRouter.route_after_retrieval(state)
        assert decision["next_step"] == "content_processing"
        
        # 3. 내용 처리 단계
        state = StateManager.update_state(state, {
            "simplified_content": "간단하게 처리된 내용입니다.",
            "readability_score": 0.8,
            "current_step": "content_processing"
        })
        
        decision = WorkflowRouter.route_after_processing(state)
        assert decision["next_step"] == "response_generation"
        
        # 4. 응답 생성 단계
        state = StateManager.update_state(state, {
            "final_response": "주민등록등본은 온라인에서 발급받을 수 있습니다.",
            "confidence_score": 0.85,
            "current_step": "response_generation"
        })
        
        decision = WorkflowRouter.route_after_response(state)
        assert decision["next_step"] == "completed"
        
        final_state = StateManager.set_step(state, "completed")
        assert StateManager.is_completed(final_state)
        assert StateManager.validate_state(final_state)
    
    def test_error_recovery_workflow(self):
        """에러 복구 워크플로우 테스트"""
        state = StateManager.create_initial_state("session-456", "테스트 질의")
        
        error_state = StateManager.set_error(state, "analysis failed")
        assert StateManager.is_error(error_state)
        assert error_state["retry_count"] == 1
        
        recovery_decision = WorkflowRouter.route_from_error(error_state)
        assert recovery_decision["next_step"] == "query_analysis"
        assert StateManager.can_retry(error_state)
    
    def test_state_serialization_workflow(self):
        """상태 직렬화 워크플로우 테스트"""
        state = StateManager.create_initial_state("session-789", "복잡한 질의")
        state = StateManager.update_state(state, {
            "query_keywords": ["키워드1", "키워드2"],
            "search_results": [
                {"id": "doc1", "title": "문서1", "score": 0.9},
                {"id": "doc2", "title": "문서2", "score": 0.8}
            ],
            "context": {"user_type": "citizen", "language": "ko"}
        })
        
        serialized = StateManager.serialize_state(state)
        assert isinstance(serialized, str)
        assert "session-789" in serialized
        
        deserialized = StateManager.deserialize_state(serialized)
        
        assert deserialized["session_id"] == state["session_id"]
        assert deserialized["user_query"] == state["user_query"]
        assert len(deserialized["search_results"]) == 2
        assert deserialized["context"]["user_type"] == "citizen"
        assert StateManager.validate_state(deserialized)


@pytest.mark.performance
class TestStatePerformance:
    """상태 관리 성능 테스트"""
    
    def test_state_creation_performance(self):
        """상태 생성 성능 테스트"""
        start_time = time.time()
        
        states = []
        for i in range(1000):
            state = StateManager.create_initial_state(f"session-{i}", f"query-{i}")
            states.append(state)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 1.0
        assert len(states) == 1000
    
    def test_state_update_performance(self):
        """상태 업데이트 성능 테스트"""
        state = StateManager.create_initial_state("session", "query")
        
        start_time = time.time()
        
        for i in range(1000):
            state = StateManager.update_state(state, {f"field_{i}": f"value_{i}"})
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 1.0


@pytest.mark.edge_cases
class TestStateEdgeCases:
    """상태 관리 엣지 케이스 테스트"""
    
    def test_empty_string_fields(self):
        """빈 문자열 필드 처리 테스트"""
        state = StateManager.create_initial_state("", "")
        assert StateManager.validate_state(state) is False
    
    def test_unicode_handling(self):
        """유니코드 문자 처리 테스트"""
        state = StateManager.create_initial_state("세션-한글", "안녕하세요! 👋 특수문자 테스트")
        
        updated_state = StateManager.update_state(state, {
            "processed_query": "처리된 한글 질의 🔍",
            "query_keywords": ["한글", "키워드", "🏛️"],
            "context": {
                "언어": "한국어",
                "이모지": "🚀📚💡"
            }
        })
        
        serialized = StateManager.serialize_state(updated_state)
        deserialized = StateManager.deserialize_state(serialized)
        
        assert deserialized["user_query"] == "안녕하세요! 👋 특수문자 테스트"
        assert "🔍" in deserialized["processed_query"]
        assert "🏛️" in deserialized["query_keywords"]
    
    def test_large_data_handling(self):
        """대용량 데이터 처리 테스트"""
        state = StateManager.create_initial_state("session", "query")
        
        large_search_results = [
            {
                "id": f"doc_{i}",
                "title": f"Document {i}",
                "content": "A" * 1000,
                "metadata": {f"key_{j}": f"value_{j}" for j in range(10)}
            }
            for i in range(10)
        ]
        
        updated_state = StateManager.update_state(state, {
            "search_results": large_search_results
        })
        
        serialized = StateManager.serialize_state(updated_state)
        deserialized = StateManager.deserialize_state(serialized)
        
        assert len(deserialized["search_results"]) == 10
        assert len(deserialized["search_results"][0]["content"]) == 1000


@pytest.mark.stress
class TestStateStress:
    """상태 관리 스트레스 테스트"""
    
    def test_multiple_rapid_updates(self):
        """빠른 연속 업데이트 테스트"""
        state = StateManager.create_initial_state("session", "query")
        
        for i in range(100):
            state = StateManager.update_state(state, {
                f"field_{i % 10}": f"value_{i}",
                "counter": i
            })
        
        assert state["counter"] == 99
        assert len(str(state)) < 50000
    
    def test_concurrent_state_operations(self):
        """동시 상태 작업 시뮬레이션 테스트"""
        results = {}
        errors = []
        
        def worker(worker_id):
            try:
                state = StateManager.create_initial_state(f"session-{worker_id}", f"query-{worker_id}")
                
                for i in range(10):
                    state = StateManager.update_state(state, {
                        "iteration": i,
                        "worker_id": worker_id,
                        "timestamp": time.time()
                    })
                    
                    serialized = StateManager.serialize_state(state)
                    deserialized = StateManager.deserialize_state(serialized)
                    
                    assert deserialized["worker_id"] == worker_id
                
                results[worker_id] = state
            except Exception as e:
                errors.append(f"Worker {worker_id}: {str(e)}")
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        for worker_id, state in results.items():
            assert state["session_id"] == f"session-{worker_id}"
            assert state["user_query"] == f"query-{worker_id}"
            assert state["iteration"] == 9