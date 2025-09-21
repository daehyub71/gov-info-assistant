"""
정부 공문서 AI 검색 서비스 - 메인 애플리케이션

시민 친화적인 정부 공문서 검색 및 상담 서비스를 제공합니다.
"""

import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def main():
    """메인 애플리케이션 진입점"""
    st.set_page_config(
        page_title="정부 공문서 AI 검색",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏛️ 정부 공문서 AI 검색 서비스")
    st.markdown("---")
    
    # 임시 환영 메시지
    st.success("👋 안녕하세요! 정부 공문서를 쉽고 빠르게 검색해보세요.")
    
    # 검색 입력 폼
    with st.form("search_form"):
        query = st.text_input(
            "궁금한 정부 정책이나 제도를 검색해보세요:",
            placeholder="예: 청년 주택 정책, 창업 지원 제도 등"
        )
        submitted = st.form_submit_button("🔍 검색하기")
        
        if submitted and query:
            st.info(f"'{query}' 검색 결과를 준비 중입니다...")
            # TODO: 실제 검색 로직 연동
    
    # 사이드바 - 카테고리 및 도움말
    with st.sidebar:
        st.header("📋 카테고리")
        categories = [
            "복지 정책",
            "교육 정책", 
            "주택 정책",
            "창업 지원",
            "세금 혜택",
            "기타"
        ]
        selected_category = st.selectbox("관심 분야를 선택하세요", categories)
        
        st.header("❓ 도움말")
        st.info("""
        **사용 방법:**
        1. 검색창에 궁금한 내용을 입력하세요
        2. 카테고리를 선택하여 범위를 좁혀보세요
        3. AI가 관련 정보를 쉽게 설명해드립니다
        """)

if __name__ == "__main__":
    main()
