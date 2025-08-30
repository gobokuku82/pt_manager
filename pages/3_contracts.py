"""
계약서 관리 페이지
모바일 서명을 위한 계약서 생성 및 관리
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import qrcode
from io import BytesIO
import base64
from database.gsheets import GoogleSheetsDB
from utils.sidebar_chat import render_sidebar_chat

# 페이지 설정
st.set_page_config(
    page_title="계약서 관리 - PT Manager",
    page_icon="📝",
    layout="wide"
)

# 데이터베이스 연결
@st.cache_resource
def get_db():
    return GoogleSheetsDB()

db = get_db()

# 사이드바에 챗봇 추가
with st.sidebar:
    render_sidebar_chat(db)

# 스타일
st.markdown("""
<style>
.contract-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: white;
}
.contract-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    border: 1px solid #e5e7eb;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.status-pending {
    color: #f59e0b;
    background: #fef3c7;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.875rem;
}
.status-signed {
    color: #10b981;
    background: #d1fae5;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.875rem;
}
.link-box {
    background: #f3f4f6;
    padding: 1rem;
    border-radius: 8px;
    border: 1px dashed #9ca3af;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="contract-header">
    <h1 style="margin: 0; color: white;">계약서 관리</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">전자 계약서를 생성하고 모바일 서명을 받습니다</p>
</div>
""", unsafe_allow_html=True)

# 계약서 템플릿
CONTRACT_TEMPLATES = {
    "회원권 계약서": """
[PT 회원권 이용 계약서]

1. 계약 내용
- 회원명: {member_name}
- 연락처: {phone}
- 회원권 종류: {membership_type}
- 이용 기간: {start_date} ~ {end_date}
- 총 횟수: {total_sessions}회
- 결제 금액: {price}원

2. 이용 약관
- PT 예약은 최소 1일 전에 해주시기 바랍니다.
- 당일 취소 시 1회 차감됩니다.
- 회원권은 타인에게 양도할 수 없습니다.
- 유효기간 내 미사용 횟수는 소멸됩니다.

3. 환불 규정
- 계약일로부터 7일 이내: 전액 환불
- 이용 횟수 50% 미만: 잔여 횟수 환불
- 이용 횟수 50% 이상: 환불 불가

본인은 위 내용을 충분히 이해하였으며, 이에 동의합니다.

날짜: {date}
회원 서명: 
""",
    
    "개인정보 동의서": """
[개인정보 수집 및 이용 동의서]

1. 수집 항목
- 필수: 성명, 연락처, 생년월일
- 선택: 이메일, 주소, 건강 정보

2. 수집 목적
- 회원 관리 및 PT 서비스 제공
- 예약 알림 및 정보 안내
- 서비스 개선 및 통계 분석

3. 보유 기간
- 회원 탈퇴 시까지
- 관련 법령에 따른 보관 의무 기간

4. 동의 거부 권리
- 개인정보 수집 동의를 거부할 수 있습니다.
- 단, 필수 항목 거부 시 서비스 이용이 제한될 수 있습니다.

본인은 위 개인정보 수집 및 이용에 동의합니다.

날짜: {date}
회원명: {member_name}
서명:
""",
    
    "이용 약관": """
[PT샵 이용 약관]

제1조 (목적)
본 약관은 PT샵 서비스 이용에 관한 권리와 의무를 규정합니다.

제2조 (회원 가입)
- 회원 가입은 본인이 직접 신청해야 합니다.
- 허위 정보 기재 시 서비스 이용이 제한될 수 있습니다.

제3조 (서비스 이용)
- 시설 이용 시간: 평일 06:00-23:00, 주말 09:00-20:00
- PT 예약은 앱 또는 전화로 가능합니다.
- 타인에게 피해를 주는 행위는 금지됩니다.

제4조 (회원의 의무)
- 시설물을 소중히 사용해야 합니다.
- 다른 회원의 이용을 방해해서는 안 됩니다.
- 트레이너의 지시사항을 준수해야 합니다.

본인은 위 약관을 숙지하였으며 이에 동의합니다.

날짜: {date}
회원명: {member_name}
서명:
"""
}

# 탭 메뉴
tab1, tab2, tab3, tab4 = st.tabs(["계약서 생성", "대기 중 계약서", "서명 완료", "템플릿 관리"])

# === 계약서 생성 탭 ===
with tab1:
    st.markdown("### 새 계약서 생성")
    
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
        
        # 계약서 종류 선택
        contract_type = st.selectbox("계약서 종류", list(CONTRACT_TEMPLATES.keys()))
    
    with col2:
        # 추가 정보 입력
        if contract_type == "회원권 계약서":
            membership_type = st.selectbox("회원권 종류", ["PT10", "PT20", "PT30", "월간", "연간"])
            start_date = st.date_input("시작일")
            end_date = st.date_input("종료일")
            total_sessions = st.number_input("총 횟수", min_value=1, value=10)
            price = st.number_input("금액(원)", min_value=0, value=500000, step=10000)
        else:
            membership_type = None
            start_date = None
            end_date = None
            total_sessions = None
            price = None
    
    # 계약서 미리보기
    st.markdown("### 계약서 미리보기")
    
    if selected_member:
        # 템플릿에 정보 채우기
        contract_content = CONTRACT_TEMPLATES[contract_type].format(
            member_name=selected_member['name'],
            phone=selected_member['phone'],
            membership_type=membership_type or "",
            start_date=start_date.strftime("%Y-%m-%d") if start_date else "",
            end_date=end_date.strftime("%Y-%m-%d") if end_date else "",
            total_sessions=total_sessions or "",
            price=f"{price:,}" if price else "",
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # 미리보기 표시
        st.text_area("", value=contract_content, height=400, disabled=True)
        
        # 계약서 생성 버튼
        if st.button("계약서 생성 및 링크 전송", use_container_width=True, type="primary"):
            try:
                # 계약서 데이터 생성
                contract_data = {
                    "member_id": selected_member['id'],
                    "member_name": selected_member['name'],
                    "type": contract_type,
                    "content": contract_content
                }
                
                # 데이터베이스에 저장
                new_contract = db.create_contract(contract_data)
                
                # 서명 링크 생성
                base_url = st.secrets.get("BASE_URL", "http://localhost:8501")
                sign_url = f"{base_url}/sign?token={new_contract['link_token']}"
                
                # QR 코드 생성
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(sign_url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_image = buffer.getvalue()
                
                # 결과 표시
                st.success("계약서가 생성되었습니다!")
                
                st.markdown(f"""
                <div class="link-box">
                    <h4>서명 링크</h4>
                    <p>{sign_url}</p>
                    <p style="color: #6b7280; font-size: 0.875rem;">* 링크는 24시간 후 만료됩니다</p>
                </div>
                """, unsafe_allow_html=True)
                
                # QR 코드 표시
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(qr_image, caption="QR 코드", width=200)
                
                with col2:
                    st.info("""
                    **전송 방법**
                    1. 링크를 복사하여 카카오톡으로 전송
                    2. QR 코드를 저장하여 전송
                    3. 회원이 링크 접속 후 서명
                    """)
                
                # 카카오톡 전송 버튼 (실제 구현은 카카오 API 연동 필요)
                if st.button("카카오톡으로 전송", use_container_width=True):
                    st.info("카카오톡 전송 기능은 준비 중입니다.")
                
            except Exception as e:
                st.error(f"계약서 생성 중 오류가 발생했습니다: {str(e)}")
    else:
        st.info("회원을 선택해주세요.")

# === 대기 중 계약서 탭 ===
with tab2:
    st.markdown("### 서명 대기 중인 계약서")
    
    pending_contracts = db.get_pending_contracts()
    
    if pending_contracts:
        for contract in pending_contracts:
            with st.expander(f"{contract['member_name']} - {contract['type']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**회원명:** {contract['member_name']}")
                    st.write(f"**계약서 종류:** {contract['type']}")
                    st.write(f"**생성일:** {contract['created_at']}")
                    st.write(f"**만료일:** {contract['expires_at']}")
                    
                    # 상태 표시
                    st.markdown('<span class="status-pending">대기중</span>', unsafe_allow_html=True)
                
                with col2:
                    # 링크 재전송
                    if st.button("링크 재전송", key=f"resend_{contract['id']}"):
                        base_url = st.secrets.get("BASE_URL", "http://localhost:8501")
                        sign_url = f"{base_url}/sign?token={contract['link_token']}"
                        st.text_input("서명 링크", value=sign_url, key=f"link_{contract['id']}")
                    
                    # 계약서 취소
                    if st.button("취소", key=f"cancel_{contract['id']}", type="secondary"):
                        if db.update_contract(contract['id'], {"status": "cancelled"}):
                            st.success("계약서가 취소되었습니다")
                            st.rerun()
    else:
        st.info("대기 중인 계약서가 없습니다.")

# === 서명 완료 탭 ===
with tab3:
    st.markdown("### 서명 완료된 계약서")
    
    # 모든 계약서 조회 (서명 완료된 것만)
    all_contracts = []
    for member in db.get_all_members():
        contracts = [c for c in db.get_pending_contracts() if c.get('status') == 'signed']
        all_contracts.extend(contracts)
    
    if all_contracts:
        df_contracts = pd.DataFrame(all_contracts)
        
        # 컬럼 선택 및 이름 변경
        display_columns = ['member_name', 'type', 'created_at', 'signed_at']
        if all(col in df_contracts.columns for col in display_columns):
            df_display = df_contracts[display_columns].copy()
            
            column_names = {
                'member_name': '회원명',
                'type': '계약서 종류',
                'created_at': '생성일',
                'signed_at': '서명일'
            }
            df_display.rename(columns=column_names, inplace=True)
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # PDF 다운로드 기능 (추후 구현)
            st.info("PDF 다운로드 기능은 준비 중입니다.")
    else:
        st.info("서명 완료된 계약서가 없습니다.")

# === 템플릿 관리 탭 ===
with tab4:
    st.markdown("### 계약서 템플릿")
    
    # 현재 템플릿 목록
    for template_name, template_content in CONTRACT_TEMPLATES.items():
        with st.expander(template_name):
            st.text_area("", value=template_content, height=300, disabled=True, key=f"template_{template_name}")
    
    st.info("템플릿 수정 기능은 관리자 페이지에서 가능합니다.")