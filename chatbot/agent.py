"""
LangGraph 기반 PT Manager 에이전트
"""

from typing import TypedDict, Annotated, List, Union, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import streamlit as st
from datetime import datetime
import json

from .tools import get_tools
from .prompts import SYSTEM_PROMPT

# 상태 정의
class AgentState(TypedDict):
    """에이전트 상태"""
    messages: Annotated[List[BaseMessage], "대화 메시지"]
    current_action: Optional[str]
    action_result: Optional[Dict[str, Any]]
    next_step: Optional[str]

class PTManagerAgent:
    """PT Manager 메인 에이전트"""
    
    def __init__(self):
        """에이전트 초기화"""
        self.llm = self._create_llm()
        self.tools = get_tools()
        self.graph = self._create_graph()
    
    def _create_llm(self):
        """LLM 인스턴스 생성"""
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=st.secrets.get("OPENAI_API_KEY")
        )
    
    def _create_graph(self):
        """LangGraph 워크플로우 생성"""
        # 상태 그래프 생성
        workflow = StateGraph(AgentState)
        
        # 노드 추가
        workflow.add_node("analyze", self.analyze_request)
        workflow.add_node("execute_action", self.execute_action)
        workflow.add_node("generate_response", self.generate_response)
        
        # 엣지 추가
        workflow.set_entry_point("analyze")
        
        workflow.add_conditional_edges(
            "analyze",
            self.route_after_analysis,
            {
                "execute": "execute_action",
                "respond": "generate_response",
                "end": END
            }
        )
        
        workflow.add_edge("execute_action", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def analyze_request(self, state: AgentState) -> AgentState:
        """사용자 요청 분석"""
        messages = state["messages"]
        last_message = messages[-1] if messages else None
        
        if not last_message:
            return state
        
        # 의도 분석
        analysis_prompt = f"""
        사용자 메시지를 분석하고 적절한 작업을 결정하세요.
        
        사용자: {last_message.content}
        
        가능한 작업:
        1. search_member - 회원 검색
        2. create_member - 회원 등록
        3. update_member - 회원 정보 수정
        4. create_schedule - PT 예약
        5. view_schedule - 일정 조회
        6. create_contract - 계약서 생성
        7. send_message - 메시지 전송
        8. general_response - 일반 대화
        
        작업을 JSON 형식으로 반환하세요:
        {{"action": "작업명", "parameters": {{...}}}}
        """
        
        response = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ])
        
        try:
            result = json.loads(response.content)
            state["current_action"] = result.get("action", "general_response")
            state["action_result"] = result.get("parameters", {})
        except:
            state["current_action"] = "general_response"
            state["action_result"] = {}
        
        return state
    
    def route_after_analysis(self, state: AgentState) -> str:
        """분석 후 라우팅"""
        action = state.get("current_action", "")
        
        if action in ["search_member", "create_member", "update_member", 
                     "create_schedule", "view_schedule", "create_contract", 
                     "send_message"]:
            return "execute"
        elif action == "general_response":
            return "respond"
        else:
            return "end"
    
    def execute_action(self, state: AgentState) -> AgentState:
        """작업 실행"""
        action = state.get("current_action")
        parameters = state.get("action_result", {})
        
        # 도구 실행 (실제 구현 필요)
        result = self._execute_tool(action, parameters)
        
        state["action_result"] = result
        return state
    
    def _execute_tool(self, action: str, parameters: Dict) -> Dict:
        """도구 실행 (구현 필요)"""
        from database.gsheets import GoogleSheetsDB
        
        try:
            db = GoogleSheetsDB()
            
            if action == "search_member":
                query = parameters.get("query", "")
                members = db.search_members(query)
                return {"success": True, "data": members}
            
            elif action == "create_member":
                member = db.create_member(parameters)
                return {"success": True, "data": member}
            
            elif action == "view_schedule":
                date = parameters.get("date", datetime.now().strftime("%Y-%m-%d"))
                schedules = db.get_schedules_by_date(date)
                return {"success": True, "data": schedules}
            
            elif action == "create_schedule":
                schedule = db.create_schedule(parameters)
                return {"success": True, "data": schedule}
            
            elif action == "create_contract":
                contract = db.create_contract(parameters)
                return {"success": True, "data": contract}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_response(self, state: AgentState) -> AgentState:
        """응답 생성"""
        messages = state["messages"]
        action = state.get("current_action")
        result = state.get("action_result", {})
        
        # 컨텍스트 구성
        context = f"""
        수행한 작업: {action}
        결과: {json.dumps(result, ensure_ascii=False)}
        """
        
        # 응답 생성
        response_prompt = f"""
        사용자의 요청에 대한 친절하고 자연스러운 응답을 생성하세요.
        
        {context}
        
        간결하고 명확하게 답변하세요.
        """
        
        response = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=response_prompt)
        ])
        
        # 응답 메시지 추가
        messages.append(AIMessage(content=response.content))
        state["messages"] = messages
        
        return state
    
    def invoke(self, message: str) -> str:
        """메시지 처리"""
        # 초기 상태 생성
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "current_action": None,
            "action_result": None,
            "next_step": None
        }
        
        # 그래프 실행
        result = self.graph.invoke(initial_state)
        
        # 마지막 AI 메시지 반환
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage):
                return msg.content
        
        return "죄송합니다. 응답을 생성할 수 없습니다."
    
    def stream(self, message: str):
        """스트리밍 응답"""
        # 초기 상태 생성
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "current_action": None,
            "action_result": None,
            "next_step": None
        }
        
        # 그래프 스트리밍 실행
        for event in self.graph.stream(initial_state):
            yield event

# 싱글톤 인스턴스
@st.cache_resource
def get_agent():
    """에이전트 인스턴스 반환"""
    return PTManagerAgent()