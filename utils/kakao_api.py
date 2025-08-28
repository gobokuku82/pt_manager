import requests
import json
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class KakaoAPI:
    def __init__(self):
        self.rest_api_key = os.getenv("KAKAO_REST_API_KEY")
        self.admin_key = os.getenv("KAKAO_ADMIN_KEY")
        self.channel_id = os.getenv("KAKAO_CHANNEL_ID")
        self.base_url = "https://kapi.kakao.com"
        
    def send_template_message(self, receiver_uuid: str, template_id: str, template_args: Dict) -> Dict:
        """카카오톡 템플릿 메시지 전송"""
        url = f"{self.base_url}/v1/api/talk/friends/message/send"
        
        headers = {
            "Authorization": f"KakaoAK {self.admin_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "receiver_uuids": json.dumps([receiver_uuid]),
            "template_id": template_id,
            "template_args": json.dumps(template_args)
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_custom_message(self, receiver_uuid: str, message: str, button_title: Optional[str] = None, 
                          button_url: Optional[str] = None) -> Dict:
        """카카오톡 커스텀 메시지 전송"""
        url = f"{self.base_url}/v2/api/talk/memo/default/send"
        
        headers = {
            "Authorization": f"Bearer {self.rest_api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        template_object = {
            "object_type": "text",
            "text": message
        }
        
        if button_title and button_url:
            template_object["link"] = {
                "web_url": button_url,
                "mobile_web_url": button_url
            }
            template_object["button_title"] = button_title
        
        data = {
            "template_object": json.dumps(template_object)
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_session_reminder(self, receiver_uuid: str, member_name: str, 
                            session_date: datetime, trainer_name: str) -> Dict:
        """PT 세션 알림 메시지 전송"""
        message = f"""안녕하세요, {member_name}님! 
        
PT 세션 안내드립니다.
📅 일시: {session_date.strftime('%Y-%m-%d %H:%M')}
👨‍⚕️ 담당 트레이너: {trainer_name}

준비물을 챙겨 10분 전까지 도착 부탁드립니다.
변경이 필요하시면 미리 연락 주세요!

건강한 하루 되세요! 💪"""
        
        return self.send_custom_message(
            receiver_uuid=receiver_uuid,
            message=message,
            button_title="일정 확인",
            button_url="https://your-pt-shop.com/schedule"
        )
    
    def send_payment_reminder(self, receiver_uuid: str, member_name: str, 
                            amount: int, due_date: str) -> Dict:
        """결제 알림 메시지 전송"""
        message = f"""안녕하세요, {member_name}님!

회원권 결제 안내드립니다.
💳 결제 금액: {amount:,}원
📅 결제 기한: {due_date}

편리한 시간에 결제 부탁드립니다.
감사합니다!"""
        
        return self.send_custom_message(
            receiver_uuid=receiver_uuid,
            message=message,
            button_title="결제하기",
            button_url="https://your-pt-shop.com/payment"
        )
    
    def send_membership_expiry_notice(self, receiver_uuid: str, member_name: str,
                                     remaining_sessions: int, expiry_date: str) -> Dict:
        """회원권 만료 안내 메시지"""
        message = f"""안녕하세요, {member_name}님!

회원권 만료 안내드립니다.
🔔 남은 횟수: {remaining_sessions}회
📅 만료일: {expiry_date}

연장을 원하시면 언제든지 문의 주세요!
항상 건강하세요! 🌟"""
        
        return self.send_custom_message(
            receiver_uuid=receiver_uuid,
            message=message,
            button_title="회원권 연장",
            button_url="https://your-pt-shop.com/membership"
        )
    
    def send_welcome_message(self, receiver_uuid: str, member_name: str) -> Dict:
        """신규 회원 환영 메시지"""
        message = f"""환영합니다, {member_name}님! 🎉

저희 PT샵의 회원이 되신 것을 진심으로 환영합니다!

앞으로 함께 건강한 몸과 마음을 만들어가요.
궁금한 점이 있으시면 언제든지 문의해주세요.

첫 PT 세션 예약을 도와드릴게요!
건강한 시작을 응원합니다! 💪✨"""
        
        return self.send_custom_message(
            receiver_uuid=receiver_uuid,
            message=message,
            button_title="PT 예약하기",
            button_url="https://your-pt-shop.com/booking"
        )

# 싱글톤 인스턴스
kakao_api = KakaoAPI()