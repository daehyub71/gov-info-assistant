"""
사이드바 컴포넌트

네비게이션과 설정 옵션을 제공하는 사이드바를 렌더링합니다.
"""

import streamlit as st
from datetime import datetime


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        # 로고 및 서비스 정보
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #1e40af;">🏛️ 정부문서 AI</h2>
            <p style="color: #64748b; font-size: 0.9rem;">
                Version 1.0.0<br>
                일반시민 맞춤형 서비스
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 메인 네비게이션
        st.markdown("### 📋 메뉴")
        
        # 페이지 선택
        page_options = {
            "🔍 검색": "검색",
            "💬 대화상담": "대화상담", 
            "📂 카테고리 탐색": "카테고리 탐색",
            "❓ 도움말": "도움말"
        }
        
        selected_page = st.radio(
            "페이지 선택",
            options=list(page_options.keys()),
            index=0,
            label_visibility="collapsed"
        )
        
        # 선택된 페이지를 세션 상태에 저장
        st.session_state.current_page = page_options[selected_page]
        
        st.divider()
        
        # 검색 설정 (검색 페이지일 때만 표시)
        if st.session_state.current_page == "검색":
            render_search_settings()
        
        # 채팅 설정 (대화상담 페이지일 때만 표시)
        elif st.session_state.current_page == "대화상담":
            render_chat_settings()
        
        st.divider()
        
        # 사용 통계
        render_usage_stats()
        
        st.divider()
        
        # 피드백 섹션
        render_feedback_section()


def render_search_settings():
    """검색 설정 옵션"""
    st.markdown("### ⚙️ 검색 설정")
    
    # 카테고리 필터
    categories = [
        "전체", "정책안내", "행정절차", "복지혜택", 
        "세금정보", "사업지원", "교육지원"
    ]
    
    selected_category = st.selectbox(
        "카테고리 필터",
        categories,
        index=0
    )
    
    # 검색 결과 수
    max_results = st.slider(
        "검색 결과 수",
        min_value=3,
        max_value=10,
        value=5,
        help="한 번에 표시할 검색 결과의 개수"
    )
    
    # 응답 상세도
    detail_level = st.radio(
        "응답 상세도",
        ["간단히", "보통", "자세히"],
        index=1,
        help="AI 응답의 자세한 정도를 선택하세요"
    )
    
    # 설정을 세션 상태에 저장
    st.session_state.search_settings = {
        "category": selected_category,
        "max_results": max_results,
        "detail_level": detail_level
    }


def render_chat_settings():
    """채팅 설정 옵션"""
    st.markdown("### 💬 채팅 설정")
    
    # 채팅 스타일
    chat_style = st.radio(
        "응답 스타일",
        ["친근한 톤", "정중한 톤", "전문적 톤"],
        index=0,
        help="AI 응답의 말투를 선택하세요"
    )
    
    # 응답 속도
    response_speed = st.radio(
        "응답 속도",
        ["빠른 응답", "균형잡힌", "정확한 응답"],
        index=1,
        help="응답 속도와 정확도의 균형을 조절합니다"
    )
    
    # 대화 기록 저장
    save_history = st.checkbox(
        "대화 기록 저장",
        value=True,
        help="대화 내용을 저장하여 다음에도 이어서 상담받을 수 있습니다"
    )
    
    # 새 대화 시작 버튼
    if st.button("🔄 새 대화 시작", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.chat_history = []
        st.success("새로운 대화를 시작합니다!")
        st.rerun()
    
    # 설정을 세션 상태에 저장
    st.session_state.chat_settings = {
        "style": chat_style,
        "speed": response_speed,
        "save_history": save_history
    }


def render_usage_stats():
    """사용 통계 표시"""
    st.markdown("### 📊 오늘의 활동")
    
    # TODO: 실제 사용 통계 데이터 연동 (Day 6에서)
    # 현재는 더미 데이터 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("검색 횟수", "12", "2")
    
    with col2:
        st.metric("대화 수", "3", "1")
    
    # 최근 검색어
    if 'search_history' in st.session_state and st.session_state.search_history:
        st.markdown("**최근 검색어**")
        for i, query in enumerate(st.session_state.search_history[-3:]):
            st.markdown(f"• {query}")
    else:
        st.markdown("**최근 검색어**")
        st.markdown("• 아직 검색 기록이 없습니다")


def render_feedback_section():
    """피드백 섹션"""
    st.markdown("### 💬 의견 보내기")
    
    feedback_type = st.selectbox(
        "피드백 유형",
        ["개선 제안", "버그 신고", "새 기능 요청", "기타"]
    )
    
    feedback_text = st.text_area(
        "의견을 자유롭게 적어주세요",
        placeholder="서비스 개선을 위한 소중한 의견을 들려주세요...",
        max_chars=500
    )
    
    if st.button("📤 의견 보내기", use_container_width=True):
        if feedback_text.strip():
            # TODO: 실제 피드백 전송 로직 (Day 6에서)
            st.success("소중한 의견 감사합니다! 검토 후 반영하겠습니다.")
            st.balloons()
        else:
            st.warning("피드백 내용을 입력해주세요.")
    
    # 서비스 정보
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.8rem;">
        <p>🤖 AI 기반 정부문서 검색<br>
        📅 {today}<br>
        ⚡ 서버 상태: 정상</p>
    </div>
    """.format(today=datetime.now().strftime("%Y.%m.%d")), unsafe_allow_html=True)
