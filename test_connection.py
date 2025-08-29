"""
Google Sheets 연결 테스트 스크립트
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

def test_google_sheets_connection():
    """Google Sheets 연결 테스트"""
    
    print("=" * 50)
    print("Google Sheets 연결 테스트 시작")
    print("=" * 50)
    
    try:
        # 1. 인증 정보 로드
        print("\n1. 인증 정보 로드 중...")
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        print("✅ 인증 정보 로드 성공")
        
        # 2. gspread 클라이언트 생성
        print("\n2. Google Sheets 클라이언트 생성 중...")
        client = gspread.authorize(credentials)
        print("✅ 클라이언트 생성 성공")
        
        # 3. 스프레드시트 열기
        print("\n3. 스프레드시트 연결 중...")
        spreadsheet_id = st.secrets["SPREADSHEET_ID"]
        print(f"   스프레드시트 ID: {spreadsheet_id}")
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"✅ 스프레드시트 연결 성공: {spreadsheet.title}")
        
        # 4. 시트 목록 확인
        print("\n4. 시트 목록 확인...")
        worksheets = spreadsheet.worksheets()
        print(f"   발견된 시트 수: {len(worksheets)}")
        for ws in worksheets:
            print(f"   - {ws.title}")
        
        # 5. 필요한 시트 생성 또는 확인
        print("\n5. 필수 시트 확인 및 생성...")
        required_sheets = ["Members", "Schedules", "Contracts", "Signatures"]
        existing_sheet_names = [ws.title for ws in worksheets]
        
        for sheet_name in required_sheets:
            if sheet_name not in existing_sheet_names:
                print(f"   Creating sheet: {sheet_name}")
                spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
                print(f"   ✅ {sheet_name} 시트 생성됨")
            else:
                print(f"   ✅ {sheet_name} 시트 확인됨")
        
        # 6. Members 시트에 헤더 추가
        print("\n6. Members 시트 헤더 설정...")
        members_sheet = spreadsheet.worksheet("Members")
        
        # 헤더가 비어있으면 추가
        if not members_sheet.get_all_values():
            headers = ["id", "name", "phone", "email", "birth_date", "gender", 
                      "address", "membership_type", "remaining_sessions", 
                      "created_at", "updated_at", "status"]
            members_sheet.update('A1', [headers])
            print("   ✅ Members 시트 헤더 추가됨")
        else:
            print("   ✅ Members 시트 헤더 확인됨")
        
        # 7. 테스트 데이터 추가
        print("\n7. 테스트 데이터 추가...")
        test_data = [
            f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "테스트 회원",
            "010-1234-5678",
            "test@example.com",
            "1990-01-01",
            "남성",
            "서울시 강남구",
            "PT10",
            "10",
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            "active"
        ]
        
        members_sheet.append_row(test_data)
        print("   ✅ 테스트 데이터 추가됨")
        
        # 8. 데이터 읽기 테스트
        print("\n8. 데이터 읽기 테스트...")
        all_records = members_sheet.get_all_records()
        print(f"   ✅ 총 {len(all_records)}개의 레코드 확인됨")
        
        if all_records:
            print("\n   최근 추가된 레코드:")
            last_record = all_records[-1]
            for key, value in last_record.items():
                print(f"      {key}: {value}")
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 성공!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        print("\n문제 해결 방법:")
        print("1. secrets.toml 파일이 올바르게 설정되었는지 확인")
        print("2. Google Sheets가 서비스 계정과 공유되었는지 확인")
        print("3. Google Sheets API가 활성화되었는지 확인")
        return False

if __name__ == "__main__":
    # Streamlit 없이 실행하는 경우를 위한 대체 코드
    try:
        test_google_sheets_connection()
    except Exception as e:
        print("\n⚠️ Streamlit 환경에서 실행해주세요:")
        print("streamlit run test_connection.py")