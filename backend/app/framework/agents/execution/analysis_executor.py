"""
Analysis Executor - 범용 데이터 분석 에이전트

수집된 데이터를 분석하여 인사이트와 추천사항을 생성합니다:
- 통계 분석: 평균, 중앙값, 트렌드, 분포
- 비교 분석: A vs B 비교, 다중 항목 비교
- 패턴 인식: 이상치 탐지, 시계열 패턴
- 인사이트 생성: LLM 기반 통찰력 도출
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


class AnalysisExecutor(BaseExecutor):
    """
    범용 데이터 분석 에이전트

    수집된 데이터를 분석하여 다음을 수행합니다:
    1. 통계 분석: 기술 통계, 트렌드 분석
    2. 비교 분석: 다중 데이터셋 비교
    3. 패턴 인식: 이상치, 클러스터링
    4. 인사이트 생성: LLM 기반 해석

    Examples:
        >>> executor = AnalysisExecutor(llm_context=llm_ctx)
        >>> result = await executor.execute(shared_state, input_data={...})
        >>> print(result['insights'])
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
                logger.info("LLMService initialized in AnalysisExecutor")
            except Exception as e:
                logger.error(f"LLMService initialization failed: {e}")

        # BaseExecutor 초기화
        super().__init__(llm_context=llm_context, progress_callback=progress_callback)

        logger.info(f"AnalysisExecutor initialized with tools: {list(self.tools.keys())}")

    def _get_team_name(self) -> str:
        """팀 이름 반환"""
        return "analysis"

    def _register_tools(self) -> Dict[str, BaseTool]:
        """
        분석 도구 등록

        Returns:
            Dict[str, BaseTool]: 등록된 분석 도구들
        """
        tools = {}

        # 통계 분석 도구
        stats_tool = ToolRegistry.get("statistical_analysis")
        if stats_tool:
            tools["statistical_analysis"] = stats_tool
            logger.info("Registered statistical_analysis tool")

        # 비교 분석 도구
        comparison_tool = ToolRegistry.get("comparison_analysis")
        if comparison_tool:
            tools["comparison_analysis"] = comparison_tool
            logger.info("Registered comparison_analysis tool")

        # 패턴 인식 도구
        pattern_tool = ToolRegistry.get("pattern_recognition")
        if pattern_tool:
            tools["pattern_recognition"] = pattern_tool
            logger.info("Registered pattern_recognition tool")

        if not tools:
            logger.warning("No analysis tools registered in ToolRegistry")

        return tools

    async def execute(self, shared_state: Any, **kwargs) -> Dict[str, Any]:
        """
        데이터 분석 실행

        워크플로우:
        1. 데이터 전처리 (Step 0)
        2. 통계 분석 (Step 1)
        3. 패턴 인식 (Step 2)
        4. 인사이트 생성 (Step 3)
        5. 보고서 작성 (Step 4)

        Args:
            shared_state: 공유 상태
            **kwargs: 추가 파라미터
                - input_data: Dict[str, Any] - 분석할 데이터
                - analysis_type: str - 분석 타입 ("statistical", "comparison", "comprehensive")

        Returns:
            Dict[str, Any]: {
                "status": "completed" | "failed",
                "insights": List[Dict],
                "metrics": Dict,
                "report": str,
                "execution_time": float
            }
        """
        start_time = datetime.now()

        # 입력 데이터 추출
        input_data = kwargs.get("input_data", {})
        analysis_type = kwargs.get("analysis_type", "comprehensive")

        if not input_data:
            logger.warning("No input data provided")
            return {
                "status": "failed",
                "error": "No input data provided",
                "insights": [],
                "metrics": {}
            }

        query = shared_state.get("query") or shared_state.get("user_query", "")
        logger.info(f"[AnalysisExecutor] Starting {analysis_type} analysis")

        try:
            # Step 0: 데이터 전처리
            await self.send_step_start(0, "데이터 전처리")
            preprocessed_data = await self._preprocess_data(input_data)
            await self.send_step_complete(0, "데이터 전처리")

            # Step 1: 통계 분석
            await self.send_step_start(1, "통계 분석")
            stats_results = await self._perform_statistical_analysis(preprocessed_data, analysis_type)
            await self.send_step_complete(1, "통계 분석")

            # Step 2: 패턴 인식
            await self.send_step_start(2, "패턴 인식")
            pattern_results = await self._perform_pattern_recognition(preprocessed_data, analysis_type)
            await self.send_step_complete(2, "패턴 인식")

            # Step 3: 인사이트 생성
            await self.send_step_start(3, "인사이트 생성")
            insights = await self._generate_insights(
                query=query,
                stats_results=stats_results,
                pattern_results=pattern_results,
                preprocessed_data=preprocessed_data
            )
            await self.send_step_complete(3, "인사이트 생성")

            # Step 4: 보고서 작성
            await self.send_step_start(4, "보고서 작성")
            report = await self._create_report(
                analysis_type=analysis_type,
                insights=insights,
                stats_results=stats_results,
                pattern_results=pattern_results
            )
            await self.send_step_complete(4, "보고서 작성")

            execution_time = (datetime.now() - start_time).total_seconds()

            logger.info(
                f"[AnalysisExecutor] Completed: {len(insights)} insights "
                f"in {execution_time:.2f}s"
            )

            return {
                "status": "completed",
                "insights": insights,
                "metrics": stats_results.get("metrics", {}),
                "patterns": pattern_results.get("patterns", []),
                "report": report,
                "execution_time": execution_time,
                "analysis_type": analysis_type
            }

        except Exception as e:
            logger.error(f"[AnalysisExecutor] Failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "insights": [],
                "metrics": {}
            }

    async def _preprocess_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터 전처리

        Args:
            input_data: 원본 입력 데이터

        Returns:
            Dict[str, Any]: 전처리된 데이터
        """
        logger.info("[AnalysisExecutor] Preprocessing data")

        preprocessed = {}

        for source, data in input_data.items():
            # 데이터 정제
            if isinstance(data, list):
                # 리스트 데이터는 그대로
                preprocessed[source] = data
            elif isinstance(data, dict):
                # 딕셔너리 데이터도 그대로
                preprocessed[source] = data
            else:
                # 기타 타입은 래핑
                preprocessed[source] = {"value": data}

        logger.info(f"[AnalysisExecutor] Preprocessed {len(preprocessed)} data sources")

        return preprocessed

    async def _perform_statistical_analysis(
        self,
        data: Dict[str, Any],
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        통계 분석 수행

        Args:
            data: 전처리된 데이터
            analysis_type: 분석 타입

        Returns:
            Dict[str, Any]: 통계 분석 결과
        """
        logger.info("[AnalysisExecutor] Performing statistical analysis")

        # Tool이 있으면 사용
        stats_tool = self.tools.get("statistical_analysis")
        if stats_tool:
            try:
                result = await stats_tool.execute(
                    data=data,
                    analysis_type=analysis_type
                )
                if result.get("status") == "success":
                    return result.get("data", {})
            except Exception as e:
                logger.error(f"Statistical analysis tool failed: {e}")

        # Fallback: 기본 통계
        return {
            "metrics": {
                "data_sources": len(data),
                "total_records": sum(len(v) if isinstance(v, list) else 1 for v in data.values())
            },
            "status": "basic_stats"
        }

    async def _perform_pattern_recognition(
        self,
        data: Dict[str, Any],
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        패턴 인식 수행

        Args:
            data: 전처리된 데이터
            analysis_type: 분석 타입

        Returns:
            Dict[str, Any]: 패턴 인식 결과
        """
        logger.info("[AnalysisExecutor] Performing pattern recognition")

        # Tool이 있으면 사용
        pattern_tool = self.tools.get("pattern_recognition")
        if pattern_tool:
            try:
                result = await pattern_tool.execute(
                    data=data,
                    analysis_type=analysis_type
                )
                if result.get("status") == "success":
                    return result.get("data", {})
            except Exception as e:
                logger.error(f"Pattern recognition tool failed: {e}")

        # Fallback: 기본 패턴
        return {
            "patterns": [],
            "status": "no_patterns"
        }

    async def _generate_insights(
        self,
        query: str,
        stats_results: Dict[str, Any],
        pattern_results: Dict[str, Any],
        preprocessed_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        인사이트 생성 (LLM 기반)

        Args:
            query: 사용자 쿼리
            stats_results: 통계 분석 결과
            pattern_results: 패턴 인식 결과
            preprocessed_data: 전처리된 데이터

        Returns:
            List[Dict[str, Any]]: 인사이트 목록
        """
        logger.info("[AnalysisExecutor] Generating insights")

        if not self.llm_service:
            # Fallback: 기본 인사이트
            logger.warning("No LLM service, using basic insights")
            return [
                {
                    "type": "summary",
                    "content": f"분석 완료: {stats_results.get('metrics', {}).get('data_sources', 0)}개 데이터 소스",
                    "confidence": 0.5
                }
            ]

        try:
            # LLM 기반 인사이트 생성
            result = await self.llm_service.complete_json_async(
                prompt_name="insight_generation",
                variables={
                    "query": query,
                    "stats_results": str(stats_results),
                    "pattern_results": str(pattern_results),
                    "data_summary": self._summarize_data(preprocessed_data)
                },
                temperature=0.3
            )

            logger.info(f"[AnalysisExecutor] Generated {len(result.get('insights', []))} insights")

            return result.get("insights", [])

        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            # Fallback
            return [
                {
                    "type": "error",
                    "content": f"인사이트 생성 실패: {str(e)}",
                    "confidence": 0.0
                }
            ]

    def _summarize_data(self, data: Dict[str, Any]) -> str:
        """
        데이터 요약 생성

        Args:
            data: 데이터

        Returns:
            str: 요약 문자열
        """
        summary_parts = []

        for source, content in data.items():
            if isinstance(content, list):
                summary_parts.append(f"{source}: {len(content)} items")
            elif isinstance(content, dict):
                summary_parts.append(f"{source}: {len(content)} fields")
            else:
                summary_parts.append(f"{source}: 1 item")

        return ", ".join(summary_parts)

    async def _create_report(
        self,
        analysis_type: str,
        insights: List[Dict[str, Any]],
        stats_results: Dict[str, Any],
        pattern_results: Dict[str, Any]
    ) -> str:
        """
        분석 보고서 생성

        Args:
            analysis_type: 분석 타입
            insights: 인사이트 목록
            stats_results: 통계 결과
            pattern_results: 패턴 결과

        Returns:
            str: 보고서 텍스트
        """
        logger.info("[AnalysisExecutor] Creating report")

        report_parts = [
            f"# {analysis_type.upper()} 분석 보고서",
            f"\n## 주요 인사이트 ({len(insights)}개)",
        ]

        for i, insight in enumerate(insights, 1):
            report_parts.append(
                f"{i}. [{insight.get('type', 'general')}] "
                f"{insight.get('content', '')} "
                f"(신뢰도: {insight.get('confidence', 0):.0%})"
            )

        report_parts.append("\n## 통계 메트릭")
        for key, value in stats_results.get("metrics", {}).items():
            report_parts.append(f"- {key}: {value}")

        report_parts.append("\n## 발견된 패턴")
        patterns = pattern_results.get("patterns", [])
        if patterns:
            for pattern in patterns:
                report_parts.append(f"- {pattern.get('description', '')}")
        else:
            report_parts.append("- 특별한 패턴이 발견되지 않았습니다.")

        return "\n".join(report_parts)


# 사용 예시
if __name__ == "__main__":
    async def test_analysis_executor():
        """AnalysisExecutor 테스트"""

        # Executor 초기화
        executor = AnalysisExecutor()

        # 테스트 데이터
        test_data = {
            "sales_data": [
                {"month": "Jan", "amount": 100},
                {"month": "Feb", "amount": 150},
                {"month": "Mar", "amount": 120}
            ],
            "user_stats": {
                "total_users": 1000,
                "active_users": 750
            }
        }

        # 공유 상태 생성
        shared_state = {
            "query": "매출 데이터 분석해줘",
            "session_id": "test_session"
        }

        print("="*60)
        print("Testing AnalysisExecutor")
        print("-"*60)

        # 실행
        result = await executor.execute(
            shared_state,
            input_data=test_data,
            analysis_type="comprehensive"
        )

        print(f"Status: {result['status']}")
        print(f"Insights: {len(result.get('insights', []))}")
        print(f"Execution time: {result.get('execution_time', 0):.2f}s")
        print("\nReport:")
        print(result.get('report', ''))

    import asyncio
    asyncio.run(test_analysis_executor())
