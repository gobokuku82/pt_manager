"""
PT Shop Management System - 간소화 버전
Streamlit Cloud 테스트용
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="PT Shop Management System",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: bold !important;
        margin: 0 0 0.5rem 0 !important;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.2rem !important;
        margin: 0 !important;
    }
</style>
<div class="main-header">
    <h1>💪 PT Shop Management System</h1>
    <p>성수PT - 사용자 : 김태호</p>
</div>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# 사이드바 메뉴
with st.sidebar:
    st.session_state.current_page = st.selectbox(
        "메뉴 선택",
        ["Dashboard", "회원 관리", "스케줄 관리", "AI 챗봇", "알림 관리", "통계"]
    )

# 메인 콘텐츠
if st.session_state.current_page == "Dashboard":
    st.header("📊 대시보드")
    
    # 통계 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="전체 회원", value="150명")
    
    with col2:
        st.metric(label="활성 회원", value="98명")
    
    with col3:
        st.metric(label="오늘 PT", value="12건")
    
    with col4:
        st.metric(label="신규 회원 (월)", value="8명")
    
    st.divider()
    
    # 최근 활동
    st.subheader("📈 최근 활동")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🆕 최근 등록 회원")
        st.write("🟢 **김철수** - 010-1234-5678")
        st.write("🟢 **이영희** - 010-2345-6789")
        st.write("🟢 **박민수** - 010-3456-7890")
    
    with col2:
        st.markdown("#### ⚠️ 회원권 만료 예정")
        st.write("📅 **김지은** - 3일 남음")
        st.write("📅 **최준호** - 5일 남음")
        st.write("📅 **정미라** - 7일 남음")

elif st.session_state.current_page == "회원 관리":
    st.header("👥 회원 관리")
    
    tab1, tab2, tab3 = st.tabs(["📋 회원 목록", "➕ 회원 등록", "🔍 회원 검색"])
    
    with tab1:
        # 샘플 데이터
        sample_data = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            '이름': ['김철수', '이영희', '박민수', '정미라', '최준호'],
            '전화번호': ['010-1234-5678', '010-2345-6789', '010-3456-7890', '010-4567-8901', '010-5678-9012'],
            '상태': ['활성', '활성', '활성', '일시정지', '활성'],
            '회원권': ['PT30', 'PT20', 'PT10', 'PT30', 'PT20'],
            '잔여 횟수': [15, 8, 3, 20, 12]
        })
        st.dataframe(sample_data, use_container_width=True)
    
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
                    st.success(f"✅ {name}님이 성공적으로 등록되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 이름과 전화번호는 필수 입력 항목입니다.")
    
    with tab3:
        st.subheader("회원 검색")
        search_query = st.text_input("검색어 입력 (이름, 전화번호, 카카오ID)")
        if search_query:
            st.info(f"'{search_query}' 검색 결과가 표시됩니다.")

elif st.session_state.current_page == "AI 챗봇":
    st.header("🤖 AI 상담 챗봇")
    
    # 채팅 기록 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 이전 메시지 표시
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

elif st.session_state.current_page == "스케줄 관리":
    st.header("📅 스케줄 관리")
    st.info("스케줄 관리 기능이 곧 추가됩니다.")

elif st.session_state.current_page == "알림 관리":
    st.header("🔔 알림 관리")
    st.info("알림 관리 기능이 곧 추가됩니다.")

elif st.session_state.current_page == "통계":
    st.header("📈 통계 및 분석")
    st.info("통계 기능이 곧 추가됩니다.")