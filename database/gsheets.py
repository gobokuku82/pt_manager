"""
Google Sheets 데이터베이스 연결 및 CRUD 작업
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json
from typing import List, Dict, Optional, Any
import uuid

class GoogleSheetsDB:
    """Google Sheets 데이터베이스 클래스"""
    
    def __init__(self):
        """Google Sheets 연결 초기화"""
        self.client = None
        self.spreadsheet = None
        self.connect()
    
    def connect(self):
        """Google Sheets에 연결"""
        try:
            # Streamlit secrets에서 인증 정보 가져오기
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
            
            # gspread 클라이언트 생성
            self.client = gspread.authorize(credentials)
            
            # 스프레드시트 열기
            self.spreadsheet = self.client.open_by_key(st.secrets["SPREADSHEET_ID"])
            
        except Exception as e:
            st.error(f"Google Sheets 연결 실패: {str(e)}")
            raise
    
    def get_worksheet(self, sheet_name: str):
        """워크시트 가져오기"""
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # 워크시트가 없으면 생성
            worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            # 헤더 설정
            headers = self._get_headers(sheet_name)
            if headers:
                worksheet.update('A1', [headers])
            return worksheet
    
    def _get_headers(self, sheet_name: str) -> List[str]:
        """시트별 헤더 정의"""
        headers = {
            "Members": ["id", "name", "phone", "email", "birth_date", "gender", 
                       "address", "membership_type", "remaining_sessions", 
                       "created_at", "updated_at", "status"],
            "Schedules": ["id", "member_id", "member_name", "date", "time", 
                         "trainer", "type", "duration", "status", "notes", 
                         "created_at", "updated_at"],
            "Contracts": ["id", "member_id", "member_name", "type", "content", 
                         "created_at", "signed_at", "signature_url", "status", 
                         "link_token", "expires_at"],
            "Signatures": ["id", "contract_id", "signer_name", "signer_phone", 
                          "signature_data", "signed_at", "ip_address", "device_info"]
        }
        return headers.get(sheet_name, [])
    
    # === 회원 관리 CRUD ===
    
    def create_member(self, member_data: Dict) -> Dict:
        """회원 생성"""
        worksheet = self.get_worksheet("Members")
        
        # ID 생성
        member_data["id"] = str(uuid.uuid4())[:8]
        member_data["created_at"] = datetime.now().isoformat()
        member_data["updated_at"] = datetime.now().isoformat()
        member_data["status"] = member_data.get("status", "active")
        
        # 데이터 추가
        headers = self._get_headers("Members")
        row = [member_data.get(header, "") for header in headers]
        worksheet.append_row(row)
        
        return member_data
    
    def get_member(self, member_id: str) -> Optional[Dict]:
        """회원 조회"""
        worksheet = self.get_worksheet("Members")
        records = worksheet.get_all_records()
        
        for record in records:
            if record.get("id") == member_id:
                return record
        return None
    
    def get_all_members(self, status: Optional[str] = None) -> List[Dict]:
        """모든 회원 조회"""
        worksheet = self.get_worksheet("Members")
        records = worksheet.get_all_records()
        
        if status:
            records = [r for r in records if r.get("status") == status]
        
        return records
    
    def update_member(self, member_id: str, update_data: Dict) -> bool:
        """회원 정보 수정"""
        worksheet = self.get_worksheet("Members")
        records = worksheet.get_all_records()
        
        for idx, record in enumerate(records, start=2):  # 헤더 제외
            if record.get("id") == member_id:
                update_data["updated_at"] = datetime.now().isoformat()
                
                # 업데이트할 셀 찾기
                headers = self._get_headers("Members")
                for key, value in update_data.items():
                    if key in headers:
                        col_idx = headers.index(key) + 1
                        worksheet.update_cell(idx, col_idx, value)
                return True
        return False
    
    def delete_member(self, member_id: str) -> bool:
        """회원 삭제 (소프트 삭제)"""
        return self.update_member(member_id, {"status": "deleted"})
    
    def search_members(self, query: str) -> List[Dict]:
        """회원 검색"""
        worksheet = self.get_worksheet("Members")
        records = worksheet.get_all_records()
        
        results = []
        query_lower = query.lower()
        
        for record in records:
            if (query_lower in str(record.get("name", "")).lower() or
                query_lower in str(record.get("phone", "")).lower() or
                query_lower in str(record.get("email", "")).lower()):
                results.append(record)
        
        return results
    
    # === 스케줄 관리 CRUD ===
    
    def create_schedule(self, schedule_data: Dict) -> Dict:
        """스케줄 생성"""
        worksheet = self.get_worksheet("Schedules")
        
        schedule_data["id"] = str(uuid.uuid4())[:8]
        schedule_data["created_at"] = datetime.now().isoformat()
        schedule_data["updated_at"] = datetime.now().isoformat()
        schedule_data["status"] = schedule_data.get("status", "scheduled")
        
        headers = self._get_headers("Schedules")
        row = [schedule_data.get(header, "") for header in headers]
        worksheet.append_row(row)
        
        return schedule_data
    
    def get_schedules_by_date(self, date: str) -> List[Dict]:
        """날짜별 스케줄 조회"""
        worksheet = self.get_worksheet("Schedules")
        records = worksheet.get_all_records()
        
        return [r for r in records if r.get("date") == date]
    
    def get_member_schedules(self, member_id: str) -> List[Dict]:
        """회원별 스케줄 조회"""
        worksheet = self.get_worksheet("Schedules")
        records = worksheet.get_all_records()
        
        return [r for r in records if r.get("member_id") == member_id]
    
    def update_schedule(self, schedule_id: str, update_data: Dict) -> bool:
        """스케줄 수정"""
        worksheet = self.get_worksheet("Schedules")
        records = worksheet.get_all_records()
        
        for idx, record in enumerate(records, start=2):
            if record.get("id") == schedule_id:
                update_data["updated_at"] = datetime.now().isoformat()
                
                headers = self._get_headers("Schedules")
                for key, value in update_data.items():
                    if key in headers:
                        col_idx = headers.index(key) + 1
                        worksheet.update_cell(idx, col_idx, value)
                return True
        return False
    
    def cancel_schedule(self, schedule_id: str) -> bool:
        """스케줄 취소"""
        return self.update_schedule(schedule_id, {"status": "cancelled"})
    
    # === 계약서 관리 CRUD ===
    
    def create_contract(self, contract_data: Dict) -> Dict:
        """계약서 생성"""
        worksheet = self.get_worksheet("Contracts")
        
        contract_data["id"] = str(uuid.uuid4())[:8]
        contract_data["link_token"] = str(uuid.uuid4())
        contract_data["created_at"] = datetime.now().isoformat()
        contract_data["status"] = "pending"
        
        # 24시간 후 만료
        from datetime import timedelta
        expires_at = datetime.now() + timedelta(hours=24)
        contract_data["expires_at"] = expires_at.isoformat()
        
        headers = self._get_headers("Contracts")
        row = [contract_data.get(header, "") for header in headers]
        worksheet.append_row(row)
        
        return contract_data
    
    def get_contract_by_token(self, token: str) -> Optional[Dict]:
        """토큰으로 계약서 조회"""
        worksheet = self.get_worksheet("Contracts")
        records = worksheet.get_all_records()
        
        for record in records:
            if record.get("link_token") == token:
                # 만료 시간 체크
                expires_at = datetime.fromisoformat(record.get("expires_at"))
                if datetime.now() > expires_at:
                    return None
                return record
        return None
    
    def get_pending_contracts(self) -> List[Dict]:
        """대기중인 계약서 조회"""
        worksheet = self.get_worksheet("Contracts")
        records = worksheet.get_all_records()
        
        return [r for r in records if r.get("status") == "pending"]
    
    def update_contract(self, contract_id: str, update_data: Dict) -> bool:
        """계약서 업데이트"""
        worksheet = self.get_worksheet("Contracts")
        records = worksheet.get_all_records()
        
        for idx, record in enumerate(records, start=2):
            if record.get("id") == contract_id:
                headers = self._get_headers("Contracts")
                for key, value in update_data.items():
                    if key in headers:
                        col_idx = headers.index(key) + 1
                        worksheet.update_cell(idx, col_idx, value)
                return True
        return False
    
    # === 서명 관리 CRUD ===
    
    def create_signature(self, signature_data: Dict) -> Dict:
        """서명 저장"""
        worksheet = self.get_worksheet("Signatures")
        
        signature_data["id"] = str(uuid.uuid4())[:8]
        signature_data["signed_at"] = datetime.now().isoformat()
        
        headers = self._get_headers("Signatures")
        row = [signature_data.get(header, "") for header in headers]
        worksheet.append_row(row)
        
        # 관련 계약서 상태 업데이트
        if signature_data.get("contract_id"):
            self.update_contract(
                signature_data["contract_id"],
                {
                    "status": "signed",
                    "signed_at": signature_data["signed_at"],
                    "signature_url": signature_data.get("signature_data", "")[:100]  # 미리보기용
                }
            )
        
        return signature_data
    
    def get_signature(self, signature_id: str) -> Optional[Dict]:
        """서명 조회"""
        worksheet = self.get_worksheet("Signatures")
        records = worksheet.get_all_records()
        
        for record in records:
            if record.get("id") == signature_id:
                return record
        return None
    
    # === 통계 관련 ===
    
    def get_statistics(self) -> Dict:
        """통계 데이터 조회"""
        members = self.get_all_members(status="active")
        schedules_today = self.get_schedules_by_date(datetime.now().strftime("%Y-%m-%d"))
        pending_contracts = self.get_pending_contracts()
        
        return {
            "total_members": len(self.get_all_members()),
            "active_members": len(members),
            "today_sessions": len(schedules_today),
            "pending_signatures": len(pending_contracts)
        }
    
    # === 유틸리티 ===
    
    def backup_to_csv(self, sheet_name: str, filepath: str):
        """시트를 CSV로 백업"""
        worksheet = self.get_worksheet(sheet_name)
        df = pd.DataFrame(worksheet.get_all_records())
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        return filepath
    
    def restore_from_csv(self, sheet_name: str, filepath: str):
        """CSV에서 시트 복원"""
        df = pd.read_csv(filepath)
        worksheet = self.get_worksheet(sheet_name)
        
        # 기존 데이터 삭제
        worksheet.clear()
        
        # 새 데이터 추가
        headers = df.columns.tolist()
        values = [headers] + df.values.tolist()
        worksheet.update('A1', values)
        
        return True