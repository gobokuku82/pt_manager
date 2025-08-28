"""
Streamlit Cloud 엔트리 포인트
메인 앱을 실행합니다.
"""

import sys
import os

# 프로젝트 경로를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 메인 앱 실행
from app.main import *