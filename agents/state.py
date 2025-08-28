from typing import TypedDict, List, Optional, Annotated, Sequence
from langgraph.graph import add_messages

class AgentState(TypedDict):
    messages: Annotated[Sequence, add_messages]
    current_member: Optional[dict]
    search_results: Optional[List[dict]]
    action_type: Optional[str]
    action_result: Optional[dict]
    kakao_message: Optional[dict]
    error: Optional[str]