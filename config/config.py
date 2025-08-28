import os
import streamlit as st
from dotenv import load_dotenv

def get_config():
    """환경변수 또는 Streamlit secrets에서 설정 가져오기"""
    config = {}
    
    # Streamlit Cloud 환경인지 확인
    if hasattr(st, 'secrets') and len(st.secrets) > 0:
        # Streamlit Cloud에서 실행 중 - st.secrets 사용
        config = {
            'OPENAI_API_KEY': st.secrets.get('OPENAI_API_KEY'),
            'KAKAO_REST_API_KEY': st.secrets.get('KAKAO_REST_API_KEY'),
            'KAKAO_JAVASCRIPT_KEY': st.secrets.get('KAKAO_JAVASCRIPT_KEY'),
            'KAKAO_ADMIN_KEY': st.secrets.get('KAKAO_ADMIN_KEY'),
            'KAKAO_REDIRECT_URI': st.secrets.get('KAKAO_REDIRECT_URI'),
            'KAKAO_CHANNEL_ID': st.secrets.get('KAKAO_CHANNEL_ID'),
            'DATABASE_URL': st.secrets.get('DATABASE_URL'),
            'APP_NAME': st.secrets.get('APP_NAME', 'PT Shop Management System'),
            'APP_VERSION': st.secrets.get('APP_VERSION', '1.0.0'),
            'DEBUG_MODE': st.secrets.get('DEBUG_MODE', False),
            'SESSION_SECRET_KEY': st.secrets.get('SESSION_SECRET_KEY')
        }
    else:
        # 로컬 환경 - .env 파일 사용
        load_dotenv()
        config = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'KAKAO_REST_API_KEY': os.getenv('KAKAO_REST_API_KEY'),
            'KAKAO_JAVASCRIPT_KEY': os.getenv('KAKAO_JAVASCRIPT_KEY'),
            'KAKAO_ADMIN_KEY': os.getenv('KAKAO_ADMIN_KEY'),
            'KAKAO_REDIRECT_URI': os.getenv('KAKAO_REDIRECT_URI'),
            'KAKAO_CHANNEL_ID': os.getenv('KAKAO_CHANNEL_ID'),
            'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///database/pt_shop.db'),
            'APP_NAME': os.getenv('APP_NAME', 'PT Shop Management System'),
            'APP_VERSION': os.getenv('APP_VERSION', '1.0.0'),
            'DEBUG_MODE': os.getenv('DEBUG_MODE', 'False').lower() == 'true',
            'SESSION_SECRET_KEY': os.getenv('SESSION_SECRET_KEY')
        }
    
    return config