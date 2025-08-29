"""
스케줄 관리 페이지
PT 세션 예약 및 일정 관리
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from database.gsheets import GoogleSheetsDB

# 페이지 설정
st.set_page_config(
    page_title="스케줄 관리 - PT Manager",
    page_icon="📅",
    layout="wide"
)

# 데이터베이스 연결
@st.cache_resource
def get_db():
    return GoogleSheetsDB()

db = get_db()

# 스타일
st.markdown("""
<style>
.schedule-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: white;
}
.time-slot {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.5rem;
}
.time-slot-booked {
    background: #fef2f2;
    border: 1px solid #fca5a5;
}
.time-slot-available {
    background: #f0fdf4;
    border: 1px solid #86efac;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="schedule-header">
    <h1 style="margin: 0; color: white;">스케줄 관리</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">PT 세션을 예약하고 일정을 관리합니다</p>
</div>
""", unsafe_allow_html=True)

# 탭 메뉴
tab1, tab2, tab3, tab4 = st.tabs(["오늘 일정", "예약 등록", "주간 일정", "예약 관리"])

# === 오늘 일정 탭 ===
with tab1:
    st.markdown("### 오늘의 PT 일정")
    
    today = datetime.now().strftime("%Y-%m-%d")
    schedules_today = db.get_schedules_by_date(today)
    
    if schedules_today:
        # 시간순 정렬
        schedules_today.sort(key=lambda x: x.get('time', ''))
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            for schedule in schedules_today:
                status_color = {
                    "scheduled": "blue",
                    "completed": "green",
                    "cancelled": "red",
                    "no-show": "orange"
                }.get(schedule.get('status', 'scheduled'), 'gray')
                
                st.markdown(f"""
                <div class="time-slot">
                    <h4>{schedule.get('time', '')} - {schedule.get('member_name', '')}</h4>
                    <p>트레이너: {schedule.get('trainer', '')}</p>
                    <p>종류: {schedule.get('type', 'PT')}</p>
                    <p>시간: {schedule.get('duration', 60)}분</p>
                    <p style="color: {status_color};">상태: {schedule.get('status', 'scheduled')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.metric("총 예약", f"{len(schedules_today)}건")
            
            completed = len([s for s in schedules_today if s.get('status') == 'completed'])
            st.metric("완료", f"{completed}건")
            
            remaining = len([s for s in schedules_today if s.get('status') == 'scheduled'])
            st.metric("예정", f"{remaining}건")
    else:
        st.info("오늘 예약된 PT 세션이 없습니다.")

# === 예약 등록 탭 ===
with tab2:
    st.markdown("### 새 PT 예약")
    
    with st.form("schedule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # 회원 선택
            members = db.get_all_members(status="active")
            if members:
                member_options = {f"{m['name']} ({m['phone']})": m for m in members}
                selected_member_key = st.selectbox("회원 선택", options=list(member_options.keys()))
                selected_member = member_options[selected_member_key]
            else:
                st.warning("등록된 활성 회원이 없습니다.")
                selected_member = None
            
            # 날짜 선택
            schedule_date = st.date_input("예약 날짜", min_value=date.today())
            
            # 시간 선택
            time_slots = [f"{h:02d}:{m:02d}" for h in range(9, 21) for m in [0, 30]]
            schedule_time = st.selectbox("예약 시간", options=time_slots)
        
        with col2:
            # 트레이너 선택
            trainers = ["김코치", "이코치", "박코치", "최코치"]
            trainer = st.selectbox("트레이너", options=trainers)
            
            # PT 종류
            pt_type = st.selectbox("PT 종류", ["PT", "필라테스", "재활", "그룹"])
            
            # 시간
            duration = st.number_input("세션 시간(분)", min_value=30, max_value=120, value=60, step=30)
        
        # 메모
        notes = st.text_area("메모", placeholder="특이사항을 입력하세요...")
        
        submitted = st.form_submit_button("예약 등록", use_container_width=True)
        
        if submitted and selected_member:
            try:
                schedule_data = {
                    "member_id": selected_member['id'],
                    "member_name": selected_member['name'],
                    "date": schedule_date.strftime("%Y-%m-%d"),
                    "time": schedule_time,
                    "trainer": trainer,
                    "type": pt_type,
                    "duration": duration,
                    "notes": notes
                }
                
                new_schedule = db.create_schedule(schedule_data)
                st.success(f"{selected_member['name']}님의 PT가 {schedule_date} {schedule_time}에 예약되었습니다!")
                
            except Exception as e:
                st.error(f"예약 등록 중 오류가 발생했습니다: {str(e)}")

# === 주간 일정 탭 ===
with tab3:
    st.markdown("### 주간 일정표")
    
    # 이번 주 날짜 계산
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    week_names = ["월", "화", "수", "목", "금", "토", "일"]
    
    # 주간 일정 데이터 수집
    weekly_schedule = {}
    for date_str in week_dates:
        weekly_schedule[date_str] = db.get_schedules_by_date(date_str)
    
    # 컬럼으로 요일 표시
    cols = st.columns(7)
    for idx, (col, date_str, day_name) in enumerate(zip(cols, week_dates, week_names)):
        with col:
            is_today = date_str == today.strftime("%Y-%m-%d")
            
            if is_today:
                st.markdown(f"**{day_name} (오늘)**")
            else:
                st.markdown(f"**{day_name}**")
            
            st.caption(date_str[5:])  # MM-DD 형식
            
            schedules = weekly_schedule[date_str]
            if schedules:
                for schedule in schedules[:3]:  # 최대 3개만 표시
                    st.info(f"{schedule.get('time', '')[:5]}\n{schedule.get('member_name', '')[:8]}")
                
                if len(schedules) > 3:
                    st.caption(f"외 {len(schedules)-3}건")
            else:
                st.caption("예약 없음")

# === 예약 관리 탭 ===
with tab4:
    st.markdown("### 예약 조회 및 관리")
    
    # 검색 필터
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_member = st.text_input("회원 이름", placeholder="검색할 회원 이름...")
    
    with col2:
        search_date = st.date_input("날짜 선택", value=None)
    
    with col3:
        search_status = st.selectbox("상태", ["전체", "예정", "완료", "취소", "노쇼"])
    
    # 검색 실행
    if st.button("검색", use_container_width=True):
        all_schedules = []
        
        if search_member:
            # 회원 이름으로 검색
            members = db.search_members(search_member)
            for member in members:
                member_schedules = db.get_member_schedules(member['id'])
                all_schedules.extend(member_schedules)
        elif search_date:
            # 날짜로 검색
            all_schedules = db.get_schedules_by_date(search_date.strftime("%Y-%m-%d"))
        else:
            # 최근 일정 조회
            for i in range(7):
                date_str = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                all_schedules.extend(db.get_schedules_by_date(date_str))
        
        # 상태 필터링
        if search_status != "전체":
            status_map = {
                "예정": "scheduled",
                "완료": "completed",
                "취소": "cancelled",
                "노쇼": "no-show"
            }
            all_schedules = [s for s in all_schedules if s.get('status') == status_map.get(search_status)]
        
        # 결과 표시
        if all_schedules:
            df_schedules = pd.DataFrame(all_schedules)
            
            # 컬럼 선택 및 이름 변경
            display_columns = ['date', 'time', 'member_name', 'trainer', 'type', 'duration', 'status']
            available_columns = [col for col in display_columns if col in df_schedules.columns]
            
            if available_columns:
                df_display = df_schedules[available_columns].copy()
                
                column_names = {
                    'date': '날짜',
                    'time': '시간',
                    'member_name': '회원',
                    'trainer': '트레이너',
                    'type': '종류',
                    'duration': '시간(분)',
                    'status': '상태'
                }
                df_display.rename(columns=column_names, inplace=True)
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # 예약 수정/취소
                st.markdown("### 예약 변경")
                
                schedule_to_modify = st.selectbox(
                    "변경할 예약 선택",
                    options=all_schedules,
                    format_func=lambda x: f"{x['date']} {x['time']} - {x['member_name']}"
                )
                
                if schedule_to_modify:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_status = st.selectbox(
                            "상태 변경",
                            ["scheduled", "completed", "cancelled", "no-show"],
                            index=["scheduled", "completed", "cancelled", "no-show"].index(
                                schedule_to_modify.get('status', 'scheduled')
                            )
                        )
                        
                        if st.button("상태 변경", use_container_width=True):
                            if db.update_schedule(schedule_to_modify['id'], {'status': new_status}):
                                st.success("예약 상태가 변경되었습니다")
                                st.rerun()
                    
                    with col2:
                        if st.button("예약 취소", use_container_width=True, type="secondary"):
                            if db.cancel_schedule(schedule_to_modify['id']):
                                st.success("예약이 취소되었습니다")
                                st.rerun()
        else:
            st.info("검색 결과가 없습니다")