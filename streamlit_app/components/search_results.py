"""
검색 결과 컴포넌트

검색 결과를 표시하는 재사용 가능한 컴포넌트입니다.
"""

import streamlit as st
from typing import List, Dict, Any
from datetime import datetime

def display_search_results(results: List[Dict[str, Any]], query: str = ""):
    """
    검색 결과를 표시하는 컴포넌트
    
    Args:
        results: 검색 결과 리스트
        query: 검색 쿼리
    """
    if not results:
        st.warning("검색 결과가 없습니다. 다른 키워드로 다시 검색해보세요.")
        return
    
    st.success(f"총 {len(results)}개의 관련 문서를 찾았습니다.")
    
    for i, result in enumerate(results):
        with st.expander(f"📄 {result.get('title', f'문서 {i+1}')}"):
            # 문서 메타데이터
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("관련도", f"{result.get('score', 0):.1%}")
            with col2:
                st.metric("카테고리", result.get('category', '기타'))
            with col3:
                st.metric("발행일", result.get('date', '정보없음'))
            
            # 문서 요약
            st.markdown("**📋 요약:**")
            st.info(result.get('summary', '요약 정보가 없습니다.'))
            
            # 주요 내용
            if result.get('content'):
                st.markdown("**📖 주요 내용:**")
                st.markdown(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
            
            # 액션 버튼
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"전체 보기", key=f"view_{i}"):
                    st.session_state[f"show_full_{i}"] = True
            with col2:
                if st.button(f"관련 질문", key=f"related_{i}"):
                    st.session_state[f"show_related_{i}"] = True
            with col3:
                if st.button(f"북마크", key=f"bookmark_{i}"):
                    st.success("북마크에 추가되었습니다!")

def display_document_card(document: Dict[str, Any], index: int = 0):
    """
    개별 문서 카드 컴포넌트
    
    Args:
        document: 문서 정보
        index: 인덱스 번호
    """
    with st.container():
        st.markdown(f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: #f9f9f9;
        ">
            <h4 style="color: #1f77b4; margin: 0 0 10px 0;">
                📄 {document.get('title', '제목 없음')}
            </h4>
            <p style="margin: 5px 0;">
                <strong>카테고리:</strong> {document.get('category', '기타')} | 
                <strong>발행일:</strong> {document.get('date', '정보없음')} |
                <strong>관련도:</strong> {document.get('score', 0):.1%}
            </p>
            <p style="margin: 10px 0;">
                {document.get('summary', '요약 정보가 없습니다.')[:200]}...
            </p>
        </div>
        """, unsafe_allow_html=True)

def display_loading_spinner(message: str = "처리 중..."):
    """
    로딩 스피너 컴포넌트
    
    Args:
        message: 로딩 메시지
    """
    with st.spinner(message):
        st.empty()

def display_stats_metrics(stats: Dict[str, Any]):
    """
    통계 메트릭 컴포넌트
    
    Args:
        stats: 통계 정보
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="총 검색 횟수",
            value=stats.get('total_searches', 0),
            delta=stats.get('searches_delta', 0)
        )
    
    with col2:
        st.metric(
            label="평균 응답 시간",
            value=f"{stats.get('avg_response_time', 0):.1f}초",
            delta=f"{stats.get('response_time_delta', 0):.1f}초"
        )
    
    with col3:
        st.metric(
            label="만족도",
            value=f"{stats.get('satisfaction', 0):.1%}",
            delta=f"{stats.get('satisfaction_delta', 0):.1%}"
        )
    
    with col4:
        st.metric(
            label="활성 사용자",
            value=stats.get('active_users', 0),
            delta=stats.get('users_delta', 0)
        )
