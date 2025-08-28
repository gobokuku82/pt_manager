"""
Streamlit 메인 실행 파일
루트 디렉토리에서 실행됩니다.
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

# CSS 로드
def load_css():
    # 먼저 파일에서 로드 시도
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styles', 'style.css')
    try:
        with open(css_path, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            return
    except FileNotFoundError:
        pass
    
    # 파일이 없으면 인라인 CSS 사용
    st.markdown("""
    <style>
    /* PT Shop Management System Custom CSS */
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .stat-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .card-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-active {
        background: #d4edda;
        color: #155724;
    }
    
    .status-inactive {
        background: #f8d7da;
        color: #721c24;
    }
    
    .status-paused {
        background: #fff3cd;
        color: #856404;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터베이스 초기화
@st.cache_resource
def initialize_database():
    init_database()
    return True

# 초기화
initialize_database()
load_css()

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# 헤더
st.markdown("""
<div class="header-container">
    <div class="header-title">💪 PT Shop Management System</div>
    <div class="header-subtitle">성수PT - 사용자 : 김태호 </div>
</div>
""", unsafe_allow_html=True)

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
    # 대시보드
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
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">전체 회원</div>
        </div>
        """.format(total_members), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">활성 회원</div>
        </div>
        """.format(active_members), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">오늘 PT</div>
        </div>
        """.format(today_sessions), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">신규 회원 (월)</div>
        </div>
        """.format(new_members), unsafe_allow_html=True)
    
    # 최근 활동
    st.markdown("### 📊 최근 활동")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card"><div class="card-header">🆕 최근 등록 회원</div>', unsafe_allow_html=True)
        with MemberManager() as manager:
            recent_members = manager.get_all_members()[:5]
            if recent_members:
                for member in recent_members:
                    status_class = f"status-{member.membership_status}"
                    st.markdown(f"""
                    <div style="padding: 0.5rem; border-bottom: 1px solid #eee;">
                        <strong>{member.name}</strong> 
                        <span class="status-badge {status_class}">{member.membership_status}</span>
                        <br>
                        <small>{member.phone}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("등록된 회원이 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><div class="card-header">⚠️ 회원권 만료 예정</div>', unsafe_allow_html=True)
        with MemberManager() as manager:
            expiring = manager.get_expiring_memberships(days=7)
            if expiring:
                for item in expiring[:5]:
                    st.markdown(f"""
                    <div style="padding: 0.5rem; border-bottom: 1px solid #eee;">
                        <strong>{item['member'].name}</strong>
                        <br>
                        <small>만료까지 {item['days_until_expiry']}일 남음</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("만료 예정 회원권이 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "회원 관리":
    # 회원 관리 페이지
    st.markdown("### 👥 회원 관리")
    
    tab1, tab2, tab3 = st.tabs(["회원 목록", "회원 등록", "회원 검색"])
    
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
            
            if st.form_submit_button("회원 등록", use_container_width=True):
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
                        st.success(f"{name}님이 성공적으로 등록되었습니다!")
                        st.rerun()
                else:
                    st.error("이름과 전화번호는 필수 입력 항목입니다.")
    
    with tab3:
        search_query = st.text_input("검색어 입력 (이름, 전화번호, 카카오ID)")
        if search_query:
            with MemberManager() as manager:
                results = manager.search_members(search_query)
                if results:
                    for member in results:
                        with st.expander(f"{member.name} - {member.phone}"):
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
    # AI 챗봇 페이지
    st.markdown("### 🤖 AI 상담 챗봇")
    
    # 채팅 기록 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 채팅 인터페이스
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 대화")
        
        # 채팅 히스토리 표시
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**🤖 AI:** {message['content']}")
        
        # 입력 폼
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_area("메시지를 입력하세요", height=100)
            col1_1, col1_2, col1_3 = st.columns([1, 1, 3])
            with col1_1:
                submit_button = st.form_submit_button("전송", use_container_width=True)
            with col1_2:
                if st.form_submit_button("대화 초기화", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
        
        if submit_button and user_input:
            # 사용자 메시지 추가
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # 임시 AI 응답 (실제 구현시 LangGraph 사용)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': "AI 챗봇 기능이 곧 활성화됩니다."
            })
            
            st.rerun()
    
    with col2:
        st.markdown("### 📋 빠른 명령어")
        st.info("""
        - "김철수 회원 검색"
        - "신규 회원 등록"
        - "PT 세션 예약"
        - "회원권 등록"
        """)

elif st.session_state.current_page == "스케줄 관리":
    st.markdown("### 📅 스케줄 관리")
    st.info("스케줄 관리 기능이 곧 추가됩니다.")

elif st.session_state.current_page == "알림 관리":
    st.markdown("### 🔔 알림 관리")
    st.info("알림 관리 기능이 곧 추가됩니다.")

elif st.session_state.current_page == "통계":
    st.markdown("### 📈 통계 및 분석")
    st.info("통계 기능이 곧 추가됩니다.")