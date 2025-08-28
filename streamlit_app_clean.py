"""
Streamlit Cloud 엔트리 포인트 (정리된 버전)
"""

import sys
import os

# 프로젝트 경로를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 메인 앱 실행
from app.main import *