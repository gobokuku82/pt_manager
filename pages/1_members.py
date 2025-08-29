"""
회원 관리 페이지
회원 등록, 조회, 수정, 삭제 기능
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from database.gsheets import GoogleSheetsDB
from database.models import Member

# 페이지 설정
st.set_page_config(
    page_title="회원 관리 - PT Manager",
    page_icon="👥",
    layout="wide"
)

# 데이터베이스 연결
@st.cache_resource
def get_db():
    return GoogleSheetsDB()

db = get_db()

# 헤더
st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: white;
}
.member-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    border: 1px solid #e5e7eb;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.status-active {
    background: #10b981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.875rem;
}
.status-inactive {
    background: #ef4444;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.875rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h1 style="margin: 0; color: white;">회원 관리</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">회원 정보를 관리하고 회원권을 설정합니다</p>
</div>
""", unsafe_allow_html=True)

# 탭 메뉴
tab1, tab2, tab3, tab4 = st.tabs(["회원 목록", "회원 등록", "회원 검색", "통계"])

# === 회원 목록 탭 ===
with tab1:
    st.markdown("### 전체 회원 목록")
    
    # 필터링 옵션
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        status_filter = st.selectbox("상태", ["전체", "활성", "비활성", "삭제됨"])
    with col2:
        sort_by = st.selectbox("정렬", ["최근 등록순", "이름순", "회원권 만료순"])
    
    # 회원 목록 조회
    if status_filter == "전체":
        members = db.get_all_members()
    else:
        status_map = {"활성": "active", "비활성": "inactive", "삭제됨": "deleted"}
        members = db.get_all_members(status=status_map.get(status_filter))
    
    if members:
        # 데이터프레임으로 표시
        df_members = pd.DataFrame(members)
        
        # 필요한 컬럼만 선택
        display_columns = ["name", "phone", "email", "membership_type", 
                          "remaining_sessions", "status", "created_at"]
        available_columns = [col for col in display_columns if col in df_members.columns]
        
        if available_columns:
            df_display = df_members[available_columns].copy()
            
            # 컬럼명 한글로 변경
            column_names = {
                "name": "이름",
                "phone": "전화번호",
                "email": "이메일",
                "membership_type": "회원권",
                "remaining_sessions": "잔여횟수",
                "status": "상태",
                "created_at": "등록일"
            }
            df_display.rename(columns=column_names, inplace=True)
            
            # 데이터테이블 표시
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "상태": st.column_config.TextColumn(
                        "상태",
                        help="회원 상태"
                    ),
                    "잔여횟수": st.column_config.NumberColumn(
                        "잔여횟수",
                        format="%d회"
                    )
                }
            )
            
            # 회원 상세 보기
            st.markdown("### 회원 상세 정보")
            selected_member = st.selectbox(
                "회원 선택",
                options=members,
                format_func=lambda x: f"{x.get('name', '')} - {x.get('phone', '')}"
            )
            
            if selected_member:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="member-card">
                        <h4>{selected_member.get('name', '')}</h4>
                        <p>전화: {selected_member.get('phone', '')}</p>
                        <p>이메일: {selected_member.get('email', '-')}</p>
                        <p>생일: {selected_member.get('birth_date', '-')}</p>
                        <p>주소: {selected_member.get('address', '-')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="member-card">
                        <h4>회원권 정보</h4>
                        <p>종류: {selected_member.get('membership_type', '-')}</p>
                        <p>잔여: {selected_member.get('remaining_sessions', 0)}회</p>
                        <p>상태: <span class="status-{selected_member.get('status', 'active')}">{selected_member.get('status', 'active')}</span></p>
                        <p>등록일: {selected_member.get('created_at', '-')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 회원 수정/삭제 버튼
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button("수정", key=f"edit_{selected_member.get('id')}"):
                        st.session_state.edit_member = selected_member
                        st.rerun()
                with col2:
                    if st.button("삭제", key=f"delete_{selected_member.get('id')}"):
                        if db.delete_member(selected_member.get('id')):
                            st.success("회원이 삭제되었습니다")
                            st.rerun()
    else:
        st.info("등록된 회원이 없습니다. 회원 등록 탭에서 새 회원을 추가해주세요.")

# === 회원 등록 탭 ===
with tab2:
    st.markdown("### 새 회원 등록")
    
    with st.form("register_member_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("이름 *", placeholder="홍길동")
            phone = st.text_input("전화번호 *", placeholder="010-1234-5678")
            email = st.text_input("이메일", placeholder="example@email.com")
            birth_date = st.date_input("생년월일")
        
        with col2:
            gender = st.selectbox("성별", ["남성", "여성", "기타"])
            membership_type = st.selectbox(
                "회원권 종류",
                ["PT10", "PT20", "PT30", "월간", "연간"]
            )
            sessions = st.number_input("세션 횟수", min_value=0, value=10)
            address = st.text_area("주소", placeholder="서울시 강남구...")
        
        notes = st.text_area("메모", placeholder="특이사항이나 메모를 입력하세요")
        
        submitted = st.form_submit_button("회원 등록", use_container_width=True)
        
        if submitted:
            if name and phone:
                try:
                    # 회원 데이터 생성
                    member_data = {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "birth_date": birth_date.strftime("%Y-%m-%d"),
                        "gender": gender,
                        "address": address,
                        "membership_type": membership_type,
                        "remaining_sessions": sessions
                    }
                    
                    # 데이터베이스에 저장
                    new_member = db.create_member(member_data)
                    st.success(f"{name}님이 성공적으로 등록되었습니다!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"회원 등록 중 오류가 발생했습니다: {str(e)}")
            else:
                st.error("이름과 전화번호는 필수 입력 항목입니다.")

# === 회원 검색 탭 ===
with tab3:
    st.markdown("### 회원 검색")
    
    search_query = st.text_input(
        "검색어 입력",
        placeholder="이름, 전화번호, 이메일로 검색..."
    )
    
    if search_query:
        results = db.search_members(search_query)
        
        if results:
            st.success(f"{len(results)}명의 회원을 찾았습니다")
            
            for member in results:
                with st.expander(f"{member.get('name')} - {member.get('phone')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**이름:** {member.get('name')}")
                        st.write(f"**전화번호:** {member.get('phone')}")
                        st.write(f"**이메일:** {member.get('email', '-')}")
                        st.write(f"**생년월일:** {member.get('birth_date', '-')}")
                    
                    with col2:
                        st.write(f"**회원권:** {member.get('membership_type', '-')}")
                        st.write(f"**잔여횟수:** {member.get('remaining_sessions', 0)}회")
                        st.write(f"**상태:** {member.get('status', 'active')}")
                        st.write(f"**등록일:** {member.get('created_at', '-')}")
        else:
            st.info("검색 결과가 없습니다")

# === 통계 탭 ===
with tab4:
    st.markdown("### 회원 통계")
    
    stats = db.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("전체 회원", f"{stats.get('total_members', 0)}명")
    
    with col2:
        st.metric("활성 회원", f"{stats.get('active_members', 0)}명")
    
    with col3:
        inactive = stats.get('total_members', 0) - stats.get('active_members', 0)
        st.metric("비활성 회원", f"{inactive}명")
    
    with col4:
        if stats.get('total_members', 0) > 0:
            active_rate = (stats.get('active_members', 0) / stats.get('total_members', 1)) * 100
            st.metric("활성률", f"{active_rate:.1f}%")
        else:
            st.metric("활성률", "0%")
    
    # 회원권 종류별 통계
    st.markdown("### 회원권 종류별 분포")
    
    members = db.get_all_members()
    if members:
        membership_counts = {}
        for member in members:
            mtype = member.get('membership_type', '미지정')
            membership_counts[mtype] = membership_counts.get(mtype, 0) + 1
        
        df_stats = pd.DataFrame(
            list(membership_counts.items()),
            columns=['회원권 종류', '회원 수']
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df_stats.set_index('회원권 종류'))
        
        with col2:
            st.dataframe(df_stats, use_container_width=True, hide_index=True)