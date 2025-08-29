"""
모바일 서명 페이지
계약서 서명을 위한 모바일 최적화 페이지
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd
from datetime import datetime
import base64
from database.gsheets import GoogleSheetsDB

# 페이지 설정 - 모바일 최적화
st.set_page_config(
    page_title="계약서 서명",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 데이터베이스 연결
@st.cache_resource
def get_db():
    return GoogleSheetsDB()

db = get_db()

# 모바일 최적화 스타일
st.markdown("""
<style>
/* 사이드바 숨기기 */
section[data-testid="stSidebar"] {
    display: none;
}

/* 모바일 최적화 */
.main {
    padding: 1rem;
    max-width: 100%;
}

.signature-container {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
}

.contract-content {
    background: #f9fafb;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    max-height: 400px;
    overflow-y: auto;
    font-size: 0.9rem;
    line-height: 1.6;
}

.signature-box {
    border: 2px dashed #9ca3af;
    border-radius: 10px;
    padding: 1rem;
    background: white;
    margin: 1rem 0;
}

.submit-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 2rem;
    border-radius: 10px;
    font-size: 1.1rem;
    font-weight: bold;
    border: none;
    width: 100%;
    cursor: pointer;
}

.info-box {
    background: #eff6ff;
    border: 1px solid #60a5fa;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.success-message {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    margin: 2rem 0;
}

.error-message {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}

h1, h2, h3 {
    color: #1f2937;
}

/* 모바일 화면 조정 */
@media (max-width: 768px) {
    .main {
        padding: 0.5rem;
    }
    
    .signature-container {
        padding: 1rem;
    }
    
    .contract-content {
        font-size: 0.85rem;
    }
}
</style>
""", unsafe_allow_html=True)

# URL 파라미터에서 토큰 가져오기
query_params = st.query_params
token = query_params.get("token", None)

if not token:
    st.markdown("""
    <div class="error-message">
        <h2>⚠️ 잘못된 접근</h2>
        <p>유효한 서명 링크를 통해 접속해주세요.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# 토큰으로 계약서 조회
contract = db.get_contract_by_token(token)

if not contract:
    st.markdown("""
    <div class="error-message">
        <h2>⚠️ 만료된 링크</h2>
        <p>서명 링크가 만료되었거나 유효하지 않습니다.</p>
        <p>PT샵에 문의해주세요.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# 이미 서명된 계약서 체크
if contract.get("status") == "signed":
    st.markdown("""
    <div class="success-message">
        <h2>✅ 서명 완료</h2>
        <p>이미 서명이 완료된 계약서입니다.</p>
        <p>서명일: {}</p>
    </div>
    """.format(contract.get("signed_at", "")), unsafe_allow_html=True)
    st.stop()

# 서명 페이지 메인
st.markdown("""
<div class="signature-container">
    <h1 style="text-align: center; color: #667eea;">📝 계약서 서명</h1>
</div>
""", unsafe_allow_html=True)

# 회원 정보 확인
st.markdown(f"""
<div class="info-box">
    <strong>회원명:</strong> {contract.get('member_name', '')}<br>
    <strong>계약서 종류:</strong> {contract.get('type', '')}
</div>
""", unsafe_allow_html=True)

# 계약서 내용 표시
st.markdown("### 계약서 내용")
st.markdown(f"""
<div class="contract-content">
    {contract.get('content', '').replace('\n', '<br>')}
</div>
""", unsafe_allow_html=True)

# 동의 체크박스
agree1 = st.checkbox("위 계약 내용을 확인하였으며 동의합니다.")
agree2 = st.checkbox("개인정보 수집 및 이용에 동의합니다.")

# 서명자 정보 입력
st.markdown("### 서명자 정보")
col1, col2 = st.columns(2)
with col1:
    signer_name = st.text_input("이름", placeholder="홍길동")
with col2:
    signer_phone = st.text_input("전화번호", placeholder="010-1234-5678")

# 서명 캔버스
st.markdown("### 서명")
st.markdown("""
<div class="info-box">
    아래 박스에 손가락이나 마우스로 서명해주세요.
</div>
""", unsafe_allow_html=True)

# 캔버스 설정
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=200,
    width=None,
    drawing_mode="freedraw",
    key="signature_canvas",
)

# 서명 초기화 버튼
col1, col2 = st.columns(2)
with col1:
    if st.button("서명 지우기", use_container_width=True):
        st.rerun()

# 제출 버튼
with col2:
    if st.button("서명 완료", use_container_width=True, type="primary"):
        # 유효성 검사
        errors = []
        
        if not agree1 or not agree2:
            errors.append("모든 동의 항목에 체크해주세요.")
        
        if not signer_name or not signer_phone:
            errors.append("서명자 정보를 모두 입력해주세요.")
        
        if canvas_result.image_data is None:
            errors.append("서명을 해주세요.")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                # 서명 이미지를 base64로 변환
                import json
                from PIL import Image
                import io
                
                # 캔버스 데이터를 이미지로 변환
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                
                # 이미지를 base64 문자열로 변환
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_str = base64.b64encode(buffer.getvalue()).decode()
                signature_data = f"data:image/png;base64,{img_str}"
                
                # 서명 데이터 저장
                signature_info = {
                    "contract_id": contract['id'],
                    "signer_name": signer_name,
                    "signer_phone": signer_phone,
                    "signature_data": signature_data,
                    "ip_address": st.session_state.get('client_ip', 'unknown'),
                    "device_info": st.session_state.get('user_agent', 'unknown')
                }
                
                # 데이터베이스에 저장
                db.create_signature(signature_info)
                
                # 성공 메시지
                st.markdown("""
                <div class="success-message">
                    <h2>✅ 서명이 완료되었습니다!</h2>
                    <p>계약서 서명이 성공적으로 처리되었습니다.</p>
                    <p>감사합니다.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 3초 후 자동 새로고침
                import time
                time.sleep(3)
                st.rerun()
                
            except Exception as e:
                st.error(f"서명 처리 중 오류가 발생했습니다: {str(e)}")

# 하단 안내
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.875rem; margin-top: 2rem;">
    <p>문의사항이 있으시면 PT샵으로 연락주세요.</p>
    <p>📞 02-1234-5678</p>
</div>
""", unsafe_allow_html=True)