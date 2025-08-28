"""
PT Shop Management System - Streamlit Native Components Version
Streamlit 클라우드에 최적화된 안정적인 버전
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_database, get_db, Member, Membership, PTSession
from utils.member_manager import MemberManager

# 페이지 설정
st.set_page_config(
    page_title="PT Shop Management System",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터베이스 초기화
@st.cache_resource
def initialize_database():
    init_database()
    return True

# 초기화
initialize_database()

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# 헤더 - Streamlit native 컴포넌트 사용
st.title("💪 PT Shop Management System")
st.subheader("성수PT - 사용자 : 김태호")
st.divider()

# 사이드바 메뉴
with st.sidebar:
    selected = option_menu(
        menu_title="메뉴",
        options=["Dashboard", "회원 관리", "스케줄 관리", "AI 챗봇", "알림 관리", "통계"],
        icons=["house", "people", "calendar", "robot", "bell", "graph-up"],
        menu_icon="cast",
        default_index=0,
    )
    st.session_state.current_page = selected

# 메인 콘텐츠
if st.session_state.current_page == "Dashboard":
    st.header("📊 대시보드")
    
    # 통계 메트릭 - Streamlit native metric 사용
    col1, col2, col3, col4 = st.columns(4)
    
    with MemberManager() as manager:
        # 전체 회원 수
        total_members = len(manager.get_all_members())
        # 활성 회원 수
        active_members = len(manager.get_all_members(status="active"))
        # 오늘 예정 세션
        today = datetime.now().date()
        db = next(get_db())
        today_sessions = db.query(PTSession).filter(
            PTSession.session_date >= datetime.combine(today, datetime.min.time()),
            PTSession.session_date < datetime.combine(today + timedelta(days=1), datetime.min.time()),
            PTSession.status == "scheduled"
        ).count()
        db.close()
        # 이번 달 신규 회원
        month_start = datetime.now().replace(day=1)
        db = next(get_db())
        new_members = db.query(Member).filter(
            Member.registration_date >= month_start
        ).count()
        db.close()
    
    with col1:
        st.metric(label="전체 회원", value=f"{total_members}명")
    
    with col2:
        st.metric(label="활성 회원", value=f"{active_members}명")
    
    with col3:
        st.metric(label="오늘 PT", value=f"{today_sessions}건")
    
    with col4:
        st.metric(label="신규 회원 (월)", value=f"{new_members}명")
    
    st.divider()
    
    # 최근 활동
    st.subheader("📈 최근 활동")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🆕 최근 등록 회원")
        with MemberManager() as manager:
            recent_members = manager.get_all_members()[:5]
            if recent_members:
                for member in recent_members:
                    status_icon = "🟢" if member.membership_status == "active" else "🔴"
                    st.write(f"{status_icon} **{member.name}** - {member.phone}")
            else:
                st.info("등록된 회원이 없습니다.")
    
    with col2:
        st.markdown("#### ⚠️ 회원권 만료 예정")
        with MemberManager() as manager:
            expiring = manager.get_expiring_memberships(days=7)
            if expiring:
                for item in expiring[:5]:
                    st.write(f"📅 **{item['member'].name}** - {item['days_until_expiry']}일 남음")
            else:
                st.info("만료 예정 회원권이 없습니다.")

elif st.session_state.current_page == "회원 관리":
    st.header("👥 회원 관리")
    
    tab1, tab2, tab3 = st.tabs(["📋 회원 목록", "➕ 회원 등록", "🔍 회원 검색"])
    
    with tab1:
        with MemberManager() as manager:
            members = manager.get_all_members()
            if members:
                member_data = []
                for member in members:
                    membership = manager.get_member_membership(member.id)
                    member_data.append({
                        "ID": member.id,
                        "이름": member.name,
                        "전화번호": member.phone,
                        "상태": member.membership_status,
                        "회원권": membership.membership_type if membership else "-",
                        "잔여 횟수": membership.remaining_sessions if membership else 0,
                        "등록일": member.registration_date.strftime("%Y-%m-%d") if member.registration_date else "-"
                    })
                df = pd.DataFrame(member_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("등록된 회원이 없습니다.")
    
    with tab2:
        st.subheader("신규 회원 등록")
        with st.form("register_member"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("이름*")
                phone = st.text_input("전화번호*")
                email = st.text_input("이메일")
                birth_date = st.date_input("생년월일")
            with col2:
                kakao_id = st.text_input("카카오 ID")
                gender = st.selectbox("성별", ["남성", "여성", "기타"])
                address = st.text_area("주소")
                notes = st.text_area("메모")
            
            if st.form_submit_button("회원 등록", use_container_width=True, type="primary"):
                if name and phone:
                    with MemberManager() as manager:
                        member_data = {
                            "name": name,
                            "phone": phone,
                            "email": email,
                            "birth_date": birth_date.strftime("%Y-%m-%d"),
                            "kakao_id": kakao_id,
                            "gender": gender,
                            "address": address,
                            "notes": notes
                        }
                        manager.create_member(member_data)
                        st.success(f"✅ {name}님이 성공적으로 등록되었습니다!")
                        st.balloons()
                        st.rerun()
                else:
                    st.error("❌ 이름과 전화번호는 필수 입력 항목입니다.")
    
    with tab3:
        st.subheader("회원 검색")
        search_query = st.text_input("검색어 입력 (이름, 전화번호, 카카오ID)")
        if search_query:
            with MemberManager() as manager:
                results = manager.search_members(search_query)
                if results:
                    for member in results:
                        with st.expander(f"👤 {member.name} - {member.phone}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**ID:** {member.id}")
                                st.write(f"**이름:** {member.name}")
                                st.write(f"**전화번호:** {member.phone}")
                                st.write(f"**상태:** {member.membership_status}")
                            with col2:
                                st.write(f"**카카오ID:** {member.kakao_id or '-'}")
                                st.write(f"**이메일:** {member.email or '-'}")
                                st.write(f"**성별:** {member.gender or '-'}")
                                st.write(f"**등록일:** {member.registration_date.strftime('%Y-%m-%d') if member.registration_date else '-'}")
                else:
                    st.info("검색 결과가 없습니다.")

elif st.session_state.current_page == "AI 챗봇":
    st.header("🤖 AI 상담 챗봇")
    
    # 채팅 기록 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    # 이전 메시지 표시
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # 채팅 입력
    if prompt := st.chat_input("메시지를 입력하세요"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # AI 응답 (임시)
        response = "AI 챗봇 기능이 곧 활성화됩니다. OpenAI API 키를 설정해주세요."
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
    
    # 사이드바에 빠른 명령어
    with st.sidebar:
        st.markdown("### 📋 빠른 명령어")
        st.code("""
• 김철수 회원 검색
• 신규 회원 등록
• PT 세션 예약
• 회원권 등록
        """)

elif st.session_state.current_page == "스케줄 관리":
    st.header("📅 스케줄 관리")
    st.info("스케줄 관리 기능이 곧 추가됩니다.")

elif st.session_state.current_page == "알림 관리":
    st.header("🔔 알림 관리")
    st.info("알림 관리 기능이 곧 추가됩니다.")

elif st.session_state.current_page == "통계":
    st.header("📈 통계 및 분석")
    st.info("통계 기능이 곧 추가됩니다.")