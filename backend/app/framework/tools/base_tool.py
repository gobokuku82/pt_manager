"""
Base Tool - 모든 Tool의 추상 기본 클래스

범용 에이전트 프레임워크의 핵심 컴포넌트
모든 사용자 정의 Tool은 이 클래스를 상속받아 구현합니다.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """
    Tool 메타데이터

    Tool의 기본 정보를 정의합니다.
    """
    name: str = Field(..., description="Tool의 고유 이름")
    description: str = Field(..., description="Tool의 기능 설명")
    version: str = Field(default="1.0.0", description="Tool 버전")
    author: Optional[str] = Field(default=None, description="Tool 작성자")
    tags: List[str] = Field(default_factory=list, description="Tool 태그 (검색용)")
    input_schema: Optional[Dict[str, Any]] = Field(default=None, description="입력 스키마")
    output_schema: Optional[Dict[str, Any]] = Field(default=None, description="출력 스키마")


class BaseTool(ABC):
    """
    모든 Tool의 추상 기본 클래스

    사용자 정의 Tool은 이 클래스를 상속받아 구현합니다.

    Examples:
        >>> class MySearchTool(BaseTool):
        ...     @property
        ...     def metadata(self):
        ...         return ToolMetadata(
        ...             name="my_search",
        ...             description="검색 도구"
        ...         )
        ...
        ...     async def execute(self, query: str, **kwargs):
        ...         results = await self._search(query)
        ...         return {"results": results}
    """

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """
        Tool 메타데이터 반환

        Returns:
            ToolMetadata: Tool의 메타데이터
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Tool 실행 (비동기)

        Args:
            **kwargs: Tool별 실행 파라미터

        Returns:
            Dict[str, Any]: 실행 결과

        Raises:
            NotImplementedError: 하위 클래스에서 구현 필요
        """
        pass

    def validate_input(self, **kwargs) -> bool:
        """
        입력 검증 (선택적 override)

        Args:
            **kwargs: 검증할 입력 파라미터

        Returns:
            bool: 입력이 유효하면 True
        """
        return True

    async def pre_execute(self, **kwargs) -> Dict[str, Any]:
        """
        실행 전 처리 (선택적 override)

        Tool 실행 전에 수행할 작업을 정의합니다.
        예: 입력 정규화, 캐시 확인 등

        Args:
            **kwargs: 실행 파라미터

        Returns:
            Dict[str, Any]: 전처리된 파라미터
        """
        return kwargs

    async def post_execute(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        실행 후 처리 (선택적 override)

        Tool 실행 후에 수행할 작업을 정의합니다.
        예: 결과 포맷팅, 캐싱, 로깅 등

        Args:
            result: execute() 결과

        Returns:
            Dict[str, Any]: 후처리된 결과
        """
        return result

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Tool 실행 래퍼

        pre_execute → execute → post_execute 순서로 실행합니다.

        Args:
            **kwargs: 실행 파라미터

        Returns:
            Dict[str, Any]: 최종 결과
        """
        # 입력 검증
        if not self.validate_input(**kwargs):
            raise ValueError(f"Invalid input for tool '{self.metadata.name}'")

        # 전처리
        processed_kwargs = await self.pre_execute(**kwargs)

        # 실행
        result = await self.execute(**processed_kwargs)

        # 후처리
        final_result = await self.post_execute(result)

        return final_result

    def __repr__(self) -> str:
        """Tool 문자열 표현"""
        return f"<{self.__class__.__name__}(name='{self.metadata.name}', version='{self.metadata.version}')>"
