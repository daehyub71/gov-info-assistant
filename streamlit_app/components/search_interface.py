"""
검색 인터페이스 컴포넌트

사용자의 검색 입력과 결과 표시를 담당하는 컴포넌트입니다.
"""

import streamlit as st
from streamlit_app.services.api_client import get_api_client, safe_api_call
from datetime import datetime
import time


def render_search_interface():
    """검색 인터페이스 렌더링"""
    
    # 검색 입력 영역
    render_search_input()
    
    # 인기 검색어
    render_popular_queries()
    
    # 검색 결과 표시
    if 'last_search_results' in st.session_state:
        render_search_results(st.session_state.last_search_results)


def render_search_input():
    """검색 입력 폼"""
    
    with st.container():
        st.markdown("""
        <div class="search-container">
        """, unsafe_allow_html=True)
        
        # 검색 예시 문구
        st.markdown("""
        **💡 이렇게 질문해보세요:**
        - "주민등록등본은 어떻게 발급받나요?"
        - "출산 지원금 신청 방법을 알려주세요"
        - "사업자 등록에 필요한 서류가 무엇인가요?"
        """)
        
        # 검색 입력
        col1, col2 = st.columns([4, 1])
        
        with col1:
            search_query = st.text_input(
                "질문을 입력하세요",
                placeholder="궁금한 정부 정책이나 절차를 자유롭게 질문해주세요...",
                key="search_input",
                label_visibility="collapsed"
            )
        
        with col2:
            search_button = st.button(
                "🔍 검색",
                use_container_width=True,
                type="primary"
            )
        
        # 고급 검색 옵션 (토글)
        with st.expander("🔧 고급 검색 옵션"):
            col1, col2 = st.columns(2)
            
            with col1:
                category_filter = st.selectbox(
                    "카테고리",
                    ["전체", "정책안내", "행정절차", "복지혜택", "세금정보", "사업지원"],
                    key="category_filter"
                )
            
            with col2:
                result_count = st.slider(
                    "결과 수",
                    min_value=3,
                    max_value=10,
                    value=5,
                    key="result_count"
                )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 검색 실행
        if search_button and search_query.strip():
            perform_search(search_query, category_filter, result_count)
        elif search_button:
            st.warning("검색어를 입력해주세요.")


def render_popular_queries():
    """인기 검색어 표시"""
    
    st.markdown("### 🔥 인기 검색어")
    
    # API에서 인기 검색어 가져오기
    client = get_api_client()
    popular_queries = safe_api_call(client.get_popular_queries)
    
    if popular_queries:
        # 인기 검색어를 버튼으로 표시
        cols = st.columns(min(len(popular_queries), 3))
        
        for i, query in enumerate(popular_queries[:6]):  # 최대 6개만 표시
            col_idx = i % 3
            with cols[col_idx]:
                if st.button(
                    f"🔍 {query}",
                    key=f"popular_{i}",
                    use_container_width=True
                ):
                    # 인기 검색어 클릭 시 자동 검색
                    st.session_state.search_input = query
                    perform_search(query)
                    st.rerun()
    else:
        st.info("인기 검색어를 불러오는 중입니다...")


def perform_search(query: str, category: str = "전체", max_results: int = 5):
    """검색 실행"""
    
    # 로딩 표시
    with st.spinner('검색 중입니다...'):
        start_time = time.time()
        
        # API 클라이언트로 검색 요청
        client = get_api_client()
        
        # 카테고리 필터 처리 (전체는 None으로)
        category_param = None if category == "전체" else category
        
        # 검색 실행
        search_results = safe_api_call(
            client.search_documents,
            query,
            category_param,
            max_results
        )
        
        end_time = time.time()
        
        if search_results:
            # 검색 결과를 세션 상태에 저장
            st.session_state.last_search_results = search_results
            st.session_state.last_search_query = query
            st.session_state.search_time = end_time - start_time
            
            # 검색 히스토리에 추가
            if 'search_history' not in st.session_state:
                st.session_state.search_history = []
            
            if query not in st.session_state.search_history:
                st.session_state.search_history.append(query)
                # 최대 10개까지만 유지
                if len(st.session_state.search_history) > 10:
                    st.session_state.search_history.pop(0)
            
            st.success(f"검색 완료! ({end_time - start_time:.2f}초)")
            st.rerun()
        else:
            st.error("검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")


def render_search_results(results: dict):
    """검색 결과 표시"""
    
    if not results or not results.get('results'):
        st.info("검색 결과가 없습니다.")
        return
    
    st.markdown("---")
    st.markdown(f"### 🔍 '{st.session_state.get('last_search_query', '')}' 검색 결과")
    
    # 검색 요약 정보
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 결과", f"{results.get('total_count', 0)}개")
    
    with col2:
        st.metric("처리 시간", f"{results.get('processing_time', 0):.2f}초")
    
    with col3:
        st.metric("신뢰도", f"{results.get('confidence_score', 0):.0%}")
    
    # AI 요약
    if results.get('summary'):
        st.markdown("#### 🤖 AI 요약")
        st.info(results['summary'])
    
    # 개별 검색 결과
    st.markdown("#### 📄 관련 문서")
    
    for i, result in enumerate(results['results']):
        with st.expander(f"📋 {result.get('title', '제목 없음')}", expanded=(i == 0)):
            render_single_result(result, i)
    
    # 연관 검색어 추천
    if results.get('suggestions'):
        st.markdown("#### 💡 연관 검색어")
        
        suggestion_cols = st.columns(min(len(results['suggestions']), 3))
        
        for i, suggestion in enumerate(results['suggestions']):
            col_idx = i % 3
            with suggestion_cols[col_idx]:
                if st.button(
                    f"🔗 {suggestion}",
                    key=f"suggestion_{i}",
                    use_container_width=True
                ):
                    st.session_state.search_input = suggestion
                    perform_search(suggestion)
                    st.rerun()


def render_single_result(result: dict, index: int):
    """개별 검색 결과 렌더링"""
    
    # 결과 메타데이터
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**카테고리:** {result.get('category', '미분류')}")
    
    with col2:
        confidence = result.get('confidence_score', 0)
        st.markdown(f"**관련도:** {confidence:.0%}")
    
    with col3:
        publish_date = result.get('publish_date', '')
        if publish_date:
            st.markdown(f"**발행일:** {publish_date}")
    
    # 내용 미리보기
    content = result.get('content', '')
    if content:
        # 내용이 너무 길면 자르기
        if len(content) > 300:
            preview = content[:300] + "..."
        else:
            preview = content
        
        st.markdown("**내용 미리보기:**")
        st.markdown(f"> {preview}")
    
    # 액션 버튼들
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"📖 자세히 보기", key=f"detail_{index}"):
            show_detailed_view(result)
    
    with col2:
        if st.button(f"💬 관련 질문하기", key=f"chat_{index}"):
            # 채팅 페이지로 이동
            st.session_state.current_page = "대화상담"
            st.session_state.chat_context = result
            st.rerun()
    
    with col3:
        source_url = result.get('source_url', '')
        if source_url:
            st.markdown(f"[🌐 원문 보기]({source_url})")


def show_detailed_view(result: dict):
    """상세보기 표시"""
    
    # Streamlit에서는 실제 모달이 없으므로 별도 영역에 표시
    st.markdown("---")
    st.markdown("### 📄 문서 상세보기")
    
    # 제목
    st.markdown(f"## {result.get('title', '제목 없음')}")
    
    # 메타데이터
    info_cols = st.columns(4)
    
    with info_cols[0]:
        st.markdown(f"**카테고리**  \n{result.get('category', '미분류')}")
    
    with info_cols[1]:
        confidence = result.get('confidence_score', 0)
        st.markdown(f"**관련도**  \n{confidence:.0%}")
    
    with info_cols[2]:
        publish_date = result.get('publish_date', '')
        if publish_date:
            st.markdown(f"**발행일**  \n{publish_date}")
    
    with info_cols[3]:
        doc_id = result.get('id', '')
        if doc_id:
            st.markdown(f"**문서 ID**  \n{doc_id}")
    
    st.markdown("---")
    
    # 전체 내용
    content = result.get('content', '')
    if content:
        st.markdown("**전체 내용:**")
        st.markdown(content)
    
    # 원문 링크
    source_url = result.get('source_url', '')
    if source_url:
        st.markdown(f"[🌐 원문 보기]({source_url})")
    
    # 닫기 버튼
    if st.button("❌ 닫기", key="close_detail"):
        st.rerun()
