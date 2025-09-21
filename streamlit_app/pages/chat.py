"""
대화형 채팅 페이지

AI와의 실시간 대화를 통한 정부 정책 상담 기능을 제공합니다.
"""

import streamlit as st
from datetime import datetime

def show_chat_page():
    """대화형 채팅 페이지 표시"""
    st.header("💬 AI 정책 상담사와 대화하기")
    st.markdown("---")
    
    # 채팅 히스토리 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "안녕하세요! 정부 정책에 대해 궁금한 것이 있으면 언제든 물어보세요. 😊",
                "timestamp": datetime.now()
            }
        ]
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
                    st.caption(f"🕐 {message['timestamp'].strftime('%H:%M')}")
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    st.caption(f"🕐 {message['timestamp'].strftime('%H:%M')}")
    
    # 메시지 입력
    user_input = st.chat_input("메시지를 입력하세요...")
    
    if user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        # AI 응답 (임시)
        ai_response = f"'{user_input}'에 대한 정보를 찾고 있습니다. 잠시만 기다려주세요!"
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": ai_response,
            "timestamp": datetime.now()
        })
        
        # 페이지 새로고침
        st.rerun()

if __name__ == "__main__":
    show_chat_page()
