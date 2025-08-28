"""
Streamlit Cloud 엔트리 포인트
메인 앱을 실행합니다.
"""

import sys
import os
import streamlit as st

# 디버그 정보
st.write("현재 작업 디렉토리:", os.getcwd())
st.write("Python 경로:", sys.path[:3])

# 프로젝트 경로를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
st.write("프로젝트 루트:", project_root)

# 파일 존재 확인
css_path = os.path.join(project_root, 'styles', 'style.css')
st.write("CSS 파일 존재:", os.path.exists(css_path))

try:
    # 메인 앱 실행
    from app.main import *
except Exception as e:
    st.error(f"앱 로드 중 오류 발생: {e}")
    st.exception(e)