from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from agents.state import AgentState
from agents.tools import tools
from utils.kakao_api import kakao_api
from database.models import Member, get_db
import json
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import get_config

# 설정 가져오기
config = get_config()

# OpenAI 모델 초기화
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=config.get("OPENAI_API_KEY")
)

# 도구가 있는 LLM
llm_with_tools = llm.bind_tools(tools)

def member_management_node(state: AgentState) -> Dict:
    """회원 관리 노드"""
    messages = state.get("messages", [])
    
    if not messages:
        return state
    
    last_message = messages[-1]
    
    # LLM으로 의도 파악 및 도구 선택
    system_prompt = """당신은 PT샵 회원 관리 AI 어시스턴트입니다.
    사용자의 요청을 분석하여 적절한 회원 관리 작업을 수행하세요.
    
    가능한 작업:
    - 회원 검색 및 조회
    - 신규 회원 등록
    - 회원 상태 변경
    - 회원권 생성 및 관리
    """
    
    response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        last_message
    ])
    
    # 도구 호출 결과 처리
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # 도구 실행
            for tool in tools:
                if tool.name == tool_name:
                    result = tool.invoke(tool_args)
                    tool_results.append(result)
                    break
        
        state["action_result"] = {"tool_results": tool_results}
    
    state["messages"].append(response)
    return state

def consultation_node(state: AgentState) -> Dict:
    """상담 처리 노드"""
    messages = state.get("messages", [])
    current_member = state.get("current_member")
    
    if not messages:
        return state
    
    last_message = messages[-1]
    
    system_prompt = """당신은 PT샵 상담 AI 어시스턴트입니다.
    회원의 문의사항에 친절하고 전문적으로 답변하세요.
    
    상담 가능 분야:
    - PT 프로그램 안내
    - 회원권 및 가격 문의
    - 일정 조정 및 예약
    - 운동 및 건강 관련 조언
    """
    
    # 회원 정보가 있으면 컨텍스트에 추가
    if current_member:
        system_prompt += f"\n\n현재 상담 회원 정보:\n이름: {current_member.get('name')}\n회원 상태: {current_member.get('membership_status')}"
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        last_message
    ])
    
    # 상담 내용 저장
    if current_member:
        from agents.tools import create_consultation
        consultation_data = {
            "member_id": current_member.get("id"),
            "consultation_type": "chat",
            "subject": "챗봇 상담",
            "content": last_message.content if hasattr(last_message, 'content') else str(last_message),
            "response": response.content,
            "status": "resolved"
        }
        create_consultation.invoke(json.dumps(consultation_data))
    
    state["messages"].append(response)
    return state

def schedule_management_node(state: AgentState) -> Dict:
    """스케줄 관리 노드"""
    messages = state.get("messages", [])
    
    if not messages:
        return state
    
    last_message = messages[-1]
    
    system_prompt = """당신은 PT샵 스케줄 관리 AI 어시스턴트입니다.
    PT 세션 예약, 변경, 취소를 관리합니다.
    
    주요 기능:
    - PT 세션 예약
    - 예약 변경 및 취소
    - 트레이너 일정 확인
    - 회원 일정 조회
    """
    
    response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        last_message
    ])
    
    # 도구 호출 처리
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            for tool in tools:
                if tool.name == tool_name:
                    result = tool.invoke(tool_args)
                    tool_results.append(result)
                    
                    # 예약 성공 시 카카오톡 알림 전송
                    if tool_name == "schedule_pt_session" and result.get("success"):
                        member_id = tool_args.get("member_id")
                        db = next(get_db())
                        member = db.query(Member).filter(Member.id == member_id).first()
                        if member and member.kakao_id:
                            kakao_api.send_session_reminder(
                                receiver_uuid=member.kakao_id,
                                member_name=member.name,
                                session_date=tool_args.get("session_date"),
                                trainer_name="트레이너"
                            )
                        db.close()
                    break
        
        state["action_result"] = {"tool_results": tool_results}
    
    state["messages"].append(response)
    return state

def notification_node(state: AgentState) -> Dict:
    """알림 전송 노드"""
    kakao_message = state.get("kakao_message")
    
    if not kakao_message:
        return state
    
    # 카카오톡 메시지 전송
    message_type = kakao_message.get("type")
    receiver_uuid = kakao_message.get("receiver_uuid")
    
    result = None
    if message_type == "session_reminder":
        result = kakao_api.send_session_reminder(
            receiver_uuid=receiver_uuid,
            member_name=kakao_message.get("member_name"),
            session_date=kakao_message.get("session_date"),
            trainer_name=kakao_message.get("trainer_name")
        )
    elif message_type == "payment_reminder":
        result = kakao_api.send_payment_reminder(
            receiver_uuid=receiver_uuid,
            member_name=kakao_message.get("member_name"),
            amount=kakao_message.get("amount"),
            due_date=kakao_message.get("due_date")
        )
    elif message_type == "membership_expiry":
        result = kakao_api.send_membership_expiry_notice(
            receiver_uuid=receiver_uuid,
            member_name=kakao_message.get("member_name"),
            remaining_sessions=kakao_message.get("remaining_sessions"),
            expiry_date=kakao_message.get("expiry_date")
        )
    elif message_type == "welcome":
        result = kakao_api.send_welcome_message(
            receiver_uuid=receiver_uuid,
            member_name=kakao_message.get("member_name")
        )
    
    if result:
        state["action_result"] = {"notification_result": result}
    
    return state

def router(state: AgentState) -> str:
    """라우터 - 다음 노드 결정"""
    messages = state.get("messages", [])
    
    if not messages:
        return "end"
    
    last_message = messages[-1]
    message_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    # 간단한 키워드 기반 라우팅
    if any(word in message_content.lower() for word in ["회원", "등록", "가입", "검색"]):
        return "member_management"
    elif any(word in message_content.lower() for word in ["예약", "스케줄", "일정", "pt", "세션"]):
        return "schedule_management"
    elif any(word in message_content.lower() for word in ["알림", "메시지", "카카오"]):
        return "notification"
    elif any(word in message_content.lower() for word in ["상담", "문의", "질문", "안내"]):
        return "consultation"
    else:
        return "consultation"  # 기본값