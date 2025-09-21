"""
채팅 인터페이스 컴포넌트

사용자와 AI 간의 대화형 상담을 담당하는 컴포넌트입니다.
"""

import streamlit as st
from streamlit_app.services.api_client import get_api_client, safe_api_call
from datetime import datetime
import time


def render_chat_interface():
    """채팅 인터페이스 렌더링"""
    
    # 채팅 세션 초기화
    initialize_chat_session()
    
    # 채팅 히스토리 표시
    render_chat_history()
    
    # 메시지 입력 영역
    render_message_input()
    
    # 추천 질문 버튼들
    render_suggested_questions()


def initialize_chat_session():
    """채팅 세션 초기화"""
    
    # 세션 상태 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'session_id' not in st.session_state or st.session_state.session_id is None:
        # 새 세션 생성
        client = get_api_client()
        session_data = safe_api_call(client.create_session)
        
        if session_data:
            st.session_state.session_id = session_data.get('session_id')
            st.session_state.chat_start_time = datetime.now()
            
            # 환영 메시지 추가
            welcome_message = {
                "type": "assistant",
                "content": "안녕하세요! 👋 정부 공문서 전문 AI 상담원입니다. 궁금한 정책이나 행정 절차에 대해 무엇이든 편하게 물어보세요.",
                "timestamp": datetime.now(),
                "suggestions": [
                    "주민등록등본 발급 방법",
                    "출산 지원금 신청 절차", 
                    "사업자 등록 필요 서류"
                ]
            }
            st.session_state.chat_history.append(welcome_message)


def render_chat_history():
    """채팅 히스토리 표시"""
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    with chat_container:
        # 채팅 시작 시간 표시
        if 'chat_start_time' in st.session_state:
            st.markdown(f"**🕐 상담 시작:** {st.session_state.chat_start_time.strftime('%Y-%m-%d %H:%M')}")
            st.markdown("---")
        
        # 메시지 히스토리 표시
        for i, message in enumerate(st.session_state.chat_history):
            render_message(message, i)
        
        # 자동 스크롤을 위한 앵커
        st.markdown('<div id="chat-bottom"></div>', unsafe_allow_html=True)


def render_message(message: dict, index: int):
    """개별 메시지 렌더링"""
    
    message_type = message.get('type', 'user')
    content = message.get('content', '')
    timestamp = message.get('timestamp', datetime.now())
    
    if message_type == 'user':
        # 사용자 메시지 (오른쪽 정렬)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
            <div style="max-width: 70%; background-color: #1f77b4; color: white; 
                        padding: 1rem; border-radius: 15px 15px 5px 15px; 
                        word-wrap: break-word;">
                <div style="margin-bottom: 0.5rem;">{content}</div>
                <div style="font-size: 0.8rem; opacity: 0.8; text-align: right;">
                    👤 {timestamp.strftime('%H:%M')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # AI 응답 (왼쪽 정렬)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; margin: 1rem 0;">
            <div style="max-width: 70%; background-color: #f0f2f6; color: #262730; 
                        padding: 1rem; border-radius: 15px 15px 15px 5px; 
                        word-wrap: break-word; border-left: 4px solid #1f77b4;">
                <div style="margin-bottom: 0.5rem;">{content}</div>
                <div style="font-size: 0.8rem; opacity: 0.6;">
                    🤖 AI 상담원 {timestamp.strftime('%H:%M')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 추천 질문이 있으면 버튼으로 표시
        suggestions = message.get('suggestions', [])
        if suggestions:
            st.markdown("**💡 관련 질문:**")
            
            # 추천 질문을 버튼으로 표시
            suggestion_cols = st.columns(min(len(suggestions), 2))
            
            for i, suggestion in enumerate(suggestions):
                col_idx = i % 2
                with suggestion_cols[col_idx]:
                    if st.button(
                        f"💬 {suggestion}",
                        key=f"suggestion_{index}_{i}",
                        use_container_width=True
                    ):
                        # 추천 질문 클릭 시 자동으로 메시지 전송
                        send_message(suggestion)
                        st.rerun()


def render_message_input():
    """메시지 입력 영역"""
    
    st.markdown("---")
    st.markdown("### 💬 메시지 입력")
    
    # 메시지 입력 폼
    with st.form(key="message_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_message = st.text_area(
                "메시지를 입력하세요",
                placeholder="궁금한 점을 자유롭게 질문해주세요...",
                height=100,
                key="message_input",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # 공간 조정
            send_button = st.form_submit_button(
                "📤 전송",
                use_container_width=True,
                type="primary"
            )
        
        # 메시지 전송 처리
        if send_button and user_message.strip():
            send_message(user_message.strip())
            st.rerun()
        elif send_button:
            st.warning("메시지를 입력해주세요.")
    
    # 빠른 액션 버튼들
    st.markdown("**⚡ 빠른 액션:**")
    action_cols = st.columns(4)
    
    with action_cols[0]:
        if st.button("🔄 새 대화", use_container_width=True):
            start_new_conversation()
            st.rerun()
    
    with action_cols[1]:
        if st.button("📋 대화 저장", use_container_width=True):
            save_conversation()
    
    with action_cols[2]:
        if st.button("🔍 검색으로", use_container_width=True):
            st.session_state.current_page = "검색"
            st.rerun()
    
    with action_cols[3]:
        if st.button("❓ 도움말", use_container_width=True):
            st.session_state.current_page = "도움말"
            st.rerun()


def render_suggested_questions():
    """추천 질문 영역"""
    
    st.markdown("---")
    st.markdown("### 🎯 이런 질문들이 많이 물어봐요")
    
    # 카테고리별 추천 질문
    common_questions = {
        "🏠 주거/부동산": [
            "전세자금대출 조건은 무엇인가요?",
            "주택청약 신청 방법을 알려주세요",
            "임대주택 입주 자격이 궁금해요"
        ],
        "👶 출산/육아": [
            "출산 지원금은 얼마나 받을 수 있나요?",
            "육아휴직 신청 절차를 알려주세요",
            "어린이집 입소 신청은 어떻게 하나요?"
        ],
        "💼 사업/취업": [
            "사업자 등록 필요 서류가 무엇인가요?",
            "청년 창업 지원 정책을 알려주세요",
            "고용보험 실업급여 신청 방법은?"
        ],
        "📋 민원/증명": [
            "주민등록등본 온라인 발급 방법",
            "가족관계증명서는 어디서 발급받나요?",
            "인감증명서 발급 절차를 알려주세요"
        ]
    }
    
    # 탭으로 카테고리 분리
    tab_names = list(common_questions.keys())
    tabs = st.tabs(tab_names)
    
    for i, (category, questions) in enumerate(common_questions.items()):
        with tabs[i]:
            for question in questions:
                if st.button(
                    f"💬 {question}",
                    key=f"common_{category}_{question}",
                    use_container_width=True
                ):
                    send_message(question)
                    st.rerun()


def send_message(message: str):
    """메시지 전송 처리"""
    
    # 사용자 메시지를 히스토리에 추가
    user_message = {
        "type": "user",
        "content": message,
        "timestamp": datetime.now()
    }
    st.session_state.chat_history.append(user_message)
    
    # 로딩 표시를 위한 임시 메시지 추가
    loading_message = {
        "type": "assistant",
        "content": "🤔 답변을 생각하고 있습니다...",
        "timestamp": datetime.now()
    }
    st.session_state.chat_history.append(loading_message)
    
    # API 호출하여 AI 응답 받기
    with st.spinner('AI가 답변을 준비하고 있습니다...'):
        client = get_api_client()
        
        response_data = safe_api_call(
            client.send_message,
            message,
            st.session_state.session_id
        )
        
        # 로딩 메시지 제거
        st.session_state.chat_history.pop()
        
        if response_data:
            # AI 응답을 히스토리에 추가
            ai_message = {
                "type": "assistant",
                "content": response_data.get('message', '죄송합니다. 응답을 생성할 수 없습니다.'),
                "timestamp": datetime.now(),
                "suggestions": response_data.get('suggested_questions', []),
                "confidence": response_data.get('confidence_score', 0)
            }
            st.session_state.chat_history.append(ai_message)
            
            # 세션 ID 업데이트 (응답에서 받은 경우)
            if response_data.get('session_id'):
                st.session_state.session_id = response_data['session_id']
        
        else:
            # 오류 응답 추가
            error_message = {
                "type": "assistant",
                "content": "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "timestamp": datetime.now()
            }
            st.session_state.chat_history.append(error_message)


def start_new_conversation():
    """새 대화 시작"""
    
    # 기존 채팅 데이터 초기화
    st.session_state.chat_history = []
    st.session_state.session_id = None
    st.session_state.chat_start_time = None
    
    # 새 세션 초기화
    initialize_chat_session()
    
    st.success("새로운 대화를 시작합니다! 🎉")


def save_conversation():
    """대화 내용 저장"""
    
    if not st.session_state.chat_history:
        st.warning("저장할 대화 내용이 없습니다.")
        return
    
    # 대화 내용을 텍스트로 변환
    conversation_text = f"# 정부 공문서 AI 상담 기록\n\n"
    conversation_text += f"**상담 일시:** {st.session_state.get('chat_start_time', datetime.now()).strftime('%Y-%m-%d %H:%M')}\n"
    conversation_text += f"**세션 ID:** {st.session_state.get('session_id', 'N/A')}\n\n"
    conversation_text += "---\n\n"
    
    for message in st.session_state.chat_history:
        if message['type'] == 'user':
            conversation_text += f"**👤 질문 ({message['timestamp'].strftime('%H:%M')})**\n"
            conversation_text += f"{message['content']}\n\n"
        else:
            conversation_text += f"**🤖 답변 ({message['timestamp'].strftime('%H:%M')})**\n"
            conversation_text += f"{message['content']}\n\n"
            
            # 추천 질문이 있으면 추가
            if message.get('suggestions'):
                conversation_text += "**관련 질문:**\n"
                for suggestion in message['suggestions']:
                    conversation_text += f"- {suggestion}\n"
                conversation_text += "\n"
    
    # 다운로드 버튼 제공
    st.download_button(
        label="📥 대화 기록 다운로드",
        data=conversation_text,
        file_name=f"정부문서_AI상담_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )
    
    st.success("대화 기록이 준비되었습니다! 다운로드 버튼을 클릭하세요.")
