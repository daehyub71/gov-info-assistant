"""
공통 유틸리티 함수들

Streamlit 앱에서 공통으로 사용되는 헬퍼 함수들입니다.
"""

import streamlit as st
import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

def generate_session_id() -> str:
    """
    고유한 세션 ID 생성
    
    Returns:
        UUID 기반 세션 ID
    """
    return str(uuid.uuid4())

def hash_query(query: str) -> str:
    """
    검색 쿼리 해시값 생성 (캐싱용)
    
    Args:
        query: 검색 쿼리
        
    Returns:
        MD5 해시값
    """
    return hashlib.md5(query.encode()).hexdigest()

def format_datetime(dt: datetime) -> str:
    """
    날짜시간 포맷팅
    
    Args:
        dt: datetime 객체
        
    Returns:
        포맷된 날짜시간 문자열
    """
    return dt.strftime("%Y년 %m월 %d일 %H:%M")

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    텍스트 자르기
    
    Args:
        text: 원본 텍스트
        max_length: 최대 길이
        
    Returns:
        자른 텍스트
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def sanitize_input(user_input: str) -> str:
    """
    사용자 입력 정제
    
    Args:
        user_input: 사용자 입력 문자열
        
    Returns:
        정제된 문자열
    """
    # HTML 태그 제거 및 기본 정제
    import re
    
    # HTML 태그 제거
    clean_text = re.sub('<[^<]+?>', '', user_input)
    
    # 연속된 공백 제거
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    # 앞뒤 공백 제거
    clean_text = clean_text.strip()
    
    return clean_text

def save_to_session_state(key: str, value: Any) -> None:
    """
    세션 상태에 값 저장
    
    Args:
        key: 저장할 키
        value: 저장할 값
    """
    st.session_state[key] = value

def load_from_session_state(key: str, default: Any = None) -> Any:
    """
    세션 상태에서 값 로드
    
    Args:
        key: 로드할 키
        default: 기본값
        
    Returns:
        저장된 값 또는 기본값
    """
    return st.session_state.get(key, default)

def clear_session_state() -> None:
    """세션 상태 초기화"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def display_error_message(error: str, title: str = "오류 발생") -> None:
    """
    에러 메시지 표시
    
    Args:
        error: 에러 메시지
        title: 에러 제목
    """
    st.error(f"**{title}**\n\n{error}")

def display_success_message(message: str, title: str = "성공") -> None:
    """
    성공 메시지 표시
    
    Args:
        message: 성공 메시지
        title: 성공 제목
    """
    st.success(f"**{title}**\n\n{message}")

def create_download_link(data: str, filename: str, link_text: str) -> str:
    """
    다운로드 링크 생성
    
    Args:
        data: 다운로드할 데이터
        filename: 파일명
        link_text: 링크 텍스트
        
    Returns:
        HTML 다운로드 링크
    """
    import base64
    
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def validate_query(query: str) -> tuple[bool, str]:
    """
    검색 쿼리 유효성 검사
    
    Args:
        query: 검색 쿼리
        
    Returns:
        (유효성 여부, 에러 메시지)
    """
    if not query or not query.strip():
        return False, "검색어를 입력해주세요."
    
    if len(query.strip()) < 2:
        return False, "검색어는 2글자 이상 입력해주세요."
    
    if len(query) > 500:
        return False, "검색어는 500글자 이하로 입력해주세요."
    
    return True, ""

def get_user_feedback_widget(key: str = "feedback") -> Optional[Dict[str, Any]]:
    """
    사용자 피드백 위젯 표시
    
    Args:
        key: 위젯 고유 키
        
    Returns:
        피드백 데이터 또는 None
    """
    st.markdown("---")
    st.subheader("📝 이 답변이 도움이 되었나요?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👍 좋아요", key=f"{key}_good"):
            return {"type": "good", "timestamp": datetime.now()}
    
    with col2:
        if st.button("👎 별로예요", key=f"{key}_bad"):
            return {"type": "bad", "timestamp": datetime.now()}
    
    with col3:
        if st.button("💡 개선 제안", key=f"{key}_suggest"):
            suggestion = st.text_area("개선사항을 알려주세요:", key=f"{key}_text")
            if suggestion:
                return {"type": "suggestion", "text": suggestion, "timestamp": datetime.now()}
    
    return None

def load_custom_css() -> None:
    """커스텀 CSS 로드"""
    st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .search-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e1e5e9;
    }
    
    .result-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
