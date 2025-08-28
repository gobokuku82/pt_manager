import os
import sys
import subprocess

def main():
    """메인 애플리케이션 실행"""
    print("🚀 PT Shop Management System 시작...")
    print("-" * 50)
    
    # 환경 변수 파일 확인
    if not os.path.exists(".env"):
        if os.path.exists("config/.env.example"):
            print("⚠️  .env 파일이 없습니다.")
            print("config/.env.example 파일을 복사하여 .env 파일을 생성하고")
            print("필요한 API 키를 설정해주세요.")
            print("-" * 50)
            return
    
    # 데이터베이스 초기화
    print("📊 데이터베이스 초기화 중...")
    from database.models import init_database
    init_database()
    print("✅ 데이터베이스 초기화 완료")
    
    # Streamlit 앱 실행
    print("-" * 50)
    print("🌐 웹 애플리케이션 시작 중...")
    print("브라우저에서 http://localhost:8501 로 접속하세요")
    print("종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py"])

if __name__ == "__main__":
    main()