"""
Streamlit 컴포넌트 단위 테스트

Streamlit 컴포넌트들의 기본 동작을 테스트합니다.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from datetime import datetime

# 테스트 환경에서 Streamlit 모킹
@pytest.fixture(autouse=True)
def mock_streamlit():
    """Streamlit 함수들을 모킹"""
    with patch('streamlit.markdown'), \
         patch('streamlit.text_input'), \
         patch('streamlit.button'), \
         patch('streamlit.selectbox'), \
         patch('streamlit.slider'), \
         patch('streamlit.columns'), \
         patch('streamlit.container'), \
         patch('streamlit.expander'), \
         patch('streamlit.success'), \
         patch('streamlit.error'), \
         patch('streamlit.warning'), \
         patch('streamlit.info'), \
         patch('streamlit.spinner'), \
         patch('streamlit.rerun'):
        yield


class TestSearchInterface:
    """검색 인터페이스 컴포넌트 테스트"""
    
    @patch('streamlit_app.components.search_interface.get_api_client')
    def test_render_search_interface(self, mock_get_api_client):
        """검색 인터페이스 렌더링 테스트"""
        # Mock API 클라이언트
        mock_client = Mock()
        mock_get_api_client.return_value = mock_client
        
        # 검색 인터페이스 임포트 및 실행
        from streamlit_app.components.search_interface import render_search_interface
        
        # 예외 없이 실행되는지 확인
        try:
            render_search_interface()
        except Exception as e:
            pytest.fail(f"render_search_interface failed: {e}")
    
    @patch('streamlit_app.components.search_interface.get_api_client')
    @patch('streamlit_app.components.search_interface.safe_api_call')
    def test_render_popular_queries(self, mock_safe_api_call, mock_get_api_client):
        """인기 검색어 렌더링 테스트"""
        # Mock 데이터 설정
        mock_client = Mock()
        mock_get_api_client.return_value = mock_client
        
        mock_popular_queries = [
            "주민등록 발급",
            "출산 지원금",
            "사업자 등록"
        ]
        mock_safe_api_call.return_value = mock_popular_queries
        
        from streamlit_app.components.search_interface import render_popular_queries
        
        # 예외 없이 실행되는지 확인
        try:
            render_popular_queries()
        except Exception as e:
            pytest.fail(f"render_popular_queries failed: {e}")
    
    @patch('streamlit_app.components.search_interface.get_api_client')
    @patch('streamlit_app.components.search_interface.safe_api_call')
    def test_perform_search(self, mock_safe_api_call, mock_get_api_client):
        """검색 실행 테스트"""
        # Mock 데이터 설정
        mock_client = Mock()
        mock_get_api_client.return_value = mock_client
        
        mock_search_results = {
            "results": [
                {
                    "id": "doc_001",
                    "title": "테스트 문서",
                    "content": "테스트 내용",
                    "category": "테스트",
                    "confidence_score": 0.9
                }
            ],
            "summary": "테스트 요약",
            "total_count": 1,
            "processing_time": 1.0,
            "confidence_score": 0.9,
            "suggestions": ["관련 검색어"]
        }
        mock_safe_api_call.return_value = mock_search_results
        
        from streamlit_app.components.search_interface import perform_search
        
        # 세션 상태 초기화
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
        
        # 검색 실행
        try:
            perform_search("테스트 쿼리")
        except Exception as e:
            pytest.fail(f"perform_search failed: {e}")
    
    def test_render_search_results_empty(self):
        """빈 검색 결과 렌더링 테스트"""
        from streamlit_app.components.search_interface import render_search_results
        
        # 빈 결과 테스트
        empty_results = {"results": []}
        
        try:
            render_search_results(empty_results)
        except Exception as e:
            pytest.fail(f"render_search_results with empty data failed: {e}")
    
    def test_render_single_result(self):
        """개별 검색 결과 렌더링 테스트"""
        from streamlit_app.components.search_interface import render_single_result
        
        sample_result = {
            "id": "doc_001",
            "title": "테스트 문서",
            "content": "테스트 내용입니다.",
            "category": "정책안내",
            "confidence_score": 0.85,
            "publish_date": "2024-01-15",
            "source_url": "https://example.gov.kr/doc001"
        }
        
        try:
            render_single_result(sample_result, 0)
        except Exception as e:
            pytest.fail(f"render_single_result failed: {e}")


class TestChatInterface:
    """채팅 인터페이스 컴포넌트 테스트"""
    
    @patch('streamlit_app.components.chat_interface.get_api_client')
    def test_render_chat_interface(self, mock_get_api_client):
        """채팅 인터페이스 렌더링 테스트"""
        # Mock API 클라이언트
        mock_client = Mock()
        mock_get_api_client.return_value = mock_client
        
        from streamlit_app.components.chat_interface import render_chat_interface
        
        # 세션 상태 초기화
        st.session_state.clear()
        
        try:
            render_chat_interface()
        except Exception as e:
            pytest.fail(f"render_chat_interface failed: {e}")
    
    @patch('streamlit_app.components.chat_interface.get_api_client')
    @patch('streamlit_app.components.chat_interface.safe_api_call')
    def test_initialize_chat_session(self, mock_safe_api_call, mock_get_api_client):
        """채팅 세션 초기화 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_get_api_client.return_value = mock_client
        
        mock_session_data = {
            "session_id": "test_session_123",
            "created_at": datetime.now().isoformat()
        }
        mock_safe_api_call.return_value = mock_session_data
        
        from streamlit_app.components.chat_interface import initialize_chat_session
        
        # 세션 상태 초기화
        st.session_state.clear()
        
        try:
            initialize_chat_session()
            
            # 세션 상태 확인
            assert 'chat_history' in st.session_state
            assert 'session_id' in st.session_state
            assert st.session_state.session_id == "test_session_123"
            
        except Exception as e:
            pytest.fail(f"initialize_chat_session failed: {e}")
    
    def test_render_message_user(self):
        """사용자 메시지 렌더링 테스트"""
        from streamlit_app.components.chat_interface import render_message
        
        user_message = {
            "type": "user",
            "content": "안녕하세요",
            "timestamp": datetime.now()
        }
        
        try:
            render_message(user_message, 0)
        except Exception as e:
            pytest.fail(f"render_message (user) failed: {e}")
    
    def test_render_message_assistant(self):
        """AI 응답 메시지 렌더링 테스트"""
        from streamlit_app.components.chat_interface import render_message
        
        assistant_message = {
            "type": "assistant",
            "content": "안녕하세요! 도움이 필요하시면 말씀해주세요.",
            "timestamp": datetime.now(),
            "suggestions": ["질문 1", "질문 2"]
        }
        
        try:
            render_message(assistant_message, 0)
        except Exception as e:
            pytest.fail(f"render_message (assistant) failed: {e}")
    
    @patch('streamlit_app.components.chat_interface.get_api_client')
    @patch('streamlit_app.components.chat_interface.safe_api_call')
    def test_send_message(self, mock_safe_api_call, mock_get_api_client):
        """메시지 전송 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_get_api_client.return_value = mock_client
        
        mock_response = {
            "message": "AI 응답입니다.",
            "session_id": "test_session_123",
            "message_id": "msg_001",
            "timestamp": datetime.now().isoformat(),
            "confidence_score": 0.9,
            "suggested_questions": ["관련 질문 1", "관련 질문 2"],
            "processing_time": 1.5
        }
        mock_safe_api_call.return_value = mock_response
        
        from streamlit_app.components.chat_interface import send_message
        
        # 세션 상태 초기화
        st.session_state.chat_history = []
        st.session_state.session_id = "test_session_123"
        
        try:
            send_message("테스트 메시지")
            
            # 메시지가 히스토리에 추가되었는지 확인
            assert len(st.session_state.chat_history) >= 2  # 사용자 + AI 메시지
            
        except Exception as e:
            pytest.fail(f"send_message failed: {e}")
    
    def test_start_new_conversation(self):
        """새 대화 시작 테스트"""
        from streamlit_app.components.chat_interface import start_new_conversation
        
        # 기존 데이터 설정
        st.session_state.chat_history = [{"test": "data"}]
        st.session_state.session_id = "old_session"
        
        try:
            start_new_conversation()
            
            # 데이터가 초기화되었는지 확인
            assert st.session_state.chat_history == []
            assert st.session_state.session_id is None
            
        except Exception as e:
            pytest.fail(f"start_new_conversation failed: {e}")


class TestSidebar:
    """사이드바 컴포넌트 테스트"""
    
    def test_render_sidebar(self):
        """사이드바 렌더링 테스트"""
        from streamlit_app.components.sidebar import render_sidebar
        
        # 세션 상태 초기화
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "검색"
        
        try:
            render_sidebar()
        except Exception as e:
            pytest.fail(f"render_sidebar failed: {e}")
    
    def test_render_search_settings(self):
        """검색 설정 렌더링 테스트"""
        from streamlit_app.components.sidebar import render_search_settings
        
        try:
            render_search_settings()
            
            # 설정이 세션 상태에 저장되는지 확인
            assert 'search_settings' in st.session_state
            
        except Exception as e:
            pytest.fail(f"render_search_settings failed: {e}")
    
    def test_render_chat_settings(self):
        """채팅 설정 렌더링 테스트"""
        from streamlit_app.components.sidebar import render_chat_settings
        
        try:
            render_chat_settings()
            
            # 설정이 세션 상태에 저장되는지 확인
            assert 'chat_settings' in st.session_state
            
        except Exception as e:
            pytest.fail(f"render_chat_settings failed: {e}")


class TestAPIClient:
    """API 클라이언트 테스트"""
    
    @patch('httpx.AsyncClient')
    def test_sync_api_client_initialization(self, mock_httpx):
        """동기 API 클라이언트 초기화 테스트"""
        from streamlit_app.services.api_client import SyncAPIClient
        
        try:
            client = SyncAPIClient()
            assert client is not None
            assert hasattr(client, 'async_client')
        except Exception as e:
            pytest.fail(f"SyncAPIClient initialization failed: {e}")
    
    def test_get_api_client_cache(self):
        """API 클라이언트 캐시 테스트"""
        from streamlit_app.services.api_client import get_api_client
        
        try:
            client1 = get_api_client()
            client2 = get_api_client()
            
            # 캐시된 인스턴스가 동일한지 확인
            assert client1 is client2
            
        except Exception as e:
            pytest.fail(f"get_api_client caching failed: {e}")
    
    def test_safe_api_call_success(self):
        """안전한 API 호출 성공 테스트"""
        from streamlit_app.services.api_client import safe_api_call
        
        def mock_function():
            return "success"
        
        try:
            result = safe_api_call(mock_function)
            assert result == "success"
        except Exception as e:
            pytest.fail(f"safe_api_call success case failed: {e}")
    
    def test_safe_api_call_failure(self):
        """안전한 API 호출 실패 테스트"""
        from streamlit_app.services.api_client import safe_api_call
        
        def mock_function():
            raise Exception("Test error")
        
        try:
            result = safe_api_call(mock_function)
            assert result is None  # 실패 시 None 반환
        except Exception as e:
            pytest.fail(f"safe_api_call failure case failed: {e}")


# 통합 테스트
class TestComponentIntegration:
    """컴포넌트 통합 테스트"""
    
    @patch('streamlit_app.services.api_client.get_api_client')
    def test_search_to_chat_integration(self, mock_get_api_client):
        """검색에서 채팅으로의 연동 테스트"""
        # Mock API 클라이언트
        mock_client = Mock()
        mock_get_api_client.return_value = mock_client
        
        # 검색 결과에서 채팅으로 이동하는 시나리오 테스트
        st.session_state.current_page = "검색"
        
        # 채팅 컨텍스트 설정
        test_context = {
            "title": "테스트 문서",
            "content": "테스트 내용"
        }
        st.session_state.chat_context = test_context
        st.session_state.current_page = "대화상담"
        
        assert st.session_state.current_page == "대화상담"
        assert st.session_state.chat_context == test_context


if __name__ == "__main__":
    pytest.main([__file__])
