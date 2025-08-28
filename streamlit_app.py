"""
Streamlit Cloud 엔트리 포인트
메인 앱을 실행합니다.
"""

import sys
import os

# 프로젝트 경로를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# set_page_config를 건너뛰도록 플래그 설정
os.environ['STREAMLIT_RUNNING'] = 'true'

# 메인 앱 모듈을 직접 실행
exec(open(os.path.join(project_root, 'app', 'main.py')).read())