"""
Tool Registry - Tool 등록 및 관리 시스템

범용 에이전트 프레임워크의 핵심 컴포넌트
모든 Tool을 중앙에서 등록하고 관리합니다.
"""

from typing import Dict, List, Optional
from app.framework.tools.base_tool import BaseTool, ToolMetadata
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Tool 등록 및 관리 (싱글톤 패턴)

    모든 Tool을 중앙에서 관리하며, Agent에서 Tool을 조회할 수 있습니다.

    Examples:
        >>> # Tool 등록
        >>> tool = MySearchTool()
        >>> ToolRegistry.register(tool)

        >>> # Tool 조회
        >>> search_tool = ToolRegistry.get("my_search")
        >>> result = await search_tool.execute(query="test")

        >>> # Tool 목록
        >>> all_tools = ToolRegistry.list_tools()

        >>> # 태그로 검색
        >>> search_tools = ToolRegistry.search_by_tag("search")
    """

    # 싱글톤 저장소
    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        """
        Tool 등록

        Args:
            tool: 등록할 Tool 인스턴스

        Raises:
            ValueError: Tool 메타데이터가 유효하지 않은 경우
        """
        if not isinstance(tool, BaseTool):
            raise ValueError(f"Tool must inherit from BaseTool, got {type(tool)}")

        name = tool.metadata.name

        if not name:
            raise ValueError("Tool name cannot be empty")

        if name in cls._tools:
            logger.warning(f"Tool '{name}' already registered, overwriting")

        cls._tools[name] = tool
        logger.info(f"Tool registered: {name} v{tool.metadata.version}")

    @classmethod
    def unregister(cls, name: str) -> bool:
        """
        Tool 등록 해제

        Args:
            name: 제거할 Tool 이름

        Returns:
            bool: 제거 성공 여부
        """
        if name in cls._tools:
            del cls._tools[name]
            logger.info(f"Tool unregistered: {name}")
            return True

        logger.warning(f"Tool '{name}' not found for unregistration")
        return False

    @classmethod
    def get(cls, name: str) -> Optional[BaseTool]:
        """
        Tool 조회

        Args:
            name: 조회할 Tool 이름

        Returns:
            Optional[BaseTool]: Tool 인스턴스 (없으면 None)
        """
        tool = cls._tools.get(name)

        if tool is None:
            logger.warning(f"Tool '{name}' not found in registry")

        return tool

    @classmethod
    def list_tools(cls) -> List[ToolMetadata]:
        """
        등록된 Tool 목록 조회

        Returns:
            List[ToolMetadata]: 등록된 Tool의 메타데이터 리스트
        """
        return [tool.metadata for tool in cls._tools.values()]

    @classmethod
    def search_by_tag(cls, tag: str) -> List[BaseTool]:
        """
        태그로 Tool 검색

        Args:
            tag: 검색할 태그

        Returns:
            List[BaseTool]: 태그를 가진 Tool 리스트
        """
        return [
            tool for tool in cls._tools.values()
            if tag in tool.metadata.tags
        ]

    @classmethod
    def search_by_name_pattern(cls, pattern: str) -> List[BaseTool]:
        """
        이름 패턴으로 Tool 검색

        Args:
            pattern: 검색 패턴 (부분 일치)

        Returns:
            List[BaseTool]: 패턴과 일치하는 Tool 리스트
        """
        return [
            tool for tool in cls._tools.values()
            if pattern.lower() in tool.metadata.name.lower()
        ]

    @classmethod
    def get_by_author(cls, author: str) -> List[BaseTool]:
        """
        작성자로 Tool 검색

        Args:
            author: 작성자 이름

        Returns:
            List[BaseTool]: 해당 작성자의 Tool 리스트
        """
        return [
            tool for tool in cls._tools.values()
            if tool.metadata.author == author
        ]

    @classmethod
    def clear(cls) -> int:
        """
        모든 Tool 제거 (주로 테스트용)

        Returns:
            int: 제거된 Tool 개수
        """
        count = len(cls._tools)
        cls._tools.clear()
        logger.info(f"All tools cleared ({count} tools)")
        return count

    @classmethod
    def count(cls) -> int:
        """
        등록된 Tool 개수

        Returns:
            int: Tool 개수
        """
        return len(cls._tools)

    @classmethod
    def has_tool(cls, name: str) -> bool:
        """
        Tool 존재 여부 확인

        Args:
            name: 확인할 Tool 이름

        Returns:
            bool: Tool 존재 여부
        """
        return name in cls._tools

    @classmethod
    def get_all_tool_names(cls) -> List[str]:
        """
        모든 Tool 이름 목록

        Returns:
            List[str]: Tool 이름 리스트
        """
        return list(cls._tools.keys())

    @classmethod
    def print_registry(cls) -> None:
        """
        등록된 Tool 목록 출력 (디버깅용)
        """
        print(f"\n=== Tool Registry ({cls.count()} tools) ===")

        if not cls._tools:
            print("  (No tools registered)")
            return

        for tool in cls._tools.values():
            meta = tool.metadata
            tags_str = f" [{', '.join(meta.tags)}]" if meta.tags else ""
            print(f"  - {meta.name} v{meta.version}{tags_str}")
            print(f"    {meta.description}")

        print()


# Singleton instance accessor (optional)
def get_tool_registry() -> ToolRegistry:
    """
    ToolRegistry 인스턴스 접근 (편의 함수)

    Returns:
        ToolRegistry: ToolRegistry 클래스
    """
    return ToolRegistry
