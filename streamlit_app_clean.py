"""
Streamlit Cloud 엔트리 포인트 (정리된 버전)
"""

import sys
import os
import streamlit as st

# 프로젝트 경로를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 페이지 설정 (가장 먼저 실행)
st.set_page_config(
    page_title="PT Shop Management System",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# set_page_config를 건너뛰도록 플래그 설정
os.environ['STREAMLIT_RUNNING'] = 'true'

# 메인 앱 실행
from app import main