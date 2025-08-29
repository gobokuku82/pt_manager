"""
LangGraph 에이전트용 도구 정의
"""

from langchain.tools import Tool, StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

# 도구 스키마 정의
class MemberSearchSchema(BaseModel):
    """회원 검색 스키마"""
    query: str = Field(description="검색어 (이름, 전화번호, 이메일)")

class MemberCreateSchema(BaseModel):
    """회원 생성 스키마"""
    name: str = Field(description="회원 이름")
    phone: str = Field(description="전화번호")
    email: Optional[str] = Field(description="이메일 주소")
    membership_type: Optional[str] = Field(description="회원권 종류")
    remaining_sessions: Optional[int] = Field(description="잔여 세션 수")

class ScheduleCreateSchema(BaseModel):
    """스케줄 생성 스키마"""
    member_id: str = Field(description="회원 ID")
    date: str = Field(description="예약 날짜 (YYYY-MM-DD)")
    time: str = Field(description="예약 시간 (HH:MM)")
    trainer: str = Field(description="트레이너 이름")
    type: str = Field(description="PT 종류")
    duration: int = Field(description="세션 시간(분)")

class ScheduleViewSchema(BaseModel):
    """스케줄 조회 스키마"""
    date: Optional[str] = Field(description="조회할 날짜 (YYYY-MM-DD)")
    member_id: Optional[str] = Field(description="회원 ID")

class ContractCreateSchema(BaseModel):
    """계약서 생성 스키마"""
    member_id: str = Field(description="회원 ID")
    member_name: str = Field(description="회원 이름")
    type: str = Field(description="계약서 종류")
    content: str = Field(description="계약서 내용")

class MessageSendSchema(BaseModel):
    """메시지 전송 스키마"""
    to_phone: str = Field(description="수신자 전화번호")
    message: str = Field(description="메시지 내용")
    link_url: Optional[str] = Field(description="링크 URL")

# 도구 함수 정의
def search_member(query: str) -> str:
    """회원 검색"""
    from database.gsheets import GoogleSheetsDB
    
    try:
        db = GoogleSheetsDB()
        members = db.search_members(query)
        
        if members:
            result = f"{len(members)}명의 회원을 찾았습니다:\n"
            for member in members[:5]:  # 최대 5명만 표시
                result += f"- {member['name']} ({member['phone']})\n"
            return result
        else:
            return "검색 결과가 없습니다."
    except Exception as e:
        return f"검색 중 오류 발생: {str(e)}"

def create_member(name: str, phone: str, email: Optional[str] = None,
                 membership_type: Optional[str] = None, 
                 remaining_sessions: Optional[int] = None) -> str:
    """회원 등록"""
    from database.gsheets import GoogleSheetsDB
    
    try:
        db = GoogleSheetsDB()
        member_data = {
            "name": name,
            "phone": phone,
            "email": email,
            "membership_type": membership_type,
            "remaining_sessions": remaining_sessions or 0
        }
        
        new_member = db.create_member(member_data)
        return f"회원 등록 완료: {new_member['name']} (ID: {new_member['id']})"
    except Exception as e:
        return f"회원 등록 중 오류 발생: {str(e)}"

def create_schedule(member_id: str, date: str, time: str, trainer: str,
                   type: str, duration: int) -> str:
    """PT 예약 생성"""
    from database.gsheets import GoogleSheetsDB
    
    try:
        db = GoogleSheetsDB()
        
        # 회원 정보 조회
        member = db.get_member(member_id)
        if not member:
            return f"회원 ID {member_id}를 찾을 수 없습니다."
        
        schedule_data = {
            "member_id": member_id,
            "member_name": member['name'],
            "date": date,
            "time": time,
            "trainer": trainer,
            "type": type,
            "duration": duration
        }
        
        new_schedule = db.create_schedule(schedule_data)
        return f"PT 예약 완료: {member['name']}님 {date} {time}"
    except Exception as e:
        return f"예약 생성 중 오류 발생: {str(e)}"

def view_schedule(date: Optional[str] = None, member_id: Optional[str] = None) -> str:
    """스케줄 조회"""
    from database.gsheets import GoogleSheetsDB
    
    try:
        db = GoogleSheetsDB()
        
        if member_id:
            schedules = db.get_member_schedules(member_id)
            title = f"회원 ID {member_id}의 스케줄"
        elif date:
            schedules = db.get_schedules_by_date(date)
            title = f"{date} 스케줄"
        else:
            date = datetime.now().strftime("%Y-%m-%d")
            schedules = db.get_schedules_by_date(date)
            title = f"오늘({date}) 스케줄"
        
        if schedules:
            result = f"{title}:\n"
            for schedule in schedules:
                result += f"- {schedule['time']} {schedule['member_name']} ({schedule['trainer']})\n"
            return result
        else:
            return f"{title}: 예약이 없습니다."
    except Exception as e:
        return f"스케줄 조회 중 오류 발생: {str(e)}"

def create_contract(member_id: str, member_name: str, type: str, content: str) -> str:
    """계약서 생성"""
    from database.gsheets import GoogleSheetsDB
    
    try:
        db = GoogleSheetsDB()
        
        contract_data = {
            "member_id": member_id,
            "member_name": member_name,
            "type": type,
            "content": content
        }
        
        new_contract = db.create_contract(contract_data)
        
        # 서명 링크 생성
        base_url = "https://your-app.streamlit.app"  # 실제 URL로 변경 필요
        sign_url = f"{base_url}/sign?token={new_contract['link_token']}"
        
        return f"계약서 생성 완료\n서명 링크: {sign_url}"
    except Exception as e:
        return f"계약서 생성 중 오류 발생: {str(e)}"

def send_kakao_message(to_phone: str, message: str, link_url: Optional[str] = None) -> str:
    """카카오톡 메시지 전송"""
    # 실제 카카오 API 연동 필요
    return f"메시지 전송 완료: {to_phone}로 '{message[:20]}...' 전송"

def get_statistics() -> str:
    """통계 조회"""
    from database.gsheets import GoogleSheetsDB
    
    try:
        db = GoogleSheetsDB()
        stats = db.get_statistics()
        
        result = "PT샵 현황:\n"
        result += f"- 전체 회원: {stats['total_members']}명\n"
        result += f"- 활성 회원: {stats['active_members']}명\n"
        result += f"- 오늘 PT: {stats['today_sessions']}건\n"
        result += f"- 대기중 서명: {stats['pending_signatures']}건"
        
        return result
    except Exception as e:
        return f"통계 조회 중 오류 발생: {str(e)}"

# LangChain 도구 생성
def get_tools() -> List[Tool]:
    """에이전트용 도구 목록 반환"""
    tools = [
        StructuredTool(
            name="search_member",
            description="회원을 이름, 전화번호, 이메일로 검색합니다",
            func=search_member,
            args_schema=MemberSearchSchema
        ),
        StructuredTool(
            name="create_member",
            description="새 회원을 등록합니다",
            func=create_member,
            args_schema=MemberCreateSchema
        ),
        StructuredTool(
            name="create_schedule",
            description="PT 세션을 예약합니다",
            func=create_schedule,
            args_schema=ScheduleCreateSchema
        ),
        StructuredTool(
            name="view_schedule",
            description="스케줄을 조회합니다",
            func=view_schedule,
            args_schema=ScheduleViewSchema
        ),
        StructuredTool(
            name="create_contract",
            description="계약서를 생성하고 서명 링크를 만듭니다",
            func=create_contract,
            args_schema=ContractCreateSchema
        ),
        StructuredTool(
            name="send_message",
            description="카카오톡 메시지를 전송합니다",
            func=send_kakao_message,
            args_schema=MessageSendSchema
        ),
        Tool(
            name="get_statistics",
            description="PT샵 통계를 조회합니다",
            func=get_statistics
        )
    ]
    
    return tools