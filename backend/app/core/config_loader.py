"""
Config Loader - 통합 설정 로더

YAML 파일들을 로드하고 환경 변수를 치환하여 Pydantic 모델로 반환합니다.

Usage:
    >>> from app.core.config_loader import get_app_config, get_framework_config
    >>>
    >>> app_config = get_app_config()
    >>> db_host = app_config.database["postgres"]["host"]
    >>>
    >>> framework_config = get_framework_config()
    >>> llm_model = framework_config.llm["models"]["intent_analysis"]
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator
import re
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig(BaseModel):
    """데이터베이스 설정"""
    postgres: Dict[str, Any]
    mongodb: Optional[Dict[str, Any]] = None


class APIConfig(BaseModel):
    """API 설정"""
    host: str
    port: int
    reload: bool = False
    workers: int = 1
    cors_origins: list = []
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]


class SessionConfig(BaseModel):
    """세션 설정"""
    ttl_hours: int
    cleanup_interval_minutes: int
    max_sessions_per_user: int = 10


class MemoryConfig(BaseModel):
    """메모리 설정"""
    enabled: bool
    retention_days: int
    shortterm_limit: int
    midterm_limit: int
    longterm_limit: int
    token_limit: int
    summary_max_length: int
    data_reuse: Dict[str, Any]


class LoggingConfig(BaseModel):
    """로깅 설정"""
    level: str = "INFO"
    format: str
    file_rotation: str = "daily"
    max_log_size: str = "100MB"
    backup_count: int = 7
    log_dir: str = "logs"
    app_log: str = "app.log"
    error_log: str = "error.log"
    access_log: str = "access.log"


class ApplicationConfig(BaseModel):
    """애플리케이션 설정 (app.yaml)"""
    application: Dict[str, Any]
    database: Dict[str, Any]
    api: Dict[str, Any]
    session: Dict[str, Any]
    memory: Dict[str, Any]
    logging: Dict[str, Any]
    security: Optional[Dict[str, Any]] = None
    storage: Optional[Dict[str, Any]] = None
    monitoring: Optional[Dict[str, Any]] = None


class LLMConfig(BaseModel):
    """LLM 설정"""
    provider: str
    api_key: str
    organization: Optional[str] = None
    base_url: Optional[str] = None
    models: Dict[str, str]
    default_params: Dict[str, Any]
    retry: Dict[str, Any]
    timeout: Optional[Dict[str, int]] = None


class FrameworkConfig(BaseModel):
    """프레임워크 설정 (framework.yaml)"""
    framework: Dict[str, str]
    llm: Dict[str, Any]
    supervisor: Dict[str, Any]
    agents: Dict[str, Any]
    execution: Dict[str, Any]
    tools: Dict[str, Any]
    state: Optional[Dict[str, Any]] = None
    checkpointing: Optional[Dict[str, Any]] = None
    paths: Dict[str, str]
    prompts: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    development: Optional[Dict[str, Any]] = None


class ConfigLoader:
    """설정 로더 (YAML + 환경 변수)"""

    @staticmethod
    def _expand_env_vars(content: str) -> str:
        """
        환경 변수 치환

        지원 형식:
        - ${VAR_NAME}: 환경 변수 (없으면 에러)
        - ${VAR_NAME:default}: 환경 변수 (없으면 default 사용)

        Args:
            content: YAML 파일 내용

        Returns:
            str: 환경 변수가 치환된 내용
        """
        # ${VAR_NAME:default} 패턴
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else None

            # 환경 변수 조회
            value = os.environ.get(var_name)

            if value is None:
                if default_value is not None:
                    return default_value
                else:
                    # 환경 변수 없고 default도 없으면 빈 문자열
                    logger.warning(f"Environment variable '{var_name}' not set, using empty string")
                    return ""

            return value

        return re.sub(pattern, replacer, content)

    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """
        YAML 파일 로드 및 환경 변수 치환

        Args:
            file_path: YAML 파일 경로 (상대 경로는 backend/ 기준)

        Returns:
            Dict[str, Any]: 파싱된 YAML 데이터

        Raises:
            FileNotFoundError: 파일이 없는 경우
            yaml.YAMLError: YAML 파싱 오류
        """
        # 경로 해석
        path = Path(file_path)

        # 상대 경로면 backend/ 기준으로 변경
        if not path.is_absolute():
            backend_dir = Path(__file__).parent.parent.parent
            path = backend_dir / file_path

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        # YAML 파일 읽기
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 환경 변수 치환
        content = ConfigLoader._expand_env_vars(content)

        # YAML 파싱
        try:
            data = yaml.safe_load(content)
            logger.info(f"Loaded config: {path.name}")
            return data
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {path}")
            raise

    @staticmethod
    def load_app_config(config_path: str = "config/app.yaml") -> ApplicationConfig:
        """
        애플리케이션 설정 로드

        Args:
            config_path: 설정 파일 경로

        Returns:
            ApplicationConfig: 애플리케이션 설정
        """
        data = ConfigLoader.load_yaml(config_path)
        return ApplicationConfig(**data)

    @staticmethod
    def load_framework_config(config_path: str = "config/framework.yaml") -> FrameworkConfig:
        """
        프레임워크 설정 로드

        Args:
            config_path: 설정 파일 경로

        Returns:
            FrameworkConfig: 프레임워크 설정
        """
        data = ConfigLoader.load_yaml(config_path)
        return FrameworkConfig(**data)


# ============================================================================
# 싱글톤 인스턴스
# ============================================================================

_app_config: Optional[ApplicationConfig] = None
_framework_config: Optional[FrameworkConfig] = None


def get_app_config(reload: bool = False) -> ApplicationConfig:
    """
    애플리케이션 설정 가져오기 (싱글톤)

    Args:
        reload: 설정 다시 로드 여부

    Returns:
        ApplicationConfig: 애플리케이션 설정
    """
    global _app_config

    if _app_config is None or reload:
        _app_config = ConfigLoader.load_app_config()

    return _app_config


def get_framework_config(reload: bool = False) -> FrameworkConfig:
    """
    프레임워크 설정 가져오기 (싱글톤)

    Args:
        reload: 설정 다시 로드 여부

    Returns:
        FrameworkConfig: 프레임워크 설정
    """
    global _framework_config

    if _framework_config is None or reload:
        _framework_config = ConfigLoader.load_framework_config()

    return _framework_config


def reload_configs():
    """모든 설정 다시 로드"""
    global _app_config, _framework_config
    _app_config = None
    _framework_config = None
    get_app_config(reload=True)
    get_framework_config(reload=True)
    logger.info("All configs reloaded")
