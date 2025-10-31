"""
Intent Loader - Intent 설정 로더

config/intents.yaml 파일에서 Intent 정의를 로드합니다.
도메인별로 Intent를 커스터마이징할 수 있습니다.

Usage:
    >>> from app.framework.agents.cognitive.intent_loader import IntentLoader
    >>>
    >>> # Intent 설정 로드
    >>> config = IntentLoader.load_from_yaml()
    >>>
    >>> # Intent 목록 조회
    >>> for intent in config.intents:
    ...     print(f"{intent.name}: {intent.display_name}")
    >>>
    >>> # 특정 Intent 조회
    >>> intent = IntentLoader.get_intent_by_name(config, "information_inquiry")
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class IntentDefinition(BaseModel):
    """
    Intent 정의

    YAML 파일의 각 Intent 항목을 나타냅니다.
    """
    name: str = Field(..., description="Intent 고유 이름 (영문, 소문자, 언더스코어)")
    display_name: str = Field(..., description="화면 표시 이름")
    description: str = Field(..., description="Intent 설명")
    keywords: List[str] = Field(default_factory=list, description="관련 키워드 리스트")
    confidence_threshold: float = Field(..., description="신뢰도 임계값 (0.0 ~ 1.0)")
    suggested_agents: List[str] = Field(default_factory=list, description="실행할 Agent 팀")
    priority: int = Field(default=1, description="우선순위 (낮을수록 우선)")
    examples: List[str] = Field(default_factory=list, description="예제 질문")
    system: bool = Field(default=False, description="시스템 Intent 여부")
    enabled: bool = Field(default=True, description="활성화 여부")
    response_template: Optional[str] = Field(default=None, description="응답 템플릿")


class IntentMatchingConfig(BaseModel):
    """Intent 매칭 설정"""
    min_confidence: float = Field(default=0.5, description="최소 신뢰도")
    fallback_intent: str = Field(default="unclear", description="Fallback Intent")
    use_llm_classification: bool = Field(default=True, description="LLM 분류 사용")
    llm_model: str = Field(default="gpt-4o-mini", description="LLM 모델")
    keyword_weight: float = Field(default=0.3, description="키워드 가중치")
    llm_weight: float = Field(default=0.7, description="LLM 가중치")


class IntentConfig(BaseModel):
    """
    Intent 설정 (intents.yaml 전체)
    """
    intents: List[IntentDefinition]
    matching: IntentMatchingConfig


class IntentLoader:
    """Intent 설정 로더"""

    @staticmethod
    def load_from_yaml(config_path: str = "config/intents.yaml") -> IntentConfig:
        """
        YAML에서 Intent 설정 로드

        Args:
            config_path: Intent 설정 파일 경로

        Returns:
            IntentConfig: Intent 설정

        Raises:
            FileNotFoundError: 파일이 없는 경우
            yaml.YAMLError: YAML 파싱 오류
        """
        # 경로 해석
        path = Path(config_path)

        # 상대 경로면 backend/ 기준으로 변경
        if not path.is_absolute():
            backend_dir = Path(__file__).parent.parent.parent.parent.parent
            path = backend_dir / config_path

        if not path.exists():
            raise FileNotFoundError(f"Intent config not found: {path}")

        # YAML 파일 읽기
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Pydantic 모델로 변환
        try:
            config = IntentConfig(**data)
            logger.info(f"Loaded {len(config.intents)} intents from {path.name}")
            return config
        except Exception as e:
            logger.error(f"Failed to parse intent config: {e}")
            raise

    @staticmethod
    def get_intent_by_name(config: IntentConfig, name: str) -> Optional[IntentDefinition]:
        """
        이름으로 Intent 조회

        Args:
            config: Intent 설정
            name: Intent 이름

        Returns:
            Optional[IntentDefinition]: Intent 정의 (없으면 None)
        """
        for intent in config.intents:
            if intent.name == name:
                return intent
        return None

    @staticmethod
    def get_active_intents(config: IntentConfig) -> List[IntentDefinition]:
        """
        활성화된 Intent 목록

        Args:
            config: Intent 설정

        Returns:
            List[IntentDefinition]: 활성화된 Intent 리스트
        """
        return [intent for intent in config.intents if intent.enabled]

    @staticmethod
    def get_non_system_intents(config: IntentConfig) -> List[IntentDefinition]:
        """
        시스템 Intent 제외한 일반 Intent 목록

        Args:
            config: Intent 설정

        Returns:
            List[IntentDefinition]: 일반 Intent 리스트
        """
        return [
            intent for intent in config.intents
            if intent.enabled and not intent.system
        ]

    @staticmethod
    def search_intents_by_keyword(
        config: IntentConfig,
        keyword: str
    ) -> List[IntentDefinition]:
        """
        키워드로 Intent 검색

        Args:
            config: Intent 설정
            keyword: 검색 키워드

        Returns:
            List[IntentDefinition]: 키워드를 포함한 Intent 리스트
        """
        keyword_lower = keyword.lower()
        results = []

        for intent in config.intents:
            if not intent.enabled:
                continue

            # 키워드 리스트에서 검색
            if any(keyword_lower in kw.lower() for kw in intent.keywords):
                results.append(intent)

        return results

    @staticmethod
    def get_intents_by_priority(config: IntentConfig) -> List[IntentDefinition]:
        """
        우선순위로 정렬된 Intent 목록

        Args:
            config: Intent 설정

        Returns:
            List[IntentDefinition]: 우선순위 순으로 정렬된 Intent
        """
        active_intents = IntentLoader.get_active_intents(config)
        return sorted(active_intents, key=lambda x: x.priority)

    @staticmethod
    def create_intent_mapping(config: IntentConfig) -> Dict[str, IntentDefinition]:
        """
        Intent 이름 → Intent 정의 매핑 생성

        Args:
            config: Intent 설정

        Returns:
            Dict[str, IntentDefinition]: Intent 매핑
        """
        return {intent.name: intent for intent in config.intents}

    @staticmethod
    def validate_config(config: IntentConfig) -> List[str]:
        """
        Intent 설정 검증

        Args:
            config: Intent 설정

        Returns:
            List[str]: 검증 오류 메시지 리스트 (빈 리스트면 정상)
        """
        errors = []

        # Intent 이름 중복 체크
        names = [intent.name for intent in config.intents]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            errors.append(f"Duplicate intent names: {set(duplicates)}")

        # Fallback intent 존재 체크
        fallback_name = config.matching.fallback_intent
        if not IntentLoader.get_intent_by_name(config, fallback_name):
            errors.append(f"Fallback intent '{fallback_name}' not found")

        # 신뢰도 범위 체크
        for intent in config.intents:
            if not 0.0 <= intent.confidence_threshold <= 1.0:
                errors.append(
                    f"Intent '{intent.name}': confidence_threshold must be 0.0-1.0"
                )

        # 우선순위 체크
        for intent in config.intents:
            if intent.priority < 1:
                errors.append(f"Intent '{intent.name}': priority must be >= 1")

        return errors


# ============================================================================
# 싱글톤 인스턴스
# ============================================================================

_intent_config: Optional[IntentConfig] = None


def get_intent_config(reload: bool = False) -> IntentConfig:
    """
    Intent 설정 가져오기 (싱글톤)

    Args:
        reload: 설정 다시 로드 여부

    Returns:
        IntentConfig: Intent 설정
    """
    global _intent_config

    if _intent_config is None or reload:
        _intent_config = IntentLoader.load_from_yaml()

        # 설정 검증
        errors = IntentLoader.validate_config(_intent_config)
        if errors:
            logger.error(f"Intent config validation errors: {errors}")
            raise ValueError(f"Invalid intent config: {errors}")

    return _intent_config


def reload_intent_config():
    """Intent 설정 다시 로드"""
    global _intent_config
    _intent_config = None
    get_intent_config(reload=True)
    logger.info("Intent config reloaded")
