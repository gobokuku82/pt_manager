"""
Pydantic 모델 정의
Google Sheets 데이터 검증용
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
import re

class Member(BaseModel):
    """회원 모델"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(남성|여성|기타)$")
    address: Optional[str] = None
    membership_type: Optional[str] = None
    remaining_sessions: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: str = "active"
    
    @validator('phone')
    def validate_phone(cls, v):
        # 한국 전화번호 형식 검증
        pattern = r'^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$'
        if not re.match(pattern, v.replace('-', '')):
            raise ValueError('올바른 전화번호 형식이 아닙니다')
        return v.replace('-', '')
    
    @validator('email')
    def validate_email(cls, v):
        if v:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v):
                raise ValueError('올바른 이메일 형식이 아닙니다')
        return v

class Schedule(BaseModel):
    """스케줄 모델"""
    id: Optional[str] = None
    member_id: str
    member_name: str
    date: str
    time: str
    trainer: str
    type: str = Field(..., pattern="^(PT|필라테스|재활|그룹)$")
    duration: int = Field(default=60, ge=30, le=120)  # 분 단위
    status: str = "scheduled"
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('날짜 형식은 YYYY-MM-DD 이어야 합니다')
        return v
    
    @validator('time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
        except ValueError:
            raise ValueError('시간 형식은 HH:MM 이어야 합니다')
        return v

class Contract(BaseModel):
    """계약서 모델"""
    id: Optional[str] = None
    member_id: str
    member_name: str
    type: str = Field(..., pattern="^(회원권|개인정보|이용약관|기타)$")
    content: str
    created_at: Optional[str] = None
    signed_at: Optional[str] = None
    signature_url: Optional[str] = None
    status: str = "pending"
    link_token: Optional[str] = None
    expires_at: Optional[str] = None
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) < 10:
            raise ValueError('계약서 내용은 최소 10자 이상이어야 합니다')
        return v

class Signature(BaseModel):
    """서명 모델"""
    id: Optional[str] = None
    contract_id: str
    signer_name: str
    signer_phone: str
    signature_data: str  # Base64 인코딩된 이미지
    signed_at: Optional[str] = None
    ip_address: Optional[str] = None
    device_info: Optional[str] = None
    
    @validator('signature_data')
    def validate_signature(cls, v):
        if not v.startswith('data:image'):
            raise ValueError('올바른 서명 데이터 형식이 아닙니다')
        return v
    
    @validator('signer_phone')
    def validate_phone(cls, v):
        pattern = r'^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$'
        if not re.match(pattern, v.replace('-', '')):
            raise ValueError('올바른 전화번호 형식이 아닙니다')
        return v.replace('-', '')

class Membership(BaseModel):
    """회원권 모델"""
    id: Optional[str] = None
    member_id: str
    type: str = Field(..., pattern="^(PT10|PT20|PT30|월간|연간)$")
    start_date: str
    end_date: str
    total_sessions: int = Field(ge=0)
    remaining_sessions: int = Field(ge=0)
    price: int = Field(ge=0)
    payment_status: str = Field(default="pending", pattern="^(paid|pending|partial)$")
    payment_method: Optional[str] = None
    created_at: Optional[str] = None
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values:
            start = datetime.strptime(values['start_date'], '%Y-%m-%d')
            end = datetime.strptime(v, '%Y-%m-%d')
            if end < start:
                raise ValueError('종료일은 시작일 이후여야 합니다')
        return v
    
    @validator('remaining_sessions')
    def validate_sessions(cls, v, values):
        if 'total_sessions' in values:
            if v > values['total_sessions']:
                raise ValueError('잔여 횟수는 전체 횟수를 초과할 수 없습니다')
        return v

class ChatMessage(BaseModel):
    """챗봇 메시지 모델"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[str] = None
    
    def dict(self):
        data = super().dict()
        if not data.get('timestamp'):
            data['timestamp'] = datetime.now().isoformat()
        return data

class KakaoMessage(BaseModel):
    """카카오톡 메시지 모델"""
    to_phone: str
    template_id: Optional[str] = None
    message: str
    link_url: Optional[str] = None
    link_mobile_url: Optional[str] = None
    button_title: Optional[str] = None
    
    @validator('to_phone')
    def validate_phone(cls, v):
        pattern = r'^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$'
        if not re.match(pattern, v.replace('-', '')):
            raise ValueError('올바른 전화번호 형식이 아닙니다')
        return v.replace('-', '')