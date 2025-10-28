"""
Domain Package

도메인 특화 코드

사용자가 이 디렉토리에 도메인별 코드를 추가합니다:
- agents/: 도메인별 Agent 구현
- tools/: 도메인별 Tool 구현
- intents.py: Intent 정의 (선택적)

Examples:
    # Tool 등록
    >>> from app.framework.tools import ToolRegistry
    >>> from app.domain.tools.my_tool import MyTool
    >>>
    >>> ToolRegistry.register(MyTool())

    # Agent 사용
    >>> from app.domain.agents.my_executor import MyExecutor
    >>>
    >>> executor = MyExecutor()
    >>> result = await executor.execute(shared_state)
"""

# 이 파일에 도메인 Tool 등록 코드를 추가할 수 있습니다
# from app.framework.tools import ToolRegistry
# from app.domain.tools.my_tool import MyTool
# ToolRegistry.register(MyTool())

__version__ = "1.0.0"
