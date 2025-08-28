import streamlit as st
from langchain.schema import HumanMessage, AIMessage
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.graph import agent_graph
from agents.state import AgentState

st.set_page_config(
    page_title="AI 챗봇 - PT Shop",
    page_icon="🤖",
    layout="wide"
)

# CSS 로드
def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'styles', 'style.css')
    with open(css_path, encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

st.markdown("""
<div class="header-container">
    <div class="header-title">🤖 AI 상담 챗봇</div>
    <div class="header-subtitle">회원 관리 및 PT 상담을 도와드립니다</div>
</div>
""", unsafe_allow_html=True)

# 채팅 기록 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 채팅 인터페이스
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 대화")
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 AI:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # 입력 폼
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_area("메시지를 입력하세요", height=100, key='user_input')
        col1_1, col1_2, col1_3 = st.columns([1, 1, 3])
        with col1_1:
            submit_button = st.form_submit_button("전송", use_container_width=True)
        with col1_2:
            clear_button = st.form_submit_button("대화 초기화", use_container_width=True)
    
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
    
    if submit_button and user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # LangGraph 에이전트 실행
        with st.spinner("AI가 응답을 생성하고 있습니다..."):
            try:
                # 초기 상태 생성
                initial_state = AgentState(
                    messages=[HumanMessage(content=user_input)],
                    current_member=None,
                    search_results=None,
                    action_type=None,
                    action_result=None,
                    kakao_message=None,
                    error=None
                )
                
                # 에이전트 실행
                result = agent_graph.invoke(initial_state)
                
                # 응답 추출
                if result.get("messages"):
                    last_message = result["messages"][-1]
                    if hasattr(last_message, 'content'):
                        response_content = last_message.content
                    else:
                        response_content = str(last_message)
                    
                    # 액션 결과가 있으면 추가
                    if result.get("action_result"):
                        tool_results = result["action_result"].get("tool_results", [])
                        if tool_results:
                            response_content += "\n\n**실행 결과:**\n"
                            for tool_result in tool_results:
                                if isinstance(tool_result, dict):
                                    if tool_result.get("success"):
                                        response_content += f"✅ {tool_result.get('message', '작업 완료')}\n"
                                    else:
                                        response_content += f"❌ {tool_result.get('error', '오류 발생')}\n"
                else:
                    response_content = "죄송합니다. 응답을 생성할 수 없습니다."
                
                # AI 응답 추가
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response_content
                })
                
            except Exception as e:
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"오류가 발생했습니다: {str(e)}"
                })
        
        st.rerun()

with col2:
    st.markdown("### 📋 빠른 명령어")
    
    st.markdown("""
    <div class="card">
        <div class="card-header">회원 관리</div>
        <ul>
            <li>"김철수 회원 검색"</li>
            <li>"신규 회원 등록"</li>
            <li>"회원 상태 변경"</li>
            <li>"회원권 등록"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <div class="card-header">스케줄 관리</div>
        <ul>
            <li>"PT 세션 예약"</li>
            <li>"내일 일정 확인"</li>
            <li>"예약 취소"</li>
            <li>"트레이너 일정 확인"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <div class="card-header">상담 및 안내</div>
        <ul>
            <li>"PT 프로그램 안내"</li>
            <li>"가격 문의"</li>
            <li>"운동 추천"</li>
            <li>"회원권 종류"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <div class="card-header">알림 관리</div>
        <ul>
            <li>"카카오 알림 전송"</li>
            <li>"회원권 만료 알림"</li>
            <li>"PT 세션 리마인더"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)