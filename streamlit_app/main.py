"""
정부 공문서 AI 검색 서비스 - 메인 애플리케이션

일반 시민을 위한 정부 공문서 AI 검색 서비스의 Streamlit 메인 페이지입니다.
"""

import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.search_interface import render_search_interface
from streamlit_app.components.chat_interface import render_chat_interface
from streamlit_app.services.api_client import APIClient
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="정부 공문서 AI 검색 서비스",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 2rem;
    }
    .search-container {
        background-color: #f8fafc;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .service-description {
        background-color: #e0f2fe;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #0369a1;
    }
    .stButton > button {
        background-color: #1e40af;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #1d4ed8;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """세션 상태 초기화"""
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "검색"


def main():
    """메인 애플리케이션 함수"""
    # 세션 상태 초기화
    initialize_session_state()
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ 정부 공문서 AI 검색 서비스</h1>
        <p style="font-size: 1.2rem; color: #64748b;">
            복잡한 정부 정책과 공문서를 쉽게 이해할 수 있도록 도와드립니다
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 렌더링
    render_sidebar()
    
    # 메인 컨텐츠 영역
    if st.session_state.current_page == "검색":
        render_search_page()
    elif st.session_state.current_page == "대화상담":
        render_chat_page()
    elif st.session_state.current_page == "카테고리 탐색":
        render_category_page()
    elif st.session_state.current_page == "도움말":
        render_help_page()


def render_search_page():
    """검색 페이지 렌더링"""
    st.markdown("""
    <div class="service-description">
        <h3>🔍 똑똑한 정부 문서 검색</h3>
        <p>
            일상 언어로 질문하시면, AI가 관련된 정부 정책과 문서를 찾아서 
            이해하기 쉽게 설명해드립니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 검색 인터페이스 렌더링
    render_search_interface()


def render_chat_page():
    """대화상담 페이지 렌더링"""
    st.markdown("""
    <div class="service-description">
        <h3>💬 대화형 정부 정책 상담</h3>
        <p>
            궁금한 점을 자유롭게 물어보세요. AI 상담원이 단계별로 
            필요한 정보와 절차를 안내해드립니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 채팅 인터페이스 렌더링
    render_chat_interface()


def render_category_page():
    """카테고리 탐색 페이지 렌더링"""
    st.markdown("""
    <div class="service-description">
        <h3>📂 분야별 정책 탐색</h3>
        <p>
            관심 있는 분야를 선택하여 관련 정책과 지원사업을 
            체계적으로 둘러보세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # TODO: 카테고리 브라우징 구현 (Day 5에서)
    st.info("🚧 카테고리 탐색 기능은 곧 구현됩니다.")
    
    # 임시 카테고리 목록
    categories = [
        {"name": "💼 사업지원", "count": 203, "description": "창업, 사업자 등록, 지원금 정보"},
        {"name": "👶 출산/육아", "count": 89, "description": "출산 지원금, 육아휴직, 보육 정책"},
        {"name": "🏠 주거복지", "count": 156, "description": "주택 구입, 전세자금, 임대주택 정보"},
        {"name": "💰 세금정보", "count": 178, "description": "소득세, 법인세, 세금 감면 혜택"},
        {"name": "🎓 교육지원", "count": 134, "description": "장학금, 교육비 지원, 평생교육"},
    ]
    
    col1, col2 = st.columns(2)
    for i, category in enumerate(categories):
        with col1 if i % 2 == 0 else col2:
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                    <h4>{category['name']}</h4>
                    <p style="color: #64748b; margin: 0.5rem 0;">{category['description']}</p>
                    <small style="color: #94a3b8;">📄 {category['count']}개 문서</small>
                </div>
                """, unsafe_allow_html=True)


def render_help_page():
    """도움말 페이지 렌더링"""
    st.markdown("""
    <div class="service-description">
        <h3>❓ 서비스 이용 가이드</h3>
        <p>
            정부 공문서 AI 검색 서비스를 효과적으로 사용하는 방법을 
            안내해드립니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ## 🎯 이런 질문을 해보세요
    
    ### 📋 절차 문의
    - "주민등록등본은 어디서 발급받나요?"
    - "사업자 등록 절차를 알려주세요"
    - "출산 지원금 신청 방법이 궁금해요"
    
    ### 💡 정책 정보
    - "청년 창업 지원 정책은 무엇이 있나요?"
    - "전세자금대출 조건을 알려주세요"
    - "교육비 지원 혜택에 대해 설명해주세요"
    
    ### 🔍 검색 팁
    - **구체적으로 질문하세요**: "세금" 보다는 "소득세 신고 방법"
    - **일상 언어로 편하게**: 전문 용어 대신 평소 말하는 방식으로
    - **단계별로 물어보세요**: 복잡한 내용은 나누어서 질문
    
    ## 🛠️ 주요 기능
    
    ### 🔍 스마트 검색
    자연어 질문을 분석하여 가장 관련성 높은 정부 문서를 찾아드립니다.
    
    ### 💬 대화형 상담
    궁금한 점을 자유롭게 대화하며 단계별 안내를 받을 수 있습니다.
    
    ### 📂 카테고리 탐색
    분야별로 체계적으로 정리된 정책 정보를 둘러볼 수 있습니다.
    
    ## 📞 문의하기
    
    서비스 이용 중 문제가 있거나 개선 사항이 있으시면 언제든 연락해주세요.
    
    📧 support@gov-info-assistant.kr  
    📞 1588-0000 (평일 09:00~18:00)
    """)


if __name__ == "__main__":
    main()
