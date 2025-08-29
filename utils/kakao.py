"""
카카오톡 메시지 API 유틸리티
"""

import requests
import json
import streamlit as st
from typing import Dict, Optional, Any
from datetime import datetime

class KakaoAPI:
    """카카오톡 API 클래스"""
    
    def __init__(self):
        """카카오 API 초기화"""
        self.rest_api_key = st.secrets.get("KAKAO_REST_API_KEY", "")
        self.admin_key = st.secrets.get("KAKAO_ADMIN_KEY", "")
        self.redirect_uri = st.secrets.get("KAKAO_REDIRECT_URI", "http://localhost:8501")
        self.access_token = None
    
    def get_access_token(self, auth_code: str) -> Optional[str]:
        """인가 코드로 액세스 토큰 획득"""
        url = "https://kauth.kakao.com/oauth/token"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.rest_api_key,
            "redirect_uri": self.redirect_uri,
            "code": auth_code
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get("access_token")
            return self.access_token
        else:
            print(f"토큰 획득 실패: {response.text}")
            return None
    
    def send_to_me(self, message: str, button_title: Optional[str] = None,
                   button_url: Optional[str] = None) -> bool:
        """나에게 메시지 보내기"""
        if not self.access_token:
            print("액세스 토큰이 없습니다. 로그인이 필요합니다.")
            return False
        
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # 메시지 템플릿
        template = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": button_url or self.redirect_uri,
                "mobile_web_url": button_url or self.redirect_uri
            }
        }
        
        if button_title and button_url:
            template["button_title"] = button_title
        
        data = {
            "template_object": json.dumps(template)
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            print("메시지 전송 성공")
            return True
        else:
            print(f"메시지 전송 실패: {response.text}")
            return False
    
    def send_custom_template(self, template_id: str, template_args: Dict) -> bool:
        """커스텀 템플릿 메시지 전송"""
        if not self.access_token:
            print("액세스 토큰이 없습니다.")
            return False
        
        url = "https://kapi.kakao.com/v2/api/talk/memo/send"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "template_id": template_id,
            "template_args": json.dumps(template_args)
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.status_code == 200
    
    def create_contract_message(self, member_name: str, contract_type: str,
                               sign_url: str) -> str:
        """계약서 서명 요청 메시지 생성"""
        message = f"""
[PT Manager] 계약서 서명 요청

안녕하세요, {member_name}님!
{contract_type} 서명을 요청드립니다.

아래 링크를 클릭하여 서명해주세요:
{sign_url}

* 링크는 24시간 후 만료됩니다.
* 문의: 02-1234-5678
        """.strip()
        
        return message
    
    def create_reminder_message(self, member_name: str, date: str, 
                               time: str, trainer: str) -> str:
        """PT 예약 리마인더 메시지 생성"""
        message = f"""
[PT Manager] 예약 알림

{member_name}님, PT 예약을 알려드립니다.

📅 날짜: {date}
⏰ 시간: {time}
👨‍🏫 트레이너: {trainer}

* 변경/취소는 1일 전까지 가능합니다.
* 문의: 02-1234-5678
        """.strip()
        
        return message
    
    def create_expiry_message(self, member_name: str, remaining_days: int,
                            remaining_sessions: int) -> str:
        """회원권 만료 알림 메시지 생성"""
        message = f"""
[PT Manager] 회원권 만료 예정

{member_name}님의 회원권이 곧 만료됩니다.

⏳ 남은 기간: {remaining_days}일
🎫 남은 횟수: {remaining_sessions}회

회원권 연장을 원하시면 PT샵으로 문의해주세요.
문의: 02-1234-5678
        """.strip()
        
        return message
    
    def log_message(self, to: str, message_type: str, content: str,
                   status: str = "pending") -> Dict:
        """메시지 전송 로그 기록"""
        log = {
            "timestamp": datetime.now().isoformat(),
            "to": to,
            "type": message_type,
            "content": content[:100],  # 처음 100자만 저장
            "status": status
        }
        
        # 실제로는 데이터베이스에 저장
        print(f"메시지 로그: {log}")
        
        return log

# 헬퍼 함수
def send_kakao_message(member_phone: str, message: str, 
                      link_url: Optional[str] = None) -> bool:
    """카카오톡 메시지 전송 헬퍼 함수"""
    api = KakaoAPI()
    
    # 실제 구현에서는 회원 전화번호로 카카오 계정 매핑 필요
    # 현재는 나에게 보내기만 구현
    
    if api.access_token:
        return api.send_to_me(
            message=message,
            button_title="바로가기" if link_url else None,
            button_url=link_url
        )
    else:
        # 액세스 토큰이 없으면 로그만 남기기
        api.log_message(
            to=member_phone,
            message_type="kakao",
            content=message,
            status="failed"
        )
        return False

def get_kakao_auth_url() -> str:
    """카카오 인증 URL 생성"""
    rest_api_key = st.secrets.get("KAKAO_REST_API_KEY", "")
    redirect_uri = st.secrets.get("KAKAO_REDIRECT_URI", "http://localhost:8501")
    
    auth_url = f"https://kauth.kakao.com/oauth/authorize"
    auth_url += f"?client_id={rest_api_key}"
    auth_url += f"&redirect_uri={redirect_uri}"
    auth_url += f"&response_type=code"
    auth_url += f"&scope=talk_message"  # 메시지 전송 권한
    
    return auth_url