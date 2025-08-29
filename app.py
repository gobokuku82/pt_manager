"""
PT Manager - 메인 애플리케이션
플로팅 챗봇이 포함된 대시보드
"""

import streamlit as st
from streamlit_float import float_init
import pandas as pd
from datetime import datetime, timedelta
import json
from database.gsheets import GoogleSheetsDB

# 페이지 설정
st.set_page_config(
    page_title="PT Manager",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Float 초기화 (플로팅 요소 지원)
float_init()

# Google Sheets 데이터베이스 초기화
@st.cache_resource
def init_database():
    """Google Sheets 데이터베이스 초기화"""
    try:
        return GoogleSheetsDB()
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {str(e)}")
        return None

db = init_database()

# CSS 스타일
def load_custom_css():
    """커스텀 CSS 로드"""
    st.markdown("""
    <style>
    /* 메인 헤더 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* 통계 카드 */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* 플로팅 챗봇 버튼 */
    .chatbot-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 1000;
        transition: transform 0.3s;
    }
    
    .chatbot-button:hover {
        transform: scale(1.1);
    }
    
    /* 챗봇 창 */
    .chatbot-window {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 380px;
        height: 600px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        z-index: 999;
        display: flex;
        flex-direction: column;
    }
    
    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 0 0;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* 정보 카드 */
    .info-card {
        background: #f9fafb;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    .info-card h4 {
        color: #374151;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    
    .info-card p {
        color: #6b7280;
        margin: 0;
        font-size: 0.95rem;
    }
    
    /* 버튼 스타일 */
    .custom-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    
    .custom-button:hover {
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'show_chatbot' not in st.session_state:
    st.session_state.show_chatbot = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

def toggle_chatbot():
    """챗봇 창 토글"""
    st.session_state.show_chatbot = not st.session_state.show_chatbot

# CSS 로드
load_custom_css()

# 헤더
st.markdown("""
<div class="main-header">
    <h1>🏋️ PT Manager</h1>
    <p>스마트한 PT샵 관리 시스템</p>
</div>
""", unsafe_allow_html=True)

# 메인 대시보드
if db:
    # 실시간 통계 가져오기
    stats = db.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('total_members', 0)}</div>
            <div class="stat-label">전체 회원</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('active_members', 0)}</div>
            <div class="stat-label">활성 회원</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('today_sessions', 0)}</div>
            <div class="stat-label">오늘 PT</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('pending_signatures', 0)}</div>
            <div class="stat-label">대기중 서명</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.error("데이터베이스 연결이 필요합니다")

# 오늘의 일정
st.markdown("### 📅 오늘의 일정")

if db:
    # 오늘 날짜의 스케줄 가져오기
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_schedules = db.get_schedules_by_date(today_str)
    
    if today_schedules:
        # 스케줄 데이터를 DataFrame으로 변환
        schedule_data = []
        for schedule in today_schedules:
            # 현재 시간과 비교하여 상태 결정
            current_time = datetime.now().strftime("%H:%M")
            if schedule.time < current_time:
                status = "완료"
            elif schedule.time <= (datetime.now() + timedelta(hours=1)).strftime("%H:%M"):
                status = "진행중"
            else:
                status = "예정"
            
            schedule_data.append({
                "시간": schedule.time,
                "회원명": schedule.member_name,
                "PT종류": schedule.pt_type,
                "트레이너": schedule.trainer_name,
                "상태": status
            })
        
        df_schedule = pd.DataFrame(schedule_data)
        if not df_schedule.empty:
            st.dataframe(df_schedule, use_container_width=True, hide_index=True)
        else:
            st.info("오늘 예정된 PT 세션이 없습니다")
    else:
        st.info("오늘 예정된 PT 세션이 없습니다")
else:
    st.error("스케줄 데이터를 불러올 수 없습니다")

# 빠른 작업
st.markdown("### ⚡ 빠른 작업")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
        <h4>👤 회원 등록</h4>
        <p>새로운 회원을 등록하고 회원권을 설정합니다</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("회원 등록 →", use_container_width=True):
        st.switch_page("pages/1_👥_회원관리.py")

with col2:
    st.markdown("""
    <div class="info-card">
        <h4>📝 계약서 생성</h4>
        <p>모바일 서명을 위한 계약서를 생성합니다</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("계약서 생성 →", use_container_width=True):
        st.switch_page("pages/3_📝_계약서.py")

with col3:
    st.markdown("""
    <div class="info-card">
        <h4>📅 PT 예약</h4>
        <p>PT 세션을 예약하고 스케줄을 관리합니다</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("예약 관리 →", use_container_width=True):
        st.switch_page("pages/2_📅_스케줄.py")

# 알림 섹션
st.markdown("### 🔔 알림")

if db:
    col1, col2 = st.columns(2)
    
    # 실제 데이터 기반 알림 생성
    with col1:
        # 만료 예정 회원권 확인
        members = db.get_all_members()
        expiring_soon = []
        for member in members:
            if hasattr(member, 'membership_end_date'):
                end_date = datetime.strptime(member.membership_end_date, "%Y-%m-%d")
                days_left = (end_date - datetime.now()).days
                if 0 < days_left <= 7:
                    expiring_soon.append((member.name, days_left))
        
        if expiring_soon:
            for name, days in expiring_soon[:2]:  # 최대 2개만 표시
                st.info(f"💡 {name} 회원의 회원권이 {days}일 후 만료됩니다")
        
        # 내일 PT 세션 확인
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_schedules = db.get_schedules_by_date(tomorrow)
        if tomorrow_schedules:
            morning_sessions = [s for s in tomorrow_schedules if s.time < "12:00"]
            if morning_sessions:
                st.warning(f"⚠️ 내일 오전 PT 세션 예약이 {len(morning_sessions)}건 있습니다")
    
    with col2:
        # 최근 서명 완료 계약서
        recent_contracts = db.get_recent_contracts(limit=5)
        signed_contracts = [c for c in recent_contracts if c.status == "signed"]
        if signed_contracts:
            st.success(f"✅ {signed_contracts[0].member_name} 회원이 계약서에 서명했습니다")
        
        # 오늘 리마인더 전송 (예시)
        if today_schedules:
            st.info(f"📱 오늘 {len(today_schedules)}명의 회원에게 PT 리마인더를 전송했습니다")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 데이터베이스 연결 후 알림이 표시됩니다")
    with col2:
        st.info("📱 데이터베이스 연결 후 알림이 표시됩니다")

# 플로팅 챗봇 버튼
chatbot_html = """
<div class="chatbot-button" onclick="parent.window.postMessage('toggle_chatbot', '*')">
    <svg width="30" height="30" viewBox="0 0 24 24" fill="white">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
    </svg>
</div>
"""

# 챗봇 창 (조건부 렌더링)
if st.session_state.show_chatbot:
    with st.container():
        float_html = """
        <div class="chatbot-window">
            <div class="chatbot-header">
                <span>🤖 AI 어시스턴트</span>
                <span style="cursor: pointer;" onclick="parent.window.postMessage('close_chatbot', '*')">✖</span>
            </div>
            <div style="flex: 1; padding: 1rem; overflow-y: auto;">
                <p style="color: #6b7280;">무엇을 도와드릴까요?</p>
            </div>
            <div style="padding: 1rem; border-top: 1px solid #e5e7eb;">
                <input type="text" placeholder="메시지를 입력하세요..." 
                       style="width: 100%; padding: 0.5rem; border: 1px solid #e5e7eb; border-radius: 8px;">
            </div>
        </div>
        """
        st.components.v1.html(chatbot_html + float_html, height=0)
else:
    st.components.v1.html(chatbot_html, height=0)

# JavaScript 이벤트 핸들러
st.markdown("""
<script>
window.addEventListener('message', function(e) {
    if (e.data === 'toggle_chatbot' || e.data === 'close_chatbot') {
        // Streamlit의 rerun을 트리거하기 위한 방법
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: true}, '*');
    }
});
</script>
""", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.markdown("### 🛠️ 관리 도구")
    
    st.markdown("#### 데이터베이스")
    if st.button("🔄 동기화", use_container_width=True):
        if db:
            # 캐시 클리어하여 새로운 데이터 로드
            st.cache_resource.clear()
            st.success("Google Sheets와 동기화되었습니다")
            st.rerun()
        else:
            st.error("데이터베이스 연결이 필요합니다")
    
    st.markdown("#### 시스템")
    if st.button("⚙️ 설정", use_container_width=True):
        st.info("설정 페이지는 준비중입니다")
    
    st.markdown("---")
    st.markdown("#### 도움말")
    st.markdown("""
    - [📚 사용 가이드](https://github.com)
    - [🐛 버그 신고](https://github.com)
    - [💬 문의하기](mailto:support@example.com)
    """)