"""
Base Executor - 모든 Executor의 추상 기본 클래스

범용 에이전트 프레임워크의 핵심 컴포넌트
모든 Execution Agent는 이 클래스를 상속받아 구현합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable
from app.framework.tools.base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)


class BaseExecutor(ABC):
    """
    모든 Executor의 추상 기본 클래스

    Executor는 특정 작업(검색, 분석, 문서 생성 등)을 실행하는 Agent입니다.
    템플릿 메서드 패턴을 사용하여 실행 워크플로우를 정의합니다.

    Examples:
        >>> class MySearchExecutor(BaseExecutor):
        ...     def _get_team_name(self):
        ...         return "search"
        ...
        ...     def _register_tools(self):
        ...         return {
        ...             "search": ToolRegistry.get("search_tool")
        ...         }
        ...
        ...     async def execute(self, shared_state, **kwargs):
        ...         # 검색 로직
        ...         keywords = await self._extract_keywords(shared_state.query)
        ...         results = await self.tools["search"].execute(keywords=keywords)
        ...         return results
    """

    def __init__(
        self,
        llm_context=None,
        progress_callback: Optional[Callable[[str, dict], Awaitable[None]]] = None
    ):
        """
        Executor 초기화

        Args:
            llm_context: LLM 컨텍스트 (선택적)
            progress_callback: 진행 상황 콜백 함수 (선택적)
                - 시그니처: async def callback(event_type: str, data: dict)
        """
        self.llm_context = llm_context
        self.progress_callback = progress_callback

        # Tool 등록
        self.tools = self._register_tools()

        # 팀 이름
        self.team_name = self._get_team_name()

        logger.info(f"Executor initialized: {self.team_name} (tools: {list(self.tools.keys())})")

    @abstractmethod
    def _get_team_name(self) -> str:
        """
        팀 이름 반환

        Returns:
            str: 팀 이름 (예: "search", "analysis", "document")
        """
        pass

    @abstractmethod
    def _register_tools(self) -> Dict[str, BaseTool]:
        """
        사용할 Tool 등록

        Returns:
            Dict[str, BaseTool]: Tool 이름 → Tool 인스턴스 매핑

        Examples:
            >>> def _register_tools(self):
            ...     return {
            ...         "search": ToolRegistry.get("search_tool"),
            ...         "filter": ToolRegistry.get("filter_tool")
            ...     }
        """
        pass

    @abstractmethod
    async def execute(self, shared_state: Any, **kwargs) -> Dict[str, Any]:
        """
        실행 로직 (하위 클래스에서 구현)

        Args:
            shared_state: 공유 상태 (SharedState 등)
            **kwargs: 추가 파라미터

        Returns:
            Dict[str, Any]: 실행 결과

        Raises:
            NotImplementedError: 하위 클래스에서 구현 필요
        """
        pass

    async def send_progress(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        진행 상황 전송 (WebSocket 등)

        Args:
            event_type: 이벤트 타입 (예: "agent_step_progress")
            data: 이벤트 데이터

        Examples:
            >>> await self.send_progress("agent_step_progress", {
            ...     "agentName": "search",
            ...     "stepIndex": 0,
            ...     "status": "in_progress",
            ...     "progress": 50
            ... })
        """
        if self.progress_callback:
            try:
                await self.progress_callback(event_type, data)
            except Exception as e:
                logger.error(f"Failed to send progress: {e}")

    async def send_step_start(self, step_index: int, step_name: str) -> None:
        """
        단계 시작 알림 (편의 메서드)

        Args:
            step_index: 단계 인덱스
            step_name: 단계 이름
        """
        await self.send_progress("agent_step_progress", {
            "agentName": self.team_name,
            "stepIndex": step_index,
            "stepName": step_name,
            "status": "in_progress",
            "progress": 0
        })

    async def send_step_complete(self, step_index: int, step_name: str) -> None:
        """
        단계 완료 알림 (편의 메서드)

        Args:
            step_index: 단계 인덱스
            step_name: 단계 이름
        """
        await self.send_progress("agent_step_progress", {
            "agentName": self.team_name,
            "stepIndex": step_index,
            "stepName": step_name,
            "status": "completed",
            "progress": 100
        })

    async def send_step_error(self, step_index: int, step_name: str, error: str) -> None:
        """
        단계 오류 알림 (편의 메서드)

        Args:
            step_index: 단계 인덱스
            step_name: 단계 이름
            error: 오류 메시지
        """
        await self.send_progress("agent_step_progress", {
            "agentName": self.team_name,
            "stepIndex": step_index,
            "stepName": step_name,
            "status": "error",
            "error": error
        })

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        등록된 Tool 조회

        Args:
            name: Tool 이름

        Returns:
            Optional[BaseTool]: Tool 인스턴스 (없으면 None)
        """
        tool = self.tools.get(name)

        if tool is None:
            logger.warning(f"Tool '{name}' not found in executor '{self.team_name}'")

        return tool

    async def pre_execute(self, shared_state: Any, **kwargs) -> Dict[str, Any]:
        """
        실행 전 처리 (선택적 override)

        Args:
            shared_state: 공유 상태
            **kwargs: 추가 파라미터

        Returns:
            Dict[str, Any]: 전처리된 파라미터
        """
        return kwargs

    async def post_execute(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        실행 후 처리 (선택적 override)

        Args:
            result: execute() 결과

        Returns:
            Dict[str, Any]: 후처리된 결과
        """
        return result

    async def __call__(self, shared_state: Any, **kwargs) -> Dict[str, Any]:
        """
        Executor 실행 래퍼

        pre_execute → execute → post_execute 순서로 실행합니다.

        Args:
            shared_state: 공유 상태
            **kwargs: 추가 파라미터

        Returns:
            Dict[str, Any]: 최종 결과
        """
        try:
            logger.info(f"Executing {self.team_name} executor")

            # 전처리
            processed_kwargs = await self.pre_execute(shared_state, **kwargs)

            # 실행
            result = await self.execute(shared_state, **processed_kwargs)

            # 후처리
            final_result = await self.post_execute(result)

            logger.info(f"Executor {self.team_name} completed successfully")
            return final_result

        except Exception as e:
            logger.error(f"Executor {self.team_name} failed: {e}", exc_info=True)
            raise

    def __repr__(self) -> str:
        """Executor 문자열 표현"""
        return f"<{self.__class__.__name__}(team='{self.team_name}', tools={list(self.tools.keys())})>"
