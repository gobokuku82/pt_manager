from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.main_agent import (
    member_management_node,
    consultation_node,
    schedule_management_node,
    notification_node,
    router
)

def create_agent_graph():
    """LangGraph 에이전트 그래프 생성"""
    
    # 그래프 초기화
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("member_management", member_management_node)
    workflow.add_node("consultation", consultation_node)
    workflow.add_node("schedule_management", schedule_management_node)
    workflow.add_node("notification", notification_node)
    
    # 조건부 엣지 추가 - 라우터를 통해 다음 노드 결정
    workflow.add_conditional_edges(
        "member_management",
        router,
        {
            "consultation": "consultation",
            "schedule_management": "schedule_management",
            "notification": "notification",
            "member_management": "member_management",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "consultation",
        router,
        {
            "member_management": "member_management",
            "schedule_management": "schedule_management",
            "notification": "notification",
            "consultation": "consultation",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "schedule_management",
        router,
        {
            "member_management": "member_management",
            "consultation": "consultation",
            "notification": "notification",
            "schedule_management": "schedule_management",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "notification",
        lambda x: "end",  # 알림 노드는 항상 종료
        {
            "end": END
        }
    )
    
    # 시작점 설정 - 라우터로 시작
    workflow.set_conditional_entry_point(
        router,
        {
            "member_management": "member_management",
            "consultation": "consultation",
            "schedule_management": "schedule_management",
            "notification": "notification",
            "end": END
        }
    )
    
    # 그래프 컴파일
    app = workflow.compile()
    
    return app

# 전역 그래프 인스턴스
agent_graph = create_agent_graph()