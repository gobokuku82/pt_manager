# 범용 에이전트 프레임워크 초기화 마스터 플랜

**작성일**: 2025-10-28
**프로젝트**: AI_PTmanager → Generic Agent Framework
**목표**: 도메인 독립적인 범용 멀티 에이전트 프레임워크 구축

---

## 📋 목차

1. [프로젝트 현황 분석](#1-프로젝트-현황-분석)
2. [초기화 목표 및 원칙](#2-초기화-목표-및-원칙)
3. [아키텍처 설계](#3-아키텍처-설계)
4. [파일별 처리 계획](#4-파일별-처리-계획)
5. [단계별 실행 계획](#5-단계별-실행-계획)
6. [검증 및 테스트 계획](#6-검증-및-테스트-계획)
7. [문서화 계획](#7-문서화-계획)

---

## 1. 프로젝트 현황 분석

### 1.1 현재 프로젝트 개요

**도메인**: 부동산 AI 챗봇 "홈즈냥즈"
**기술 스택**:
- Backend: FastAPI, LangGraph 0.6, PostgreSQL, OpenAI
- Frontend: React (Next.js), TypeScript, shadcn/ui
- Architecture: Multi-agent system with Team-based Supervisor pattern

### 1.2 핵심 강점 (유지해야 할 부분)

#### 백엔드 아키텍처
✅ **LangGraph 0.6 기반 멀티 에이전트 시스템**
- Team-based Supervisor 패턴
- 3-tier agent hierarchy (Supervisor → Teams → Agents)
- HITL (Human-in-the-loop) 지원
- PostgreSQL checkpointing

✅ **모듈화된 구조**
- Foundation layer (config, context, registry, states)
- Cognitive agents (planning, intent analysis)
- Execution agents (search, document, analysis)
- Tools & utilities

✅ **고급 기능**
- Real-time WebSocket communication
- 3-layer progress tracking (Supervisor → Agent → Step)
- Long-term memory system (3-tier: short/mid/long term)
- Data reuse optimization
- Session management

#### 프론트엔드
✅ **실시간 UI/UX**
- WebSocket-based streaming
- Three-layer progress visualization
- Structured answer display
- Agent steps tracking

### 1.3 문제점 및 개선 필요 사항

#### 구조적 문제
❌ **도메인 로직 혼재**
- IntentType이 부동산에 특화 (legal_consult, market_inquiry, loan_consult 등)
- Tools가 모두 부동산 전용 (contract_analysis, loan_simulator, market_data 등)
- 프롬프트가 부동산 도메인 하드코딩

❌ **설정 파일 분산**
- `app/core/config.py` (애플리케이션 설정)
- `app/agent/foundation/config.py` (에이전트 시스템 설정)
- 중복된 설정 항목들

❌ **미사용 코드**
- `app/agent/foundation/old/` - 구버전 메모리 서비스
- `app/api/old/` - 구버전 세션 매니저
- `app/crud/` - 빈 디렉토리

❌ **스키마 혼재**
- 부동산 전용 스키마 (`real_estate.py`, `trust.py`)
- Chat 관련 범용 스키마와 혼재

#### 코드 품질
⚠️ **하드코딩된 값들**
- `user_id = 1` 임시 하드코딩 다수
- 부동산 관련 문자열 상수
- 도메인 특화 안내 메시지

⚠️ **테스트 부재**
- `backend/tests/` 디렉토리 존재하나 테스트 파일 없음

---

## 2. 초기화 목표 및 원칙

### 2.1 핵심 목표

1. **도메인 독립성 확보**
   - 모든 도메인 특화 코드 제거 또는 템플릿화
   - 설정 기반으로 도메인 정의 가능하도록 변경

2. **현재 완성도 유지**
   - LangGraph 0.6 HITL 패턴 유지
   - 3-layer progress tracking 유지
   - Long-term memory 시스템 유지
   - WebSocket 실시간 통신 유지

3. **확장성 및 재사용성**
   - 플러그인 방식의 Tool 시스템
   - 설정 파일 기반 Intent 정의
   - Template 기반 Agent 생성

4. **개발자 경험 개선**
   - 명확한 문서화
   - 예제 코드 및 템플릿 제공
   - 빠른 시작 가이드

### 2.2 설계 원칙

#### SOLID 원칙 적용
- **Single Responsibility**: 각 모듈은 하나의 책임만
- **Open/Closed**: 확장에는 열려있고 수정에는 닫혀있도록
- **Liskov Substitution**: Agent/Tool 인터페이스 준수
- **Interface Segregation**: 필요한 기능만 노출
- **Dependency Inversion**: 구체적 구현이 아닌 추상화에 의존

#### Clean Architecture
```
┌─────────────────────────────────────┐
│     Presentation Layer              │
│  (FastAPI, WebSocket, React UI)     │
├─────────────────────────────────────┤
│     Application Layer               │
│  (Supervisor, Planning, Execution)  │
├─────────────────────────────────────┤
│     Domain Layer                    │
│  (Agents, Tools, States)            │  ← Domain-agnostic
├─────────────────────────────────────┤
│     Infrastructure Layer            │
│  (DB, LLM, External APIs)           │
└─────────────────────────────────────┘
```

---

## 3. 아키텍처 설계

### 3.1 디렉토리 구조 (목표)

```
backend/
├── app/
│   ├── core/                          # 애플리케이션 코어
│   │   ├── config.py                  # ✅ 통합된 설정 (중앙화)
│   │   └── dependencies.py            # 🆕 FastAPI dependencies
│   │
│   ├── framework/                     # 🆕 범용 프레임워크 (domain-agnostic)
│   │   ├── foundation/                # 시스템 기반
│   │   │   ├── config.py              # Framework 설정
│   │   │   ├── context.py             # LLM Context
│   │   │   ├── states.py              # State 관리
│   │   │   ├── registry.py            # Agent/Tool Registry
│   │   │   └── checkpointer.py        # Checkpointing
│   │   │
│   │   ├── supervisor/                # Supervisor 패턴
│   │   │   ├── base_supervisor.py     # 🆕 추상 Base Supervisor
│   │   │   └── team_supervisor.py     # Team-based implementation
│   │   │
│   │   ├── agents/                    # Agent 시스템
│   │   │   ├── base/                  # 🆕 Base classes
│   │   │   │   ├── base_agent.py      # Abstract Agent
│   │   │   │   ├── base_executor.py   # Abstract Executor
│   │   │   │   └── interfaces.py      # Agent interfaces
│   │   │   │
│   │   │   ├── cognitive/             # Cognitive layer
│   │   │   │   ├── planning_agent.py  # ✅ 리팩토링
│   │   │   │   └── query_decomposer.py
│   │   │   │
│   │   │   └── execution/             # Execution layer
│   │   │       └── base_executor.py   # ✅ 템플릿화
│   │   │
│   │   ├── tools/                     # Tool 시스템
│   │   │   ├── base_tool.py           # 🆕 Abstract Tool
│   │   │   ├── tool_registry.py       # 🆕 Tool Registry
│   │   │   └── examples/              # 🆕 예제 Tools
│   │   │       └── example_search_tool.py
│   │   │
│   │   └── llm/                       # LLM 관리
│   │       ├── llm_service.py         # ✅ 유지
│   │       └── prompt_templates.py    # 🆕 템플릿 시스템
│   │
│   ├── domain/                        # 🆕 Domain-specific code (사용자 정의)
│   │   ├── __init__.py                # "여기에 도메인 코드 작성"
│   │   ├── intents.py                 # 🆕 도메인별 Intent 정의
│   │   ├── agents/                    # 🆕 도메인별 Agent 구현
│   │   │   └── example_agent.py
│   │   └── tools/                     # 🆕 도메인별 Tool 구현
│   │       └── example_tool.py
│   │
│   ├── api/                           # API Layer
│   │   ├── chat_api.py                # ✅ 리팩토링
│   │   ├── ws_manager.py              # ✅ 유지
│   │   ├── session_manager.py         # ✅ 통합
│   │   └── schemas.py                 # ✅ 범용화
│   │
│   ├── db/                            # Database
│   │   ├── base.py                    # 🆕 Base models
│   │   ├── postgre_db.py              # ✅ 유지
│   │   └── models/                    # DB Models
│   │       ├── chat.py                # ✅ 유지
│   │       └── users.py               # ✅ 유지
│   │
│   └── main.py                        # ✅ 리팩토링
│
├── config/                            # 🆕 설정 파일 디렉토리
│   ├── intents.yaml                   # 🆕 Intent 정의
│   ├── agents.yaml                    # 🆕 Agent 설정
│   └── prompts/                       # 🆕 프롬프트 템플릿
│       ├── intent_analysis.txt
│       └── planning.txt
│
├── examples/                          # 🆕 예제 코드
│   ├── quickstart.py                  # 빠른 시작 예제
│   ├── custom_agent.py                # 커스텀 Agent 예제
│   └── custom_tool.py                 # 커스텀 Tool 예제
│
├── tests/                             # 🆕 테스트 코드
│   ├── unit/                          # Unit tests
│   ├── integration/                   # Integration tests
│   └── e2e/                           # E2E tests
│
└── docs/                              # 🆕 문서
    ├── ARCHITECTURE.md                # 아키텍처 가이드
    ├── QUICKSTART.md                  # 빠른 시작
    ├── API_REFERENCE.md               # API 문서
    └── CUSTOMIZATION.md               # 커스터마이징 가이드

frontend/
├── components/
│   ├── chat/                          # 🆕 Chat 관련 컴포넌트 분리
│   │   ├── chat-interface.tsx         # ✅ 리팩토링
│   │   ├── message-list.tsx           # 🆕 분리
│   │   └── input-area.tsx             # 🆕 분리
│   │
│   ├── progress/                      # 🆕 Progress 관련
│   │   ├── progress-container.tsx     # ✅ 유지
│   │   └── step-tracker.tsx           # ✅ 유지
│   │
│   └── ui/                            # UI 라이브러리
│       └── ...                        # ✅ 유지
│
├── lib/                               # Utilities
│   ├── api.ts                         # ✅ 유지
│   ├── ws.ts                          # ✅ 유지
│   └── types.ts                       # ✅ 범용화
│
└── examples/                          # 🆕 예제 페이지
    └── custom-agent-demo.tsx
```

### 3.2 핵심 컴포넌트 설계

#### 3.2.1 Intent System (설정 기반)

**현재 (하드코딩)**:
```python
class IntentType(Enum):
    LEGAL_CONSULT = "법률상담"
    MARKET_INQUIRY = "시세조회"
    LOAN_CONSULT = "대출상담"
    # ... 부동산 전용
```

**목표 (설정 기반)**:
```yaml
# config/intents.yaml
intents:
  - name: "legal_consult"
    display_name: "법률 상담"
    keywords: ["법률", "계약", "규정"]
    confidence_threshold: 0.7
    suggested_agents: ["search_team", "analysis_team"]

  - name: "data_inquiry"
    display_name: "데이터 조회"
    keywords: ["조회", "검색", "찾기"]
    confidence_threshold: 0.6
    suggested_agents: ["search_team"]

  # 사용자가 추가 정의 가능
  - name: "custom_intent"
    display_name: "커스텀 의도"
    keywords: ["custom"]
    confidence_threshold: 0.5
    suggested_agents: ["custom_team"]
```

```python
# app/framework/agents/cognitive/planning_agent.py
class PlanningAgent:
    def __init__(self, config_path: str = "config/intents.yaml"):
        self.intents = self._load_intents(config_path)

    def _load_intents(self, path: str) -> List[IntentDefinition]:
        """YAML에서 Intent 정의 로드"""
        # 동적으로 Intent 로드
        pass
```

#### 3.2.2 Tool System (플러그인 방식)

**추상 Base Class**:
```python
# app/framework/tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ToolMetadata(BaseModel):
    """Tool 메타데이터"""
    name: str
    description: str
    version: str
    author: Optional[str] = None
    tags: List[str] = []

class BaseTool(ABC):
    """모든 Tool의 기본 클래스"""

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Tool 메타데이터 반환"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Tool 실행"""
        pass

    def validate_input(self, **kwargs) -> bool:
        """입력 검증 (선택적 override)"""
        return True
```

**예제 구현**:
```python
# app/domain/tools/example_tool.py
class ExampleSearchTool(BaseTool):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="example_search",
            description="예제 검색 도구",
            version="1.0.0",
            tags=["search", "example"]
        )

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        # 사용자 정의 로직
        results = await self._search(query)
        return {"results": results}
```

**Tool Registry**:
```python
# app/framework/tools/tool_registry.py
class ToolRegistry:
    """Tool 등록 및 관리"""
    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool):
        """Tool 등록"""
        cls._tools[tool.metadata.name] = tool

    @classmethod
    def get(cls, name: str) -> Optional[BaseTool]:
        """Tool 조회"""
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> List[ToolMetadata]:
        """등록된 Tool 목록"""
        return [tool.metadata for tool in cls._tools.values()]
```

#### 3.2.3 Agent System (템플릿 기반)

**Base Executor**:
```python
# app/framework/agents/base/base_executor.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable

class BaseExecutor(ABC):
    """모든 Executor의 기본 클래스"""

    def __init__(
        self,
        llm_context=None,
        progress_callback: Optional[Callable] = None
    ):
        self.llm_context = llm_context
        self.progress_callback = progress_callback
        self.tools = self._register_tools()

    @abstractmethod
    def _register_tools(self) -> Dict[str, BaseTool]:
        """사용할 Tool 등록"""
        pass

    @abstractmethod
    async def execute(self, shared_state: SharedState, **kwargs) -> Dict[str, Any]:
        """실행 로직"""
        pass

    async def send_progress(self, event_type: str, data: Dict[str, Any]):
        """진행 상황 전송"""
        if self.progress_callback:
            await self.progress_callback(event_type, data)
```

**사용자 정의 Executor 예제**:
```python
# app/domain/agents/custom_executor.py
from app.framework.agents.base import BaseExecutor
from app.framework.tools import ToolRegistry

class CustomSearchExecutor(BaseExecutor):
    """사용자 정의 검색 Executor"""

    def _register_tools(self) -> Dict[str, BaseTool]:
        return {
            "search": ToolRegistry.get("example_search"),
            "analysis": ToolRegistry.get("example_analysis")
        }

    async def execute(self, shared_state: SharedState, **kwargs):
        # Step 1: 키워드 추출
        await self.send_progress("agent_step_progress", {
            "agentName": "custom_search",
            "stepIndex": 0,
            "status": "in_progress"
        })

        keywords = await self._extract_keywords(shared_state.query)

        # Step 2: 검색 실행
        await self.send_progress("agent_step_progress", {
            "agentName": "custom_search",
            "stepIndex": 1,
            "status": "in_progress"
        })

        results = await self.tools["search"].execute(query=keywords)

        return results
```

---

## 4. 파일별 처리 계획

### 4.1 백엔드 파일 분류

#### ✅ 유지 (범용, 수정 불필요)

| 파일 경로 | 설명 | 비고 |
|---------|------|------|
| `app/core/__init__.py` | 초기화 파일 | - |
| `app/db/postgre_db.py` | PostgreSQL 연결 | - |
| `app/db/mongo_db.py` | MongoDB 연결 | 선택적 유지 |
| `app/api/ws_manager.py` | WebSocket 관리 | 완벽함 |
| `app/api/error_handlers.py` | 에러 핸들링 | - |
| `app/framework/foundation/context.py` | LLM Context | - |
| `app/framework/foundation/checkpointer.py` | Checkpointing | - |
| `app/framework/foundation/decision_logger.py` | 로깅 | - |

#### ⚠️ 리팩토링 (범용화 필요)

| 파일 경로 | 문제점 | 수정 방안 |
|---------|--------|----------|
| `app/main.py` | 부동산 챗봇 설명 하드코딩 | 설정 기반으로 변경 |
| `app/core/config.py` | 부동산 관련 설정 포함 | 범용 설정으로 분리 |
| `app/agent/foundation/config.py` | 중복 설정, 부동산 DB 경로 | 통합 및 범용화 |
| `app/agent/cognitive_agents/planning_agent.py` | IntentType이 부동산 전용 | 설정 기반 Intent 로드 |
| `app/agent/cognitive_agents/query_decomposer.py` | 검토 필요 | 범용화 가능 여부 확인 |
| `app/agent/execution_agents/search_executor.py` | 부동산 Tool 직접 사용 | BaseTool 사용으로 변경 |
| `app/agent/execution_agents/analysis_executor.py` | 부동산 분석 로직 | 템플릿화 |
| `app/agent/execution_agents/document_executor.py` | 계약서 생성 로직 | HITL 패턴은 유지, 도메인 분리 |
| `app/agent/supervisor/team_supervisor.py` | 부동산 관련 메시지 하드코딩 | 설정 기반으로 변경 |
| `app/api/chat_api.py` | user_id=1 하드코딩 다수 | 인증 시스템 연동 준비 |
| `app/api/schemas.py` | 부동산 스키마 혼재 | 범용 스키마와 분리 |
| `app/framework/foundation/separated_states.py` | State 정의 검토 | 범용화 확인 |
| `app/framework/foundation/agent_registry.py` | Agent 등록 방식 검토 | 개선 가능 |
| `app/framework/foundation/agent_adapter.py` | Adapter 패턴 검토 | 간소화 가능 |

#### 🔄 템플릿화 (예제로 변환)

| 파일 경로 | 처리 방법 |
|---------|----------|
| `app/agent/execution_agents/search_executor.py` | → `examples/custom_search_executor.py` |
| `app/agent/execution_agents/analysis_executor.py` | → `examples/custom_analysis_executor.py` |
| `app/agent/execution_agents/document_executor.py` | → `examples/custom_document_executor.py` (HITL 예제) |

#### ❌ 제거 (도메인 특화)

| 파일 경로 | 이유 |
|---------|------|
| `app/agent/tools/contract_analysis_tool.py` | 부동산 계약서 분석 |
| `app/agent/tools/loan_simulator_tool.py` | 대출 시뮬레이션 |
| `app/agent/tools/roi_calculator_tool.py` | ROI 계산 |
| `app/agent/tools/market_analysis_tool.py` | 시장 분석 |
| `app/agent/tools/market_data_tool.py` | 시장 데이터 |
| `app/agent/tools/real_estate_search_tool.py` | 부동산 검색 |
| `app/agent/tools/loan_data_tool.py` | 대출 데이터 |
| `app/agent/tools/infrastructure_tool.py` | 인프라 조회 |
| `app/agent/tools/policy_matcher_tool.py` | 정책 매칭 |
| `app/agent/tools/hybrid_legal_search.py` | 법률 검색 (부동산 특화) |
| `app/agent/tools/lease_contract_generator_tool.py` | 임대차 계약서 생성 |
| `app/models/service/real_estate.py` | 부동산 서비스 |
| `app/models/service/trust.py` | 신탁 서비스 |
| `app/schemas/real_estate.py` | 부동산 스키마 |
| `app/schemas/trust.py` | 신탁 스키마 |
| `app/utils/building_api.py` | 건물 API |
| `app/utils/data_collector.py` | 데이터 수집 |
| `app/utils/geocode_aprtments.py` | 지오코딩 |
| `app/utils/database_config.py` | DB 설정 (중복) |
| `backend/scripts/` (전체) | 데이터 임포트 |
| `app/agent/foundation/old/` | 구버전 코드 |
| `app/api/old/` | 구버전 코드 |
| `app/crud/` | 빈 디렉토리 |

#### 🆕 신규 생성

| 파일 경로 | 목적 |
|---------|------|
| `app/framework/agents/base/base_agent.py` | Abstract Agent |
| `app/framework/agents/base/base_executor.py` | Abstract Executor |
| `app/framework/tools/base_tool.py` | Abstract Tool |
| `app/framework/tools/tool_registry.py` | Tool 등록 시스템 |
| `app/domain/intents.py` | Intent 정의 (예제) |
| `config/intents.yaml` | Intent 설정 |
| `config/agents.yaml` | Agent 설정 |
| `config/prompts/` | 프롬프트 템플릿 |
| `examples/quickstart.py` | 빠른 시작 |
| `examples/custom_agent.py` | 커스텀 Agent |
| `examples/custom_tool.py` | 커스텀 Tool |
| `docs/ARCHITECTURE.md` | 아키텍처 |
| `docs/QUICKSTART.md` | 시작 가이드 |
| `docs/API_REFERENCE.md` | API 문서 |
| `docs/CUSTOMIZATION.md` | 커스터마이징 |

### 4.2 프론트엔드 파일 분류

#### ✅ 유지

- `components/ui/` - 전체 UI 라이브러리
- `components/progress-container.tsx` - 진행 상황 표시
- `components/step-item.tsx` - 단계 표시
- `components/session-list.tsx` - 세션 목록
- `lib/api.ts` - API 클라이언트
- `lib/utils.ts` - 유틸리티
- `hooks/use-toast.ts` - Toast hook
- `hooks/use-mobile.ts` - Mobile hook

#### ⚠️ 리팩토링

| 파일 | 수정 사항 |
|-----|----------|
| `components/chat-interface.tsx` | 도메인 특화 예제 질문 제거, 범용화 |
| `components/answer-display.tsx` | 부동산 아이콘/메시지 제거 |
| `lib/types.ts` | 범용 타입으로 변경 |

#### ❌ 제거

- `components/agents/` - 부동산 Agent UI
- `components/map-interface.tsx` - 지도 (도메인 특화)
- `components/lease_contract/` - 계약서 페이지 (예제로 이동)
- `lib/district-coordinates.ts` - 지역 좌표
- `lib/clustering.ts` - 클러스터링

#### 🔄 템플릿화

- `components/lease_contract/` → `examples/hitl-form-example/`

---

## 5. 단계별 실행 계획

### Phase 1: 준비 및 백업 (1일)

#### 1.1 프로젝트 백업
```bash
# 전체 프로젝트 백업
cp -r beta_v001 beta_v001_backup_$(date +%Y%m%d)

# Git 태그 생성
git tag -a v0.1.0-real-estate -m "부동산 챗봇 완성 버전"
git push origin v0.1.0-real-estate
```

#### 1.2 브랜치 생성
```bash
git checkout -b feature/generic-framework-refactoring
```

#### 1.3 문서 작성
- [x] 마스터 플랜 작성
- [ ] 파일별 상세 처리 계획
- [ ] 리팩토링 가이드라인
- [ ] 마이그레이션 체크리스트

### Phase 2: 불필요한 코드 제거 (2일)

#### 2.1 도메인 특화 Tool 제거
```bash
# tools/ 디렉토리 정리
rm app/agent/tools/contract_analysis_tool.py
rm app/agent/tools/loan_simulator_tool.py
rm app/agent/tools/roi_calculator_tool.py
rm app/agent/tools/market_analysis_tool.py
rm app/agent/tools/market_data_tool.py
rm app/agent/tools/real_estate_search_tool.py
rm app/agent/tools/loan_data_tool.py
rm app/agent/tools/infrastructure_tool.py
rm app/agent/tools/policy_matcher_tool.py
rm app/agent/tools/hybrid_legal_search.py
rm app/agent/tools/lease_contract_generator_tool.py

# __init__.py 업데이트
# 예제 Tool 하나만 남기고 주석 처리
```

**검증**: `pytest tests/` 실행, 의존성 에러 확인

#### 2.2 도메인 특화 모델/스키마 제거
```bash
# 부동산 관련 제거
rm app/models/service/real_estate.py
rm app/models/service/trust.py
rm app/schemas/real_estate.py
rm app/schemas/trust.py

# __init__.py 업데이트
```

#### 2.3 Utility 제거
```bash
rm app/utils/building_api.py
rm app/utils/data_collector.py
rm app/utils/geocode_aprtments.py
rm app/utils/database_config.py  # config.py와 중복
```

#### 2.4 스크립트 및 구버전 코드 제거
```bash
rm -rf backend/scripts/
rm -rf app/agent/foundation/old/
rm -rf app/api/old/
rm -rf app/crud/
```

#### 2.5 프론트엔드 정리
```bash
rm -rf frontend/components/agents/
rm frontend/components/map-interface.tsx
rm frontend/lib/district-coordinates.ts
rm frontend/lib/clustering.ts

# 계약서 페이지는 examples로 이동
mkdir -p examples/frontend/hitl-form-example
mv frontend/components/lease_contract/ examples/frontend/hitl-form-example/
```

**검증**:
- `npm run build` 성공 확인
- 누락된 import 확인

### Phase 3: 디렉토리 재구성 (1일)

#### 3.1 Framework 디렉토리 생성
```bash
mkdir -p app/framework/{foundation,supervisor,agents/{base,cognitive,execution},tools,llm}
```

#### 3.2 파일 이동
```bash
# Foundation
mv app/agent/foundation/* app/framework/foundation/

# Supervisor
mv app/agent/supervisor/* app/framework/supervisor/

# Agents
mv app/agent/cognitive_agents/* app/framework/agents/cognitive/
mv app/agent/execution_agents/* app/framework/agents/execution/

# LLM
mv app/agent/llm_manager/* app/framework/llm/

# Tools (analysis_tools.py만 남김)
mv app/agent/tools/analysis_tools.py app/framework/tools/
rm -rf app/agent/tools/
rm -rf app/agent/
```

#### 3.3 Domain 디렉토리 생성
```bash
mkdir -p app/domain/{agents,tools}
touch app/domain/__init__.py
touch app/domain/intents.py
```

#### 3.4 Config 디렉토리 생성
```bash
mkdir -p config/prompts
touch config/intents.yaml
touch config/agents.yaml
```

#### 3.5 Examples 디렉토리 생성
```bash
mkdir -p examples/{backend,frontend}
touch examples/quickstart.py
touch examples/custom_agent.py
touch examples/custom_tool.py
```

**검증**: Import 경로 모두 깨졌는지 확인 (다음 단계에서 수정)

### Phase 4: 코어 리팩토링 (5일)

#### 4.1 Base Classes 생성 (Day 1)

**파일**: `app/framework/agents/base/base_agent.py`
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class AgentMetadata(BaseModel):
    """Agent 메타데이터"""
    name: str
    description: str
    version: str
    capabilities: List[str]

class BaseAgent(ABC):
    """모든 Agent의 추상 기본 클래스"""

    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        pass

    @abstractmethod
    async def process(self, state: Any) -> Any:
        pass
```

**파일**: `app/framework/agents/base/base_executor.py`
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable
from app.framework.foundation.states import SharedState
from app.framework.tools.base_tool import BaseTool

class BaseExecutor(ABC):
    """모든 Executor의 추상 기본 클래스"""

    def __init__(
        self,
        llm_context=None,
        progress_callback: Optional[Callable[[str, dict], Awaitable[None]]] = None
    ):
        self.llm_context = llm_context
        self.progress_callback = progress_callback
        self.tools = self._register_tools()
        self.team_name = self._get_team_name()

    @abstractmethod
    def _register_tools(self) -> Dict[str, BaseTool]:
        """사용할 Tool 등록"""
        pass

    @abstractmethod
    def _get_team_name(self) -> str:
        """팀 이름 반환"""
        pass

    @abstractmethod
    async def execute(self, shared_state: SharedState, **kwargs) -> Dict[str, Any]:
        """실행 로직"""
        pass

    async def send_progress(self, event_type: str, data: Dict[str, Any]):
        """진행 상황 전송 (WebSocket)"""
        if self.progress_callback:
            await self.progress_callback(event_type, data)
```

**파일**: `app/framework/tools/base_tool.py`
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ToolMetadata(BaseModel):
    """Tool 메타데이터"""
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = []
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

class BaseTool(ABC):
    """모든 Tool의 추상 기본 클래스"""

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Tool 메타데이터 반환"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Tool 실행 (비동기)"""
        pass

    def validate_input(self, **kwargs) -> bool:
        """입력 검증 (선택적 override)"""
        return True

    async def pre_execute(self, **kwargs):
        """실행 전 처리 (선택적 override)"""
        pass

    async def post_execute(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """실행 후 처리 (선택적 override)"""
        return result
```

**파일**: `app/framework/tools/tool_registry.py`
```python
from typing import Dict, List, Optional
from app.framework.tools.base_tool import BaseTool, ToolMetadata
import logging

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Tool 등록 및 관리 (싱글톤)"""
    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        """Tool 등록"""
        name = tool.metadata.name
        if name in cls._tools:
            logger.warning(f"Tool '{name}' already registered, overwriting")
        cls._tools[name] = tool
        logger.info(f"Tool registered: {name} v{tool.metadata.version}")

    @classmethod
    def unregister(cls, name: str) -> bool:
        """Tool 등록 해제"""
        if name in cls._tools:
            del cls._tools[name]
            logger.info(f"Tool unregistered: {name}")
            return True
        return False

    @classmethod
    def get(cls, name: str) -> Optional[BaseTool]:
        """Tool 조회"""
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> List[ToolMetadata]:
        """등록된 Tool 목록"""
        return [tool.metadata for tool in cls._tools.values()]

    @classmethod
    def search_by_tag(cls, tag: str) -> List[BaseTool]:
        """태그로 Tool 검색"""
        return [
            tool for tool in cls._tools.values()
            if tag in tool.metadata.tags
        ]

    @classmethod
    def clear(cls):
        """모든 Tool 제거 (테스트용)"""
        cls._tools.clear()
        logger.info("All tools cleared")
```

**검증**: Unit test 작성 및 실행

#### 4.2 Intent System 리팩토링 (Day 2)

**파일**: `config/intents.yaml`
```yaml
# Intent 정의
# 사용자가 이 파일을 수정하여 도메인별 Intent 정의

intents:
  # 범용 Intent (기본 제공)
  - name: "information_inquiry"
    display_name: "정보 조회"
    description: "데이터 검색 및 조회"
    keywords: ["조회", "검색", "찾기", "알려주", "what", "where"]
    confidence_threshold: 0.6
    suggested_agents: ["search_team"]
    priority: 1

  - name: "data_analysis"
    display_name: "데이터 분석"
    description: "데이터 분석 및 인사이트 도출"
    keywords: ["분석", "평가", "비교", "추천", "analyze"]
    confidence_threshold: 0.7
    suggested_agents: ["search_team", "analysis_team"]
    priority: 2

  - name: "document_generation"
    display_name: "문서 생성"
    description: "문서 작성 및 생성"
    keywords: ["작성", "생성", "만들기", "create", "generate"]
    confidence_threshold: 0.7
    suggested_agents: ["document_team"]
    priority: 2

  - name: "document_review"
    display_name: "문서 검토"
    description: "문서 검토 및 분석"
    keywords: ["검토", "리뷰", "확인", "review", "check"]
    confidence_threshold: 0.7
    suggested_agents: ["document_team", "analysis_team"]
    priority: 2

  # 특수 Intent (시스템)
  - name: "unclear"
    display_name: "불명확"
    description: "의도 파악 불가"
    keywords: []
    confidence_threshold: 0.0
    suggested_agents: []
    priority: 99

  - name: "irrelevant"
    display_name: "범위 외"
    description: "서비스 범위 외 질문"
    keywords: []
    confidence_threshold: 0.0
    suggested_agents: []
    priority: 99

# Intent 매칭 설정
matching:
  min_confidence: 0.5
  fallback_intent: "unclear"
  use_llm_classification: true
  llm_model: "gpt-4o-mini"
```

**파일**: `app/framework/agents/cognitive/intent_loader.py` (신규)
```python
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum

class IntentDefinition(BaseModel):
    """Intent 정의"""
    name: str
    display_name: str
    description: str
    keywords: List[str]
    confidence_threshold: float
    suggested_agents: List[str]
    priority: int = 1

class IntentConfig(BaseModel):
    """Intent 설정"""
    intents: List[IntentDefinition]
    matching: Dict[str, Any]

class IntentLoader:
    """Intent 설정 로더"""

    @staticmethod
    def load_from_yaml(config_path: str = "config/intents.yaml") -> IntentConfig:
        """YAML에서 Intent 로드"""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Intent config not found: {config_path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return IntentConfig(**data)

    @staticmethod
    def create_intent_enum(config: IntentConfig):
        """동적으로 IntentType Enum 생성"""
        intent_dict = {
            intent.name.upper(): intent.name
            for intent in config.intents
        }
        return Enum('IntentType', intent_dict)
```

**파일**: `app/framework/agents/cognitive/planning_agent.py` (수정)
```python
# 기존 하드코딩된 IntentType 제거
# class IntentType(Enum): ...  ← 삭제

class PlanningAgent:
    """의도 분석 및 실행 계획 수립"""

    def __init__(
        self,
        llm_context=None,
        intent_config_path: str = "config/intents.yaml"
    ):
        # Intent 설정 로드
        self.intent_config = IntentLoader.load_from_yaml(intent_config_path)
        self.intents = {i.name: i for i in self.intent_config.intents}

        # LLMService 초기화
        if llm_context:
            self.llm_service = LLMService(llm_context=llm_context)
        else:
            self.llm_service = None

    async def analyze_intent(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> IntentResult:
        """의도 분석"""

        if not self.llm_service:
            # Fallback: 키워드 기반 매칭
            return self._keyword_based_matching(query)

        # LLM 기반 분류
        return await self._llm_based_classification(query, context)

    def _keyword_based_matching(self, query: str) -> IntentResult:
        """키워드 기반 Intent 매칭"""
        query_lower = query.lower()

        # Intent별 점수 계산
        scores = {}
        for intent in self.intent_config.intents:
            if intent.name in ["unclear", "irrelevant"]:
                continue

            score = sum(1 for kw in intent.keywords if kw in query_lower)
            if score > 0:
                scores[intent.name] = score / len(intent.keywords)

        # 최고 점수 Intent 선택
        if not scores:
            return IntentResult(
                intent_type="unclear",
                confidence=0.0,
                keywords=[],
                suggested_agents=[]
            )

        best_intent_name = max(scores, key=scores.get)
        best_intent = self.intents[best_intent_name]

        return IntentResult(
            intent_type=best_intent_name,
            confidence=scores[best_intent_name],
            keywords=best_intent.keywords,
            suggested_agents=best_intent.suggested_agents
        )

    async def _llm_based_classification(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> IntentResult:
        """LLM 기반 Intent 분류"""

        # Intent 리스트를 프롬프트에 포함
        intent_descriptions = "\n".join([
            f"- {intent.name}: {intent.description} (키워드: {', '.join(intent.keywords)})"
            for intent in self.intent_config.intents
            if intent.name not in ["unclear", "irrelevant"]
        ])

        # 프롬프트 생성 (기존 로직 유지, intent_descriptions 동적 생성)
        prompt = f"""
사용자 질문: {query}

사용 가능한 Intent 목록:
{intent_descriptions}

위 목록에서 가장 적합한 Intent를 선택하고, confidence(0.0-1.0)를 부여하세요.
"""

        # LLM 호출 (기존 로직 유지)
        result = await self.llm_service.call_llm(
            prompt=prompt,
            model="gpt-4o-mini",
            response_format={"type": "json_object"}
        )

        # 결과 파싱 및 IntentResult 생성
        # ...
```

**검증**:
- 기존 테스트 케이스 실행
- 새로운 Intent 추가 테스트

#### 4.3 Execution Agents 리팩토링 (Day 3)

**현재 구조**:
```
search_executor.py → 부동산 Tool 직접 사용
```

**목표 구조**:
```
BaseExecutor (abstract)
  ↓ extends
ExampleSearchExecutor (예제, domain/agents/)
```

**파일**: `app/framework/agents/execution/search_executor.py` (수정)
```python
# 기존 파일 전체를 BaseExecutor 형태로 리팩토링
from app.framework.agents.base.base_executor import BaseExecutor
from app.framework.tools.tool_registry import ToolRegistry
from app.framework.foundation.states import SearchTeamState, SharedState

class SearchExecutor(BaseExecutor):
    """
    검색 실행 Executor (범용)

    사용자는 이 클래스를 상속하여 도메인별 검색 로직 구현
    """

    def _get_team_name(self) -> str:
        return "search"

    def _register_tools(self) -> Dict[str, BaseTool]:
        """
        검색에 필요한 Tool 등록

        Override 예제:
            return {
                "search": ToolRegistry.get("custom_search_tool"),
                "filter": ToolRegistry.get("custom_filter_tool")
            }
        """
        # 기본적으로 비어있음 (사용자가 override)
        return {}

    async def execute(
        self,
        shared_state: SharedState,
        **kwargs
    ) -> Dict[str, Any]:
        """
        검색 실행 (템플릿 메서드 패턴)

        Override 가능:
            - _extract_keywords()
            - _perform_search()
            - _filter_results()
            - _format_results()
        """
        # Step 1: 키워드 추출
        await self.send_progress("agent_step_progress", {
            "agentName": self.team_name,
            "stepIndex": 0,
            "status": "in_progress",
            "progress": 10
        })
        keywords = await self._extract_keywords(shared_state.query)

        # Step 2: 검색 실행
        await self.send_progress("agent_step_progress", {
            "agentName": self.team_name,
            "stepIndex": 1,
            "status": "in_progress",
            "progress": 50
        })
        raw_results = await self._perform_search(keywords)

        # Step 3: 결과 필터링
        await self.send_progress("agent_step_progress", {
            "agentName": self.team_name,
            "stepIndex": 2,
            "status": "in_progress",
            "progress": 80
        })
        filtered_results = await self._filter_results(raw_results)

        # Step 4: 결과 포맷팅
        await self.send_progress("agent_step_progress", {
            "agentName": self.team_name,
            "stepIndex": 3,
            "status": "completed",
            "progress": 100
        })
        final_results = await self._format_results(filtered_results)

        return final_results

    # 이하 protected 메서드들 (override 가능)
    async def _extract_keywords(self, query: str) -> List[str]:
        """키워드 추출 (LLM 또는 NLP)"""
        if self.llm_service:
            # LLM 사용
            pass
        else:
            # 기본 토크나이징
            return query.split()

    async def _perform_search(self, keywords: List[str]) -> List[Dict]:
        """검색 실행 (Tool 사용)"""
        if "search" not in self.tools:
            raise NotImplementedError(
                "No search tool registered. "
                "Override _register_tools() to add search tool."
            )

        search_tool = self.tools["search"]
        return await search_tool.execute(keywords=keywords)

    async def _filter_results(self, results: List[Dict]) -> List[Dict]:
        """결과 필터링"""
        # 기본 구현: 그대로 반환
        return results

    async def _format_results(self, results: List[Dict]) -> Dict[str, Any]:
        """결과 포맷팅"""
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
```

**파일**: `examples/custom_search_executor.py` (신규)
```python
"""
커스텀 검색 Executor 예제

이 파일은 SearchExecutor를 상속하여
도메인별 검색 로직을 구현하는 예제입니다.
"""

from app.framework.agents.execution.search_executor import SearchExecutor
from app.framework.tools.tool_registry import ToolRegistry
from typing import Dict, Any, List

class CustomSearchExecutor(SearchExecutor):
    """
    커스텀 검색 Executor

    예제: E-commerce 상품 검색
    """

    def _register_tools(self) -> Dict[str, BaseTool]:
        """사용할 Tool 등록"""
        return {
            "search": ToolRegistry.get("product_search_tool"),
            "filter": ToolRegistry.get("product_filter_tool")
        }

    async def _extract_keywords(self, query: str) -> List[str]:
        """키워드 추출 (E-commerce 특화)"""
        # 예: 카테고리, 브랜드, 가격대 추출
        keywords = await super()._extract_keywords(query)

        # 추가 로직: 가격대 파싱
        if "만원" in query or "원" in query:
            keywords.append("price_filter")

        return keywords

    async def _filter_results(self, results: List[Dict]) -> List[Dict]:
        """결과 필터링 (E-commerce 특화)"""
        # 예: 재고 있는 상품만 필터링
        filtered = [r for r in results if r.get("in_stock", False)]

        # 가격순 정렬
        filtered.sort(key=lambda x: x.get("price", 0))

        return filtered

# 사용 예제
if __name__ == "__main__":
    # Tool 등록
    from examples.product_search_tool import ProductSearchTool
    ToolRegistry.register(ProductSearchTool())

    # Executor 생성
    executor = CustomSearchExecutor()

    # 실행
    result = await executor.execute(
        shared_state=SharedState(query="10만원대 노트북 추천해줘")
    )
    print(result)
```

**동일하게 처리**:
- `analysis_executor.py` → BaseAnalysisExecutor + 예제
- `document_executor.py` → BaseDocumentExecutor + 예제 (HITL 패턴 유지)

**검증**:
- 기존 부동산 Executor를 예제로 변환하여 동작 확인
- Unit test 작성

#### 4.4 Config 통합 (Day 4)

**문제점**:
- `app/core/config.py` - 애플리케이션 설정 (DB, API, Memory 등)
- `app/agent/foundation/config.py` - 에이전트 시스템 설정 (Model, Timeout, Paths 등)
- 중복된 설정, 의존성 복잡

**목표**:
```
config/
  ├── app.yaml          # 애플리케이션 설정
  ├── framework.yaml    # 프레임워크 설정
  ├── intents.yaml      # Intent 정의
  ├── agents.yaml       # Agent 설정
  └── prompts/          # 프롬프트 템플릿
```

**파일**: `config/app.yaml` (신규)
```yaml
# 애플리케이션 설정
application:
  name: "Generic Agent Framework"
  version: "1.0.0"
  description: "Domain-agnostic multi-agent framework"

# 데이터베이스
database:
  postgres:
    host: "localhost"
    port: 5432
    user: "postgres"
    password: "${POSTGRES_PASSWORD}"  # 환경 변수
    database: "agent_db"

  # 선택적: MongoDB
  mongodb:
    enabled: false
    url: "${MONGODB_URL}"

# API 설정
api:
  host: "0.0.0.0"
  port: 8000
  cors_origins:
    - "http://localhost:3000"
    - "http://127.0.0.1:3000"

# 세션 관리
session:
  ttl_hours: 24
  cleanup_interval_minutes: 60

# 메모리 시스템
memory:
  enabled: true
  retention_days: 90
  shortterm_limit: 5
  midterm_limit: 5
  longterm_limit: 10
  token_limit: 2000
  summary_max_length: 200

  # 데이터 재사용
  data_reuse:
    enabled: true
    message_limit: 5

# 로깅
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_rotation: "daily"
  max_log_size: "100MB"
  backup_count: 7
```

**파일**: `config/framework.yaml` (신규)
```yaml
# 프레임워크 설정
framework:
  version: "1.0.0"

# LLM 설정
llm:
  provider: "openai"
  api_key: "${OPENAI_API_KEY}"
  organization: "${OPENAI_ORG_ID}"

  # 모델 매핑
  models:
    intent_analysis: "gpt-4o-mini"
    plan_generation: "gpt-4o-mini"
    keyword_extraction: "gpt-4o-mini"
    insight_generation: "gpt-4o"
    response_synthesis: "gpt-4o-mini"
    error_response: "gpt-4o-mini"

  # 기본 파라미터
  default_params:
    temperature: 0.3
    max_tokens: 1000

  # 재시도
  retry:
    max_attempts: 3
    backoff_seconds: 1.0

# Supervisor 설정
supervisor:
  type: "team_based"
  enable_checkpointing: true
  max_recursion: 25
  max_retries: 3

# Agent 설정
agents:
  timeout: 30
  max_message_length: 10000

# Execution 설정
execution:
  default_strategy: "sequential"
  allow_parallel: true

# Tool 설정
tools:
  auto_discover: true
  discovery_paths:
    - "app.domain.tools"
    - "app.framework.tools"

# Paths
paths:
  checkpoint_dir: "data/system/checkpoints"
  agent_logging_dir: "data/system/agent_logging"
  log_dir: "logs"
```

**파일**: `app/core/config_loader.py` (신규)
```python
"""
통합 설정 로더

YAML 파일들을 로드하고 환경 변수를 치환하여
Pydantic 모델로 반환
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseModel):
    """데이터베이스 설정"""
    postgres: Dict[str, Any]
    mongodb: Dict[str, Any]

class APIConfig(BaseModel):
    """API 설정"""
    host: str
    port: int
    cors_origins: list

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

class ApplicationConfig(BaseModel):
    """애플리케이션 설정"""
    application: Dict[str, str]
    database: DatabaseConfig
    api: APIConfig
    session: Dict[str, Any]
    memory: MemoryConfig
    logging: Dict[str, Any]

class LLMConfig(BaseModel):
    """LLM 설정"""
    provider: str
    api_key: str
    organization: str
    models: Dict[str, str]
    default_params: Dict[str, Any]
    retry: Dict[str, Any]

class FrameworkConfig(BaseModel):
    """프레임워크 설정"""
    framework: Dict[str, str]
    llm: LLMConfig
    supervisor: Dict[str, Any]
    agents: Dict[str, Any]
    execution: Dict[str, Any]
    tools: Dict[str, Any]
    paths: Dict[str, str]

class ConfigLoader:
    """설정 로더"""

    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """
        YAML 파일 로드 및 환경 변수 치환

        예: ${OPENAI_API_KEY} → os.environ["OPENAI_API_KEY"]
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 환경 변수 치환
        content = os.path.expandvars(content)

        return yaml.safe_load(content)

    @staticmethod
    def load_app_config(config_path: str = "config/app.yaml") -> ApplicationConfig:
        """애플리케이션 설정 로드"""
        data = ConfigLoader.load_yaml(config_path)
        return ApplicationConfig(**data)

    @staticmethod
    def load_framework_config(config_path: str = "config/framework.yaml") -> FrameworkConfig:
        """프레임워크 설정 로드"""
        data = ConfigLoader.load_yaml(config_path)
        return FrameworkConfig(**data)

# 싱글톤 인스턴스
_app_config = None
_framework_config = None

def get_app_config() -> ApplicationConfig:
    """애플리케이션 설정 가져오기 (싱글톤)"""
    global _app_config
    if _app_config is None:
        _app_config = ConfigLoader.load_app_config()
    return _app_config

def get_framework_config() -> FrameworkConfig:
    """프레임워크 설정 가져오기 (싱글톤)"""
    global _framework_config
    if _framework_config is None:
        _framework_config = ConfigLoader.load_framework_config()
    return _framework_config
```

**기존 파일 수정**:
- `app/core/config.py` → 삭제, `config_loader.py`로 대체
- `app/agent/foundation/config.py` → 삭제, `config/framework.yaml`로 대체
- 모든 import 경로 수정:
  ```python
  # Before
  from app.core.config import settings

  # After
  from app.core.config_loader import get_app_config
  config = get_app_config()
  ```

**검증**:
- 모든 import 경로 수정 완료 확인
- 애플리케이션 시작 테스트

#### 4.5 Import 경로 전체 수정 (Day 5)

**작업**:
1. 모든 Python 파일의 import 문 수정
2. `__init__.py` 파일들 업데이트
3. FastAPI dependency injection 수정

**스크립트 작성**:
```python
# scripts/fix_imports.py
import os
import re
from pathlib import Path

# Import 경로 매핑
IMPORT_MAPPING = {
    "from app.agent.foundation": "from app.framework.foundation",
    "from app.agent.supervisor": "from app.framework.supervisor",
    "from app.agent.cognitive_agents": "from app.framework.agents.cognitive",
    "from app.agent.execution_agents": "from app.framework.agents.execution",
    "from app.agent.llm_manager": "from app.framework.llm",
    "from app.agent.tools": "from app.framework.tools",
    "from app.core.config import settings": "from app.core.config_loader import get_app_config",
    # ... 추가
}

def fix_imports_in_file(file_path: Path):
    """파일 내 import 경로 수정"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    for old, new in IMPORT_MAPPING.items():
        content = content.replace(old, new)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")

def main():
    """모든 Python 파일 처리"""
    backend_dir = Path("backend/app")

    for py_file in backend_dir.rglob("*.py"):
        fix_imports_in_file(py_file)

if __name__ == "__main__":
    main()
```

**실행**:
```bash
python scripts/fix_imports.py
```

**검증**:
- `python -m pytest tests/` - 모든 테스트 통과
- `python -m app.main` - 애플리케이션 시작 확인

### Phase 5: 프롬프트 템플릿화 (2일)

#### 5.1 프롬프트 추출

**현재 문제**: 프롬프트가 코드에 하드코딩되어 있음

**목표**: 템플릿 파일로 분리

**파일**: `config/prompts/intent_analysis.txt`
```
사용자 질문을 분석하여 의도를 파악해주세요.

===== 사용자 질문 =====
{{query}}

===== 대화 기록 =====
{{chat_history}}

===== 가능한 Intent 목록 =====
{{intent_list}}

===== 요청사항 =====
1. 가장 적합한 Intent를 선택하세요
2. Confidence(0.0-1.0)를 부여하세요
3. 키워드를 추출하세요
4. 추천 Agent 목록을 제시하세요

===== 출력 형식 (JSON) =====
{
  "intent_type": "선택한 intent",
  "confidence": 0.8,
  "keywords": ["키워드1", "키워드2"],
  "suggested_agents": ["agent1", "agent2"],
  "reasoning": "선택 이유"
}
```

**파일**: `app/framework/llm/prompt_templates.py` (신규)
```python
"""
프롬프트 템플릿 관리

Jinja2를 사용하여 템플릿 렌더링
"""

from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Dict, Any

class PromptTemplateManager:
    """프롬프트 템플릿 매니저"""

    def __init__(self, template_dir: str = "config/prompts"):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_name: str, **kwargs) -> str:
        """
        템플릿 렌더링

        Args:
            template_name: 템플릿 파일명 (예: "intent_analysis.txt")
            **kwargs: 템플릿 변수

        Returns:
            렌더링된 프롬프트
        """
        template = self.env.get_template(template_name)
        return template.render(**kwargs)

    def render_string(self, template_string: str, **kwargs) -> str:
        """
        문자열 템플릿 렌더링

        Args:
            template_string: 템플릿 문자열
            **kwargs: 템플릿 변수

        Returns:
            렌더링된 프롬프트
        """
        template = Template(template_string)
        return template.render(**kwargs)

# 싱글톤 인스턴스
_prompt_manager = None

def get_prompt_manager() -> PromptTemplateManager:
    """프롬프트 매니저 가져오기 (싱글톤)"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptTemplateManager()
    return _prompt_manager
```

**사용 예제**:
```python
# planning_agent.py
from app.framework.llm.prompt_templates import get_prompt_manager

class PlanningAgent:
    def __init__(self):
        self.prompt_manager = get_prompt_manager()

    async def analyze_intent(self, query: str, context: Dict):
        # 프롬프트 렌더링
        prompt = self.prompt_manager.render(
            "intent_analysis.txt",
            query=query,
            chat_history=context.get("chat_history", ""),
            intent_list=self._format_intent_list()
        )

        # LLM 호출
        result = await self.llm_service.call_llm(prompt=prompt)
        # ...
```

**작업**:
1. 모든 프롬프트 추출 (5개 파일)
   - `intent_analysis.txt`
   - `plan_generation.txt`
   - `keyword_extraction.txt`
   - `response_synthesis.txt`
   - `error_response.txt`

2. 코드 수정 (프롬프트 하드코딩 제거)

**검증**: 기존 프롬프트와 동일한 결과 생성 확인

#### 5.2 도메인별 커스터마이징 가이드 작성

**파일**: `docs/PROMPT_CUSTOMIZATION.md`
```markdown
# 프롬프트 커스터마이징 가이드

## 개요
프레임워크의 프롬프트는 `config/prompts/` 디렉토리에 템플릿 파일로 저장되어 있습니다.

## 템플릿 문법
Jinja2 템플릿 엔진을 사용합니다.

### 변수 삽입
\`\`\`
{{variable_name}}
\`\`\`

### 조건문
\`\`\`
{% if condition %}
  ...
{% endif %}
\`\`\`

### 반복문
\`\`\`
{% for item in items %}
  - {{item}}
{% endfor %}
\`\`\`

## 커스터마이징 예제

### Intent 분석 프롬프트 수정

...
```

### Phase 6: 프론트엔드 리팩토링 (2일)

#### 6.1 도메인 특화 코드 제거

**파일**: `frontend/components/chat-interface.tsx`

**제거 항목**:
1. 부동산 예제 질문
2. 하드코딩된 안내 메시지
3. 계약서 페이지 라우팅

**수정 후**:
```tsx
// 예제 질문 (설정에서 로드 또는 비활성화)
const exampleQuestions = [
  "도메인별 예제 질문 1",
  "도메인별 예제 질문 2",
  "도메인별 예제 질문 3",
]

// 또는 props로 받기
interface ChatInterfaceProps {
  exampleQuestions?: string[]
  welcomeMessage?: string
  onSplitView?: (agentType: PageType) => void
  currentSessionId?: string | null
}
```

#### 6.2 타입 범용화

**파일**: `frontend/lib/types.ts`

**수정**:
```typescript
// Before (부동산 특화)
export type IntentType =
  | "legal_consult"
  | "market_inquiry"
  | "loan_consult"
  | "contract_creation"
  | "contract_review"

// After (범용)
export type IntentType = string  // 동적으로 로드

// 또는 설정 파일에서 로드
export interface IntentDefinition {
  name: string
  displayName: string
  description: string
}

export const loadIntents = async (): Promise<IntentDefinition[]> => {
  // API에서 로드
  const response = await fetch("/api/v1/intents")
  return response.json()
}
```

#### 6.3 예제 컴포넌트 이동

**작업**:
```bash
# 계약서 페이지를 예제로 이동
mv frontend/components/lease_contract examples/frontend/hitl-form-example/

# README 작성
cat > examples/frontend/hitl-form-example/README.md << EOF
# HITL Form 예제

이 예제는 Human-in-the-Loop(HITL) 패턴을 사용한
폼 입력 및 승인 워크플로우를 보여줍니다.

## 구조
- \`lease_contract_page.tsx\` - 메인 페이지
- \`contract_form.tsx\` - 폼 컴포넌트
- \`contract_review.tsx\` - 검토 컴포넌트

## 사용 방법
1. 이 컴포넌트를 복사하여 프로젝트에 추가
2. 도메인별로 필드 수정
3. 백엔드 HITL 노드와 연동
EOF
```

### Phase 7: 문서화 (3일)

#### 7.1 아키텍처 문서

**파일**: `docs/ARCHITECTURE.md`
```markdown
# 아키텍처 가이드

## 개요
이 프레임워크는 LangGraph 0.6을 기반으로 한
도메인 독립적인 멀티 에이전트 시스템입니다.

## 핵심 개념

### 1. Team-based Supervisor 패턴
...

### 2. Agent Hierarchy
...

### 3. HITL (Human-in-the-Loop)
...

## 디렉토리 구조
...

## 데이터 흐름
...

## 확장 포인트
...
```

#### 7.2 빠른 시작 가이드

**파일**: `docs/QUICKSTART.md`
```markdown
# 빠른 시작 가이드

## 1. 설치

\`\`\`bash
# 클론
git clone https://github.com/your-repo/agent-framework.git
cd agent-framework

# 백엔드 설치
cd backend
pip install -r requirements.txt

# 프론트엔드 설치
cd ../frontend
npm install
\`\`\`

## 2. 설정

\`\`\`bash
# 환경 변수 설정
cp .env.example .env
# .env 파일 수정 (OPENAI_API_KEY 등)
\`\`\`

## 3. Intent 정의

\`\`\`yaml
# config/intents.yaml
intents:
  - name: "my_intent"
    display_name: "내 의도"
    keywords: ["키워드1", "키워드2"]
    suggested_agents: ["search_team"]
\`\`\`

## 4. 커스텀 Tool 작성

\`\`\`python
# app/domain/tools/my_tool.py
from app.framework.tools.base_tool import BaseTool

class MyTool(BaseTool):
    @property
    def metadata(self):
        return ToolMetadata(
            name="my_tool",
            description="내 도구"
        )

    async def execute(self, **kwargs):
        # 구현
        return {"result": "success"}
\`\`\`

## 5. Tool 등록

\`\`\`python
# app/domain/__init__.py
from app.framework.tools.tool_registry import ToolRegistry
from app.domain.tools.my_tool import MyTool

# 자동 등록
ToolRegistry.register(MyTool())
\`\`\`

## 6. 실행

\`\`\`bash
# 백엔드 실행
cd backend
uvicorn app.main:app --reload

# 프론트엔드 실행 (다른 터미널)
cd frontend
npm run dev
\`\`\`

## 7. 테스트

브라우저에서 `http://localhost:3000` 접속
\`\`\`

#### 7.3 커스터마이징 가이드

**파일**: `docs/CUSTOMIZATION.md`
```markdown
# 커스터마이징 가이드

## Intent 추가

### 1. YAML 파일 수정
...

### 2. 프롬프트 조정
...

## Agent 추가

### 1. BaseExecutor 상속
...

### 2. 워크플로우 정의
...

### 3. Supervisor에 등록
...

## Tool 추가

### 1. BaseTool 상속
...

### 2. Registry에 등록
...

### 3. Agent에서 사용
...

## HITL 워크플로우 구현

### 1. 백엔드 노드 작성
...

### 2. 프론트엔드 폼 작성
...

### 3. WebSocket 통신
...
```

#### 7.4 API 레퍼런스

**파일**: `docs/API_REFERENCE.md`
```markdown
# API 레퍼런스

## WebSocket API

### 연결
\`\`\`
ws://localhost:8000/api/v1/chat/ws/{session_id}
\`\`\`

### 메시지 프로토콜

#### Client → Server
...

#### Server → Client
...

## REST API

### POST /api/v1/chat/start
...

### GET /api/v1/chat/sessions
...
```

### Phase 8: 예제 및 템플릿 (2일)

#### 8.1 Quickstart 예제

**파일**: `examples/quickstart.py`
```python
"""
Quickstart 예제

가장 기본적인 에이전트 시스템 구성 예제
"""

import asyncio
from app.framework.supervisor.team_supervisor import TeamBasedSupervisor
from app.framework.foundation.context import create_default_llm_context
from app.framework.tools.tool_registry import ToolRegistry

# 1. 간단한 Tool 작성
from app.framework.tools.base_tool import BaseTool, ToolMetadata

class HelloWorldTool(BaseTool):
    @property
    def metadata(self):
        return ToolMetadata(
            name="hello_world",
            description="Hello World 출력",
            version="1.0.0"
        )

    async def execute(self, name: str = "World", **kwargs):
        return {
            "message": f"Hello, {name}!",
            "status": "success"
        }

# 2. Tool 등록
ToolRegistry.register(HelloWorldTool())

# 3. Supervisor 생성
async def main():
    # LLM Context
    llm_context = create_default_llm_context()

    # Supervisor 초기화
    supervisor = TeamBasedSupervisor(
        llm_context=llm_context,
        enable_checkpointing=False
    )

    # 쿼리 처리
    result = await supervisor.process_query_streaming(
        query="Hello World를 출력해주세요",
        session_id="quickstart_session"
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

#### 8.2 커스텀 Agent 예제

**파일**: `examples/custom_agent.py`
```python
"""
커스텀 Agent 예제

도메인별 Agent를 구현하는 방법을 보여줍니다.
"""

# ... (상세 예제 코드)
```

#### 8.3 HITL 예제

**파일**: `examples/hitl_workflow.py`
```python
"""
HITL (Human-in-the-Loop) 워크플로우 예제

사용자 승인이 필요한 워크플로우 구현 예제
"""

# ... (DocumentExecutor 기반 예제)
```

### Phase 9: 테스트 작성 (3일)

#### 9.1 Unit Tests

**파일**: `tests/unit/test_base_tool.py`
```python
import pytest
from app.framework.tools.base_tool import BaseTool, ToolMetadata
from app.framework.tools.tool_registry import ToolRegistry

class MockTool(BaseTool):
    @property
    def metadata(self):
        return ToolMetadata(
            name="mock_tool",
            description="Mock Tool",
            version="1.0.0"
        )

    async def execute(self, **kwargs):
        return {"result": "success"}

def test_tool_registration():
    """Tool 등록 테스트"""
    tool = MockTool()
    ToolRegistry.register(tool)

    retrieved = ToolRegistry.get("mock_tool")
    assert retrieved is not None
    assert retrieved.metadata.name == "mock_tool"

def test_tool_execution():
    """Tool 실행 테스트"""
    tool = MockTool()
    result = await tool.execute()

    assert result["result"] == "success"

# ... 추가 테스트
```

#### 9.2 Integration Tests

**파일**: `tests/integration/test_supervisor.py`
```python
import pytest
from app.framework.supervisor.team_supervisor import TeamBasedSupervisor

@pytest.mark.asyncio
async def test_supervisor_query_processing():
    """Supervisor 쿼리 처리 통합 테스트"""
    supervisor = TeamBasedSupervisor(enable_checkpointing=False)

    result = await supervisor.process_query_streaming(
        query="테스트 쿼리",
        session_id="test_session"
    )

    assert result is not None
    assert "final_response" in result

# ... 추가 테스트
```

#### 9.3 E2E Tests

**파일**: `tests/e2e/test_chat_flow.py`
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_chat_flow():
    """전체 채팅 플로우 E2E 테스트"""
    # 1. 세션 생성
    response = client.post("/api/v1/chat/start")
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # 2. WebSocket 연결
    with client.websocket_connect(f"/api/v1/chat/ws/{session_id}") as ws:
        # 3. 연결 확인
        data = ws.receive_json()
        assert data["type"] == "connected"

        # 4. 쿼리 전송
        ws.send_json({
            "type": "query",
            "query": "테스트 질문"
        })

        # 5. 응답 수신
        responses = []
        while True:
            data = ws.receive_json()
            responses.append(data)
            if data["type"] == "final_response":
                break

        # 6. 검증
        assert len(responses) > 0
        assert responses[-1]["type"] == "final_response"

# ... 추가 테스트
```

### Phase 10: 검증 및 마무리 (2일)

#### 10.1 체크리스트 작성

**파일**: `MIGRATION_CHECKLIST.md`
```markdown
# 마이그레이션 체크리스트

## 백엔드

- [ ] 모든 도메인 특화 Tool 제거
- [ ] 모든 도메인 특화 모델/스키마 제거
- [ ] 디렉토리 재구성 완료
- [ ] Import 경로 전체 수정
- [ ] Config 파일 통합
- [ ] 프롬프트 템플릿화
- [ ] Base Classes 구현
- [ ] Tool Registry 구현
- [ ] Intent Loader 구현
- [ ] 모든 Unit Tests 통과
- [ ] 모든 Integration Tests 통과

## 프론트엔드

- [ ] 도메인 특화 컴포넌트 제거
- [ ] 타입 범용화
- [ ] 예제 컴포넌트 이동
- [ ] Build 성공

## 문서

- [ ] ARCHITECTURE.md 작성
- [ ] QUICKSTART.md 작성
- [ ] CUSTOMIZATION.md 작성
- [ ] API_REFERENCE.md 작성
- [ ] PROMPT_CUSTOMIZATION.md 작성

## 예제

- [ ] quickstart.py 작성
- [ ] custom_agent.py 작성
- [ ] custom_tool.py 작성
- [ ] hitl_workflow.py 작성

## 검증

- [ ] 모든 테스트 통과
- [ ] 애플리케이션 정상 시작
- [ ] 예제 코드 실행 확인
- [ ] 문서 링크 확인
```

#### 10.2 최종 검증

1. **코드 품질 체크**
```bash
# Linting
flake8 backend/app
pylint backend/app

# Type checking
mypy backend/app

# Code coverage
pytest --cov=app tests/
```

2. **성능 테스트**
```bash
# Load testing
locust -f tests/load/locustfile.py
```

3. **보안 점검**
```bash
# Security scan
bandit -r backend/app
safety check
```

#### 10.3 버전 태깅 및 릴리즈

```bash
# Git 태그 생성
git tag -a v1.0.0-generic -m "Generic Framework v1.0.0"
git push origin v1.0.0-generic

# 릴리즈 노트 작성
# CHANGELOG.md 업데이트
```

---

## 6. 검증 및 테스트 계획

### 6.1 테스트 전략

#### Layer 1: Unit Tests
- **범위**: 개별 클래스/함수
- **도구**: pytest
- **목표 커버리지**: 80% 이상

**테스트 대상**:
- BaseTool
- BaseExecutor
- ToolRegistry
- IntentLoader
- ConfigLoader
- PromptTemplateManager

#### Layer 2: Integration Tests
- **범위**: 모듈 간 통합
- **도구**: pytest + mock

**테스트 시나리오**:
- Tool 등록 → Agent에서 사용
- Intent 로드 → Planning Agent 동작
- Supervisor → Teams → Tools 전체 흐름

#### Layer 3: E2E Tests
- **범위**: 전체 시스템
- **도구**: pytest + TestClient + WebSocket

**테스트 시나리오**:
- WebSocket 연결 → 쿼리 전송 → 응답 수신
- HITL 워크플로우 (interrupt → resume)
- 다중 세션 동시 처리

### 6.2 성능 테스트

#### Load Testing
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def send_query(self):
        self.client.post("/api/v1/chat/start")
        # WebSocket 시뮬레이션
```

**목표**:
- 동시 사용자: 100명
- 평균 응답 시간: < 3초
- 에러율: < 1%

#### Stress Testing
- 메모리 누수 체크
- DB 커넥션 풀 관리
- WebSocket 연결 관리

### 6.3 회귀 테스트

**기존 기능 검증**:
- [ ] 3-layer progress tracking 동작
- [ ] Long-term memory 저장/로드
- [ ] Data reuse optimization 동작
- [ ] HITL interrupt/resume 동작
- [ ] Checkpointing 동작

---

## 7. 문서화 계획

### 7.1 개발자 문서

#### 필수 문서
1. **ARCHITECTURE.md** - 시스템 아키텍처
2. **QUICKSTART.md** - 5분 내 시작
3. **CUSTOMIZATION.md** - 커스터마이징 방법
4. **API_REFERENCE.md** - API 레퍼런스
5. **DEPLOYMENT.md** - 배포 가이드

#### 선택 문서
6. **CONTRIBUTING.md** - 기여 가이드
7. **CHANGELOG.md** - 변경 이력
8. **FAQ.md** - 자주 묻는 질문

### 7.2 사용자 문서

1. **README.md** - 프로젝트 소개
2. **INSTALLATION.md** - 설치 가이드
3. **EXAMPLES.md** - 예제 모음

### 7.3 코드 문서화

#### Docstring 규칙
- Google Style Docstrings
- 모든 public 메서드에 docstring
- 예제 코드 포함

**예시**:
```python
def register_tool(self, tool: BaseTool) -> None:
    """
    Tool을 Registry에 등록합니다.

    Args:
        tool: 등록할 Tool 인스턴스

    Raises:
        ValueError: Tool 메타데이터가 유효하지 않은 경우

    Example:
        >>> tool = MyTool()
        >>> ToolRegistry.register(tool)
    """
```

---

## 8. 타임라인 요약

| Phase | 작업 | 예상 기간 | 우선순위 |
|-------|------|-----------|----------|
| 1 | 준비 및 백업 | 1일 | 최상 |
| 2 | 불필요한 코드 제거 | 2일 | 최상 |
| 3 | 디렉토리 재구성 | 1일 | 최상 |
| 4 | 코어 리팩토링 | 5일 | 최상 |
| 5 | 프롬프트 템플릿화 | 2일 | 상 |
| 6 | 프론트엔드 리팩토링 | 2일 | 상 |
| 7 | 문서화 | 3일 | 중 |
| 8 | 예제 및 템플릿 | 2일 | 중 |
| 9 | 테스트 작성 | 3일 | 상 |
| 10 | 검증 및 마무리 | 2일 | 최상 |
| **총계** | | **23일** | |

---

## 9. 리스크 관리

### 9.1 예상 리스크

| 리스크 | 발생 가능성 | 영향도 | 대응 방안 |
|--------|-------------|--------|-----------|
| Import 경로 수정 누락 | 중 | 상 | 스크립트 자동화, 단계별 테스트 |
| 기존 기능 손상 | 중 | 상 | 회귀 테스트, Git 태그 백업 |
| 설정 파일 오류 | 중 | 중 | 검증 스크립트, 기본값 제공 |
| 문서 불일치 | 상 | 하 | 코드 변경 시 문서 동시 업데이트 |
| 성능 저하 | 하 | 중 | 성능 테스트, 프로파일링 |

### 9.2 롤백 계획

**단계별 체크포인트**:
- Phase 2 완료 시: Git 태그 `v1.0-phase2`
- Phase 4 완료 시: Git 태그 `v1.0-phase4`
- Phase 6 완료 시: Git 태그 `v1.0-phase6`

**롤백 절차**:
```bash
# 특정 태그로 롤백
git checkout v1.0-phase4

# 새 브랜치 생성
git checkout -b recovery/phase4

# 문제 해결 후 재시도
```

---

## 10. 성공 기준

### 10.1 정량적 지표

- [ ] 코드 커버리지 80% 이상
- [ ] 모든 단위 테스트 통과
- [ ] 모든 통합 테스트 통과
- [ ] Linting 에러 0개
- [ ] Security scan 경고 0개
- [ ] 문서 완성도 100%

### 10.2 정성적 지표

- [ ] 새로운 도메인 Agent를 1시간 내 추가 가능
- [ ] 새로운 Tool을 30분 내 추가 가능
- [ ] Intent 추가가 YAML 수정만으로 가능
- [ ] 예제 코드가 모두 실행 가능
- [ ] 문서가 명확하고 이해하기 쉬움

### 10.3 검증 방법

**Dogfooding Test**:
1. 새로운 도메인 (예: E-commerce) Agent 구현
2. 문서만 보고 30분 내 구현 가능한지 확인
3. 팀원 피드백 수집

---

## 11. 다음 단계 (Post-Refactoring)

### 11.1 추가 기능

- [ ] Tool Marketplace (Community Tools)
- [ ] Agent Template Gallery
- [ ] Visual Workflow Builder
- [ ] Monitoring Dashboard
- [ ] A/B Testing Framework

### 11.2 최적화

- [ ] LLM 캐싱
- [ ] Parallel Tool Execution
- [ ] Response Streaming
- [ ] Database Query Optimization

---

## 12. 결론

본 계획서는 현재 부동산 챗봇을 범용 에이전트 프레임워크로 전환하기 위한
체계적이고 단계적인 로드맵을 제시합니다.

**핵심 원칙**:
1. **현재 완성도 유지**: 잘 작동하는 기능은 그대로 유지
2. **도메인 독립성**: 모든 도메인 특화 코드 분리
3. **확장성**: 플러그인 방식의 Tool/Agent 시스템
4. **문서화**: 명확한 가이드와 예제 제공

**예상 결과**:
- 어떤 도메인에도 적용 가능한 범용 프레임워크
- 빠른 프로토타이핑 및 개발 가능
- 유지보수 용이
- 커뮤니티 기여 활성화

---

**문서 버전**: 1.0
**최종 수정일**: 2025-10-28
**작성자**: Claude Code Assistant
