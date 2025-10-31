"""
Search Executor - 범용 정보 검색 에이전트

쿼리를 분석하여 적절한 검색 방법을 선택하고 실행합니다:
- Vector DB 검색: 의미 기반 검색 (임베딩, 유사도)
- Text2SQL: 정형 데이터베이스 검색 (SQL 쿼리 생성)
- 비정형 검색: 파일, API, 웹 등 비정형 데이터 검색
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.framework.agents.base.base_executor import BaseExecutor
from app.framework.tools.base_tool import BaseTool
from app.framework.tools.tool_registry import ToolRegistry
from app.framework.llm_manager import LLMService

logger = logging.getLogger(__name__)


class SearchExecutor(BaseExecutor):
    """
    범용 정보 검색 에이전트

    쿼리를 분석하여 다음 중 적절한 검색 방법을 선택합니다:
    1. Vector DB 검색: 의미 기반 검색 (문서, FAQ, 지식베이스 등)
    2. Text2SQL: 정형 DB 검색 (테이블 데이터, 통계 등)
    3. 비정형 검색: API, 파일, 웹 크롤링 등

    Examples:
        >>> executor = SearchExecutor(llm_context=llm_ctx)
        >>> result = await executor.execute(shared_state)
        >>> print(result['search_results'])
    """

    def __init__(self, llm_context=None, progress_callback=None):
        """
        초기화

        Args:
            llm_context: LLM 컨텍스트
            progress_callback: 진행 상황 콜백
        """
        # LLM Service 초기화
        self.llm_service = None
        if llm_context:
            try:
                self.llm_service = LLMService(llm_context=llm_context)
                logger.info("LLMService initialized in SearchExecutor")
            except Exception as e:
                logger.error(f"LLMService initialization failed: {e}")

        # BaseExecutor 초기화
        super().__init__(llm_context=llm_context, progress_callback=progress_callback)

        logger.info(f"SearchExecutor initialized with tools: {list(self.tools.keys())}")

    def _get_team_name(self) -> str:
        """팀 이름 반환"""
        return "search"

    def _register_tools(self) -> Dict[str, BaseTool]:
        """
        검색 도구 등록

        Returns:
            Dict[str, BaseTool]: 등록된 검색 도구들
        """
        tools = {}

        # Vector DB 검색 도구
        vector_tool = ToolRegistry.get("vector_search")
        if vector_tool:
            tools["vector_search"] = vector_tool
            logger.info("Registered vector_search tool")

        # Text2SQL 도구
        sql_tool = ToolRegistry.get("text2sql")
        if sql_tool:
            tools["text2sql"] = sql_tool
            logger.info("Registered text2sql tool")

        # 비정형 검색 도구
        unstructured_tool = ToolRegistry.get("unstructured_search")
        if unstructured_tool:
            tools["unstructured_search"] = unstructured_tool
            logger.info("Registered unstructured_search tool")

        if not tools:
            logger.warning("No search tools registered in ToolRegistry")

        return tools

    async def execute(self, shared_state: Any, **kwargs) -> Dict[str, Any]:
        """
        검색 실행

        워크플로우:
        1. 쿼리 분석 (Step 0)
        2. 검색 타입 결정 (LLM)
        3. 병렬 검색 실행 (Step 1)
        4. 결과 필터링 및 랭킹 (Step 2)
        5. 결과 통합 (Step 3)

        Args:
            shared_state: 공유 상태 (query 포함)
            **kwargs: 추가 파라미터
                - search_types: Optional[List[str]] - 강제 지정할 검색 타입
                - limit: Optional[int] - 결과 개수 제한

        Returns:
            Dict[str, Any]: {
                "status": "completed" | "failed",
                "search_results": List[Dict],
                "total_results": int,
                "search_types_used": List[str],
                "execution_time": float
            }
        """
        start_time = datetime.now()

        # 쿼리 추출
        query = shared_state.get("query") or shared_state.get("user_query", "")
        if not query:
            logger.warning("No query provided in shared_state")
            return {
                "status": "failed",
                "error": "No query provided",
                "search_results": [],
                "total_results": 0
            }

        logger.info(f"[SearchExecutor] Starting search for query: {query[:100]}...")

        try:
            # Step 0: 쿼리 분석
            await self.send_step_start(0, "쿼리 분석")
            analysis = await self._analyze_query(query, shared_state)
            await self.send_step_complete(0, "쿼리 분석")

            # 검색 타입 결정 (kwargs로 강제 지정 가능)
            search_types = kwargs.get("search_types") or analysis.get("search_types", [])

            if not search_types:
                logger.warning("No search types determined, using all available")
                search_types = list(self.tools.keys())

            logger.info(f"[SearchExecutor] Selected search types: {search_types}")

            # Step 1: 병렬 검색 실행
            await self.send_step_start(1, "데이터 검색")
            search_results = await self._execute_searches(query, search_types, shared_state)
            await self.send_step_complete(1, "데이터 검색")

            # Step 2: 결과 필터링 및 랭킹
            await self.send_step_start(2, "결과 필터링")
            filtered_results = await self._filter_and_rank(search_results, analysis)
            await self.send_step_complete(2, "결과 필터링")

            # Step 3: 결과 통합
            await self.send_step_start(3, "결과 통합")
            final_results = await self._aggregate_results(filtered_results)
            await self.send_step_complete(3, "결과 통합")

            # 결과 제한
            limit = kwargs.get("limit", 50)
            if len(final_results) > limit:
                final_results = final_results[:limit]

            execution_time = (datetime.now() - start_time).total_seconds()

            logger.info(
                f"[SearchExecutor] Completed: {len(final_results)} results "
                f"from {len(search_types)} search types in {execution_time:.2f}s"
            )

            return {
                "status": "completed",
                "search_results": final_results,
                "total_results": len(final_results),
                "search_types_used": search_types,
                "execution_time": execution_time,
                "analysis": analysis
            }

        except Exception as e:
            logger.error(f"[SearchExecutor] Failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "search_results": [],
                "total_results": 0
            }

    async def _analyze_query(
        self,
        query: str,
        shared_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        쿼리 분석 및 검색 타입 결정

        LLM을 사용하여 쿼리를 분석하고 어떤 검색 방법이 적절한지 결정합니다.

        Args:
            query: 사용자 쿼리
            shared_state: 공유 상태 (context 포함)

        Returns:
            Dict[str, Any]: {
                "search_types": ["vector_search", "text2sql"],
                "reasoning": "...",
                "keywords": [...],
                "entities": {...}
            }
        """
        if not self.llm_service:
            # Fallback: 모든 검색 타입 사용
            logger.warning("No LLM service, using all search types")
            return {
                "search_types": list(self.tools.keys()),
                "reasoning": "Fallback: no LLM available",
                "keywords": [],
                "entities": {}
            }

        try:
            # LLM 기반 쿼리 분석
            result = await self.llm_service.complete_json_async(
                prompt_name="search_type_selection",
                variables={
                    "query": query,
                    "available_search_types": {
                        "vector_search": "의미 기반 검색 (문서, FAQ, 지식베이스)",
                        "text2sql": "정형 데이터베이스 검색 (통계, 테이블 데이터)",
                        "unstructured_search": "비정형 데이터 검색 (API, 파일, 웹)"
                    }
                },
                temperature=0.1
            )

            logger.info(f"[SearchExecutor] Query analysis: {result}")

            return {
                "search_types": result.get("search_types", []),
                "reasoning": result.get("reasoning", ""),
                "keywords": result.get("keywords", []),
                "entities": result.get("entities", {})
            }

        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            # Fallback
            return {
                "search_types": list(self.tools.keys()),
                "reasoning": f"Fallback due to error: {str(e)}",
                "keywords": [],
                "entities": {}
            }

    async def _execute_searches(
        self,
        query: str,
        search_types: List[str],
        shared_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        병렬 검색 실행

        Args:
            query: 검색 쿼리
            search_types: 사용할 검색 타입 목록
            shared_state: 공유 상태

        Returns:
            Dict[str, Any]: {
                "vector_search": [...],
                "text2sql": [...],
                "unstructured_search": [...]
            }
        """
        results = {}

        # 병렬 실행을 위한 태스크 생성
        tasks = []
        task_names = []

        for search_type in search_types:
            tool = self.tools.get(search_type)
            if tool:
                task = self._execute_single_search(search_type, tool, query, shared_state)
                tasks.append(task)
                task_names.append(search_type)
            else:
                logger.warning(f"Tool '{search_type}' not found, skipping")

        # 병렬 실행
        if tasks:
            search_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 결과 매핑
            for task_name, result in zip(task_names, search_results):
                if isinstance(result, Exception):
                    logger.error(f"Search '{task_name}' failed: {result}")
                    results[task_name] = []
                else:
                    results[task_name] = result

        return results

    async def _execute_single_search(
        self,
        search_type: str,
        tool: BaseTool,
        query: str,
        shared_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        단일 검색 실행

        Args:
            search_type: 검색 타입 이름
            tool: 사용할 도구
            query: 검색 쿼리
            shared_state: 공유 상태

        Returns:
            List[Dict[str, Any]]: 검색 결과
        """
        try:
            logger.info(f"[SearchExecutor] Executing {search_type} search")

            # Tool 실행
            result = await tool.execute(
                query=query,
                context=shared_state
            )

            if result.get("status") == "success":
                data = result.get("data", [])
                logger.info(f"[SearchExecutor] {search_type} returned {len(data)} results")
                return data
            else:
                logger.warning(f"[SearchExecutor] {search_type} returned status: {result.get('status')}")
                return []

        except Exception as e:
            logger.error(f"[SearchExecutor] {search_type} failed: {e}")
            return []

    async def _filter_and_rank(
        self,
        search_results: Dict[str, List[Dict[str, Any]]],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        검색 결과 필터링 및 랭킹

        Args:
            search_results: 검색 타입별 결과
            analysis: 쿼리 분석 결과

        Returns:
            List[Dict[str, Any]]: 필터링 및 랭킹된 결과
        """
        all_results = []

        # 모든 검색 결과 수집 (출처 표시)
        for search_type, results in search_results.items():
            for result in results:
                # 결과에 출처 추가
                result["search_type"] = search_type
                all_results.append(result)

        # TODO: 향후 LLM 기반 랭킹 추가
        # - Relevance scoring
        # - Deduplication
        # - Quality filtering

        logger.info(f"[SearchExecutor] Collected {len(all_results)} total results")

        return all_results

    async def _aggregate_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        최종 결과 통합 및 정리

        Args:
            results: 필터링된 결과 목록

        Returns:
            List[Dict[str, Any]]: 최종 통합 결과
        """
        # 현재는 단순 반환, 향후 확장 가능:
        # - 중복 제거
        # - 스코어 정규화
        # - 결과 그룹핑

        return results


# 사용 예시
if __name__ == "__main__":
    async def test_search_executor():
        """SearchExecutor 테스트"""

        # Executor 초기화
        executor = SearchExecutor()

        # 테스트 쿼리
        test_queries = [
            "사용자 인증 관련 문서 찾아줘",
            "지난 달 매출 통계 알려줘",
            "최신 API 문서 검색"
        ]

        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print("-"*60)

            # 공유 상태 생성
            shared_state = {
                "query": query,
                "session_id": "test_session"
            }

            # 실행
            result = await executor.execute(shared_state)

            print(f"Status: {result['status']}")
            print(f"Total results: {result['total_results']}")
            print(f"Search types used: {result.get('search_types_used', [])}")
            print(f"Execution time: {result.get('execution_time', 0):.2f}s")

    import asyncio
    asyncio.run(test_search_executor())
