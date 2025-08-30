"""
사이드바 챗봇 컴포넌트
모든 페이지에서 재사용 가능한 챗봇 UI
"""

import streamlit as st
from datetime import datetime, timedelta

def render_sidebar_chat(db):
    """사이드바에 챗봇 UI 렌더링"""
    
    # AI 어시스턴트 챗봇
    st.markdown("---")
    st.markdown("### 🤖 AI 어시스턴트")
    
    # 채팅 메시지 초기화 (전역 세션 상태 사용)
    if "global_chat_messages" not in st.session_state:
        st.session_state.global_chat_messages = []
    
    # 빠른 질문 버튼들
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📅 오늘 일정", use_container_width=True, key="quick_today"):
            handle_chat_input("오늘 PT 일정 알려줘", db)
    with col2:
        if st.button("👥 회원 현황", use_container_width=True, key="quick_stats"):
            handle_chat_input("전체 회원 통계 보여줘", db)
    
    # 채팅 메시지 표시 (최근 3개만)
    if st.session_state.global_chat_messages:
        chat_container = st.container(height=200)
        with chat_container:
            for msg in st.session_state.global_chat_messages[-6:]:  # 최근 3개 대화쌍
                if msg["role"] == "user":
                    st.markdown(f"**👤 You:** {msg['content']}")
                else:
                    st.markdown(f"**🤖 AI:** {msg['content']}")
    
    # 입력 필드
    user_input = st.text_input(
        "무엇을 도와드릴까요?",
        key="sidebar_chat_input",
        placeholder="예: 오늘 일정, 회원 검색..."
    )
    
    if user_input:
        handle_chat_input(user_input, db)
        st.rerun()
    
    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화", use_container_width=True, key="clear_chat"):
        st.session_state.global_chat_messages = []
        st.rerun()

def handle_chat_input(user_input: str, db):
    """사용자 입력을 처리하고 응답 생성"""
    # 사용자 메시지 추가
    st.session_state.global_chat_messages.append({"role": "user", "content": user_input})
    
    # 응답 생성
    response = generate_simple_response(user_input, db)
    
    # AI 응답 추가
    st.session_state.global_chat_messages.append({"role": "assistant", "content": response})

def generate_simple_response(question: str, db):
    """간단한 규칙 기반 응답 생성"""
    question_lower = question.lower()
    
    if not db:
        return "데이터베이스 연결이 필요합니다."
    
    # 오늘 일정
    if "오늘" in question_lower and ("일정" in question_lower or "pt" in question_lower):
        today_str = datetime.now().strftime("%Y-%m-%d")
        schedules = db.get_schedules_by_date(today_str)
        if schedules:
            response = f"오늘 {len(schedules)}개 PT:\n"
            for s in schedules[:3]:
                response += f"• {s.get('time','')} {s.get('member_name','')}\n"
            return response
        return "오늘은 PT가 없습니다."
    
    # 회원 통계
    elif "회원" in question_lower or "통계" in question_lower:
        stats = db.get_statistics()
        return f"전체: {stats.get('total_members',0)}명\n활성: {stats.get('active_members',0)}명"
    
    # 도움말
    elif "도움" in question_lower or "help" in question_lower:
        return "💡 사용 가능한 명령:\n• 오늘 일정\n• 회원 현황\n• 내일 일정"
    
    # 내일 일정
    elif "내일" in question_lower:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        schedules = db.get_schedules_by_date(tomorrow)
        if schedules:
            return f"내일 {len(schedules)}개 PT 예정"
        return "내일은 PT가 없습니다."
    
    # 회원 검색
    elif "검색" in question_lower or "찾" in question_lower:
        return "회원 검색은 '👥 회원관리' 페이지에서 가능합니다."
    
    # 예약/스케줄
    elif "예약" in question_lower or "스케줄" in question_lower:
        return "PT 예약은 '📅 스케줄' 페이지에서 가능합니다."
    
    return "무엇을 도와드릴까요?\n'도움말'을 입력해보세요."