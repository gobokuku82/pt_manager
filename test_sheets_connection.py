"""
Google Sheets 연결 및 읽기/쓰기 테스트
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

def test_connection():
    """Google Sheets 연결 테스트"""
    print("="*60)
    print("Google Sheets 연결 테스트")
    print("="*60)
    
    try:
        # Streamlit secrets 로드
        st.secrets.load_if_toml_exists()
        
        # 1. 인증
        print("\n1. 인증 정보 로드 중...")
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        print("[OK] 인증 성공")
        
        # 2. 클라이언트 생성
        print("\n2. gspread 클라이언트 생성...")
        client = gspread.authorize(credentials)
        print("[OK] 클라이언트 생성 성공")
        
        # 3. 스프레드시트 열기
        print("\n3. 스프레드시트 연결...")
        spreadsheet_id = st.secrets["SPREADSHEET_ID"]
        print(f"   스프레드시트 ID: {spreadsheet_id}")
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"[OK] 연결 성공: {spreadsheet.title}")
        
        # 4. 워크시트 목록
        print("\n4. 워크시트 목록:")
        worksheets = spreadsheet.worksheets()
        for ws in worksheets:
            print(f"   - {ws.title}")
        
        # 5. Members 시트 읽기 테스트
        print("\n5. Members 시트 읽기 테스트:")
        members_sheet = spreadsheet.worksheet("Members")
        all_values = members_sheet.get_all_values()
        print(f"   총 {len(all_values)} 행 발견")
        
        if len(all_values) > 0:
            print(f"   헤더: {all_values[0]}")
            if len(all_values) > 1:
                print(f"   첫 번째 데이터 행: {all_values[1][:5]}...")  # 처음 5개 컬럼만
        
        # 6. 쓰기 테스트
        print("\n6. 쓰기 테스트:")
        test_row = [
            f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "테스트 회원",
            "010-1234-5678",
            "test@example.com",
            "1990-01-01",
            "남성",
            "2024-12-29",
            "활성",
            "010-9999-9999",
            "없음",
            "체중 감량"
        ]
        
        members_sheet.append_row(test_row)
        print("[OK] 테스트 데이터 추가 성공")
        
        # 7. 방금 추가한 데이터 읽기
        print("\n7. 추가된 데이터 확인:")
        all_values = members_sheet.get_all_values()
        last_row = all_values[-1]
        print(f"   마지막 행: {last_row[:5]}...")
        
        # 8. Schedules 시트 테스트
        print("\n8. Schedules 시트 테스트:")
        schedules_sheet = spreadsheet.worksheet("Schedules")
        schedule_values = schedules_sheet.get_all_values()
        print(f"   총 {len(schedule_values)} 행 발견")
        
        # 9. Contracts 시트 테스트
        print("\n9. Contracts 시트 테스트:")
        contracts_sheet = spreadsheet.worksheet("Contracts")
        contract_values = contracts_sheet.get_all_values()
        print(f"   총 {len(contract_values)} 행 발견")
        
        # 10. Signatures 시트 테스트
        print("\n10. Signatures 시트 테스트:")
        signatures_sheet = spreadsheet.worksheet("Signatures")
        signature_values = signatures_sheet.get_all_values()
        print(f"   총 {len(signature_values)} 행 발견")
        
        print("\n" + "="*60)
        print("[OK] 모든 테스트 성공! Google Sheets 읽기/쓰기 정상 작동")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {str(e)}")
        print("\n문제 해결 방법:")
        print("1. secrets.toml 파일 확인")
        print("2. Google Sheets가 서비스 계정과 공유되었는지 확인")
        print("3. Google Sheets API가 활성화되었는지 확인")
        print("4. 스프레드시트 ID가 올바른지 확인")
        return False

if __name__ == "__main__":
    test_connection()