"""
플로팅 챗봇 버튼 테스트
streamlit-float와 HTML/CSS 방식 비교
"""

import streamlit as st
from streamlit_float import *

st.set_page_config(page_title="플로팅 버튼 테스트", layout="wide")

st.title("플로팅 버튼 테스트")

# 방법 1: HTML + CSS (st.markdown)
st.markdown("## 방법 1: HTML + CSS")
st.markdown("""
<style>
.floating-chat-button {
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
    z-index: 9999;
    color: white;
    font-size: 24px;
}
.floating-chat-button:hover {
    transform: scale(1.1);
}
</style>
<div class="floating-chat-button" onclick="alert('버튼 클릭!')">
    💬
</div>
""", unsafe_allow_html=True)

# 방법 2: streamlit.components.v1.html
st.markdown("## 방법 2: components.v1.html")
st.components.v1.html("""
<style>
.float-button {
    position: fixed;
    bottom: 100px;
    right: 30px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #ff6b6b;
    color: white;
    border: none;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 1000;
}
</style>
<button class="float-button" onclick="console.log('클릭!')">📱</button>
""", height=100)

# 방법 3: streamlit-float 라이브러리
st.markdown("## 방법 3: streamlit-float")

# Float 초기화
float_init()

# 일반 콘텐츠
st.write("이것은 일반 콘텐츠입니다.")
st.write("스크롤해도 플로팅 버튼은 고정되어야 합니다.")

# 플로팅 컨테이너 생성
button_container = st.container()
with button_container:
    col1, col2, col3 = st.columns([8, 1, 1])
    with col3:
        if st.button("🤖", key="float_btn", help="챗봇 열기"):
            st.balloons()
            st.success("챗봇 버튼이 클릭되었습니다!")

# Float 설정
float_parent()
button_css = """
<style>
[data-testid="stVerticalBlock"] > [style*="flex-direction: row"] {
    position: fixed !important;
    bottom: 30px !important;
    right: 30px !important;
    z-index: 999 !important;
    background: transparent !important;
}
</style>
"""
st.markdown(button_css, unsafe_allow_html=True)

# 세션 상태
if "chatbot_open" not in st.session_state:
    st.session_state.chatbot_open = False

# 방법 4: CSS로 특정 버튼 플로팅
st.markdown("## 방법 4: 특정 버튼 CSS 오버라이드")

if st.button("💬 채팅", key="special_chat_btn"):
    st.session_state.chatbot_open = not st.session_state.chatbot_open

# 특정 버튼만 플로팅
st.markdown("""
<style>
div[data-testid="stButton"] button[kind="primary"] {
    position: fixed !important;
    bottom: 200px !important;
    right: 30px !important;
    width: 60px !important;
    height: 60px !important;
    border-radius: 50% !important;
    z-index: 999 !important;
}
</style>
""", unsafe_allow_html=True)

if st.session_state.chatbot_open:
    with st.container():
        st.markdown("""
        <div style="position: fixed; bottom: 100px; right: 30px; 
                    width: 300px; height: 400px; 
                    background: white; border-radius: 15px; 
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2); 
                    padding: 20px; z-index: 998;">
            <h3>챗봇</h3>
            <p>여기에 챗봇 내용이 표시됩니다.</p>
        </div>
        """, unsafe_allow_html=True)

# 더미 콘텐츠 (스크롤 테스트용)
for i in range(20):
    st.write(f"더미 콘텐츠 {i+1}")