# 파일별 상세 처리 계획

**작성일**: 2025-10-28
**관련 문서**: [01_INITIALIZATION_MASTER_PLAN.md](01_INITIALIZATION_MASTER_PLAN.md)

---

## 백엔드 파일 처리 계획

### ✅ 유지 (수정 불필요)

| # | 파일 경로 | 설명 | 비고 |
|---|----------|------|------|
| 1 | `app/__init__.py` | 초기화 파일 | - |
| 2 | `app/db/__init__.py` | DB 초기화 | - |
| 3 | `app/db/postgre_db.py` | PostgreSQL 연결 | 완벽함 |
| 4 | `app/db/mongo_db.py` | MongoDB 연결 | 선택적 유지 |
| 5 | `app/api/ws_manager.py` | WebSocket 관리 | 완벽함 |
| 6 | `app/api/error_handlers.py` | 에러 핸들링 | - |
| 7 | `app/models/chat.py` | Chat 모델 | 범용 |
| 8 | `app/models/users.py` | Users 모델 | 범용 |

**작업**: 없음

---

### ⚠️ 리팩토링 (범용화 필요)

#### 1. `app/main.py`

**현재 문제**:
```python
app = FastAPI(
    title="Chatbot App API",
    description="부동산 AI 챗봇 <도와줘 홈즈냥즈>",  # ← 하드코딩
    version="0.0.1",
    lifespan=lifespan
)
```

**수정 방안**:
```python
from app.core.config_loader import get_app_config

config = get_app_config()

app = FastAPI(
    title=config.application["name"],
    description=config.application["description"],
    version=config.application["version"],
    lifespan=lifespan
)
```

**파일 수정**:
- [ ] `app/main.py` 라인 130-135 수정
- [ ] Import 추가: `from app.core.config_loader import get_app_config`

---

#### 2. `app/core/config.py` → `app/core/config_loader.py`

**작업**:
1. **삭제**: `app/core/config.py` 전체
2. **생성**: `app/core/config_loader.py`
3. **생성**: `config/app.yaml`
4. **생성**: `config/framework.yaml`

**새 파일 내용**:
- `config/app.yaml`: 애플리케이션 설정 (DB, API, Memory 등)
- `config/framework.yaml`: 프레임워크 설정 (LLM, Agents, Tools 등)
- `app/core/config_loader.py`: YAML 로더 + Pydantic 모델

**의존 파일 수정**:
```bash
# 전체 프로젝트에서 import 경로 변경
find backend/app -name "*.py" -exec sed -i 's/from app.core.config import settings/from app.core.config_loader import get_app_config/g' {} \;

# 사용법 변경
# Before: settings.POSTGRES_HOST
# After: get_app_config().database.postgres["host"]
```

**변경 영향 파일** (약 15개):
- `app/main.py`
- `app/api/chat_api.py`
- `app/api/postgres_session_manager.py`
- `app/agent/supervisor/team_supervisor.py`
- `app/agent/foundation/checkpointer.py`
- 등...

---

#### 3. `app/agent/foundation/config.py` → 삭제, `config/framework.yaml`로 이전

**작업**:
1. **삭제**: `app/agent/foundation/config.py`
2. **생성**: `config/framework.yaml`
3. **수정**: 모든 import 경로

**Before**:
```python
from app.agent.foundation.config import Config

db_path = Config.DATABASES["real_estate_listings"]
model = Config.DEFAULT_MODELS["intent"]
```

**After**:
```python
from app.core.config_loader import get_framework_config

config = get_framework_config()
# YAML에서 동적으로 로드
```

**의존 파일** (약 20개):
- 모든 Executor 파일
- Supervisor 파일
- LLM Service 파일

---

#### 4. `app/agent/cognitive_agents/planning_agent.py`

**문제점**:
```python
class IntentType(Enum):
    LEGAL_CONSULT = "법률상담"
    MARKET_INQUIRY = "시세조회"
    LOAN_CONSULT = "대출상담"
    # ... 부동산 전용
```

**수정**:
1. `IntentType` Enum 삭제
2. `IntentLoader` 추가하여 YAML에서 로드
3. `IntentResult`의 `intent_type` 타입을 `str`로 변경

**작업**:
- [ ] IntentType Enum 제거
- [ ] `app/framework/agents/cognitive/intent_loader.py` 생성
- [ ] `config/intents.yaml` 생성
- [ ] `analyze_intent()` 메서드 수정 - YAML 기반 매칭
- [ ] 테스트 작성

**예상 라인 수정**:
- 라인 32-43: IntentType 삭제
- 라인 95-100: `__init__()` 수정
- 라인 200-300: `analyze_intent()` 수정

---

#### 5. `app/agent/execution_agents/search_executor.py`

**문제점**:
```python
# 부동산 Tool 직접 사용
from app.agent.tools.hybrid_legal_search import HybridLegalSearch
from app.agent.tools.market_data_tool import MarketDataTool
from app.agent.tools.real_estate_search_tool import RealEstateSearchTool
from app.agent.tools.loan_data_tool import LoanDataTool
```

**수정**:
1. 직접 import 제거
2. `BaseExecutor` 패턴 적용
3. `_register_tools()` 메서드로 Tool 등록
4. `ToolRegistry`에서 Tool 가져오기

**작업**:
- [ ] 부동산 Tool import 제거
- [ ] `BaseExecutor` 상속 구조로 리팩토링
- [ ] `_register_tools()` 추상 메서드 구현
- [ ] 템플릿 메서드 패턴 적용
- [ ] `examples/custom_search_executor.py`로 예제 이동

**새 구조**:
```python
class SearchExecutor(BaseExecutor):
    """범용 검색 Executor (템플릿)"""

    def _register_tools(self) -> Dict[str, BaseTool]:
        """사용자가 override"""
        return {}

    async def execute(self, shared_state: SharedState, **kwargs):
        """템플릿 메서드 패턴"""
        # Step 1-4: 범용 워크플로우
        pass
```

---

#### 6. `app/agent/execution_agents/analysis_executor.py`

**문제점**:
- 부동산 분석 로직 하드코딩

**수정**:
- `BaseAnalysisExecutor`로 템플릿화
- 예제로 이동

**작업**:
- [ ] 부동산 로직 제거
- [ ] 범용 분석 워크플로우만 남김
- [ ] `examples/custom_analysis_executor.py` 생성

---

#### 7. `app/agent/execution_agents/document_executor.py`

**문제점**:
- 계약서 생성 로직 (부동산 특화)

**수정**:
- HITL 패턴은 유지 (핵심 기능)
- 계약서 관련 로직은 예제로 분리

**작업**:
- [ ] 계약서 로직을 `examples/lease_contract_executor.py`로 이동
- [ ] `BaseDocumentExecutor` 생성 (HITL 템플릿)
- [ ] 범용 문서 생성 워크플로우 유지

---

#### 8. `app/agent/supervisor/team_supervisor.py`

**문제점**:
```python
def _generate_out_of_scope_response(self, state: MainSupervisorState):
    message = """안녕하세요! 저는 부동산 전문 상담 AI입니다.
    ...
    **제가 도와드릴 수 있는 분야:**
    - 전세/월세/매매 관련 법률 상담  # ← 하드코딩
    """
```

**수정**:
- 안내 메시지를 프롬프트 템플릿으로 분리
- `config/prompts/out_of_scope_message.txt` 생성

**작업**:
- [ ] 라인 1572-1619: 메시지 하드코딩 제거
- [ ] 프롬프트 템플릿 사용
- [ ] `_get_task_name_for_agent()` - IntentType 하드코딩 제거
- [ ] `_get_task_description_for_agent()` - 부동산 문구 제거

---

#### 9. `app/api/chat_api.py`

**문제점**:
```python
user_id = 1  # 🔧 임시: 테스트용 하드코딩  # ← 다수 위치
```

**수정**:
- 인증 시스템 준비 (추후 연동 가능하도록)
- 현재는 세션에서 추출하도록 수정

**작업**:
- [ ] `user_id = 1` 하드코딩 찾아서 주석 정리
- [ ] 세션에서 user_id 추출 로직 추가 (Optional)
- [ ] TODO 주석 추가: "// TODO: Implement authentication"

---

#### 10. `app/api/schemas.py`

**문제점**:
- 부동산 스키마 혼재

**수정**:
- 범용 스키마만 남기고 나머지 제거

**작업**:
- [ ] Real estate 관련 Schema 제거
- [ ] Trust 관련 Schema 제거
- [ ] Chat 관련 Schema만 유지

---

### ❌ 제거 (도메인 특화)

#### Tools 디렉토리

| # | 파일 | 이유 | 작업 |
|---|------|------|------|
| 1 | `app/agent/tools/contract_analysis_tool.py` | 부동산 계약서 분석 | 삭제 |
| 2 | `app/agent/tools/loan_simulator_tool.py` | 대출 시뮬레이션 | 삭제 |
| 3 | `app/agent/tools/roi_calculator_tool.py` | ROI 계산 | 삭제 |
| 4 | `app/agent/tools/market_analysis_tool.py` | 시장 분석 | 삭제 |
| 5 | `app/agent/tools/market_data_tool.py` | 시장 데이터 | 삭제 |
| 6 | `app/agent/tools/real_estate_search_tool.py` | 부동산 검색 | 삭제 |
| 7 | `app/agent/tools/loan_data_tool.py` | 대출 데이터 | 삭제 |
| 8 | `app/agent/tools/infrastructure_tool.py` | 인프라 조회 | 삭제 |
| 9 | `app/agent/tools/policy_matcher_tool.py` | 정책 매칭 | 삭제 |
| 10 | `app/agent/tools/hybrid_legal_search.py` | 법률 검색 | 삭제 |
| 11 | `app/agent/tools/lease_contract_generator_tool.py` | 계약서 생성 | 삭제 |

**명령어**:
```bash
cd backend/app/agent/tools
rm contract_analysis_tool.py
rm loan_simulator_tool.py
rm roi_calculator_tool.py
rm market_analysis_tool.py
rm market_data_tool.py
rm real_estate_search_tool.py
rm loan_data_tool.py
rm infrastructure_tool.py
rm policy_matcher_tool.py
rm hybrid_legal_search.py
rm lease_contract_generator_tool.py
```

**`__init__.py` 수정**:
```python
# Before
from app.agent.tools.contract_analysis_tool import ContractAnalysisTool
# ... 많은 import

# After
# 예제 Tool만 남김 (또는 비워둠)
```

---

#### Models & Schemas

| # | 파일 | 이유 | 작업 |
|---|------|------|------|
| 1 | `app/models/service/real_estate.py` | 부동산 서비스 | 삭제 |
| 2 | `app/models/service/trust.py` | 신탁 서비스 | 삭제 |
| 3 | `app/schemas/real_estate.py` | 부동산 스키마 | 삭제 |
| 4 | `app/schemas/trust.py` | 신탁 스키마 | 삭제 |

**명령어**:
```bash
rm app/models/service/real_estate.py
rm app/models/service/trust.py
rm app/schemas/real_estate.py
rm app/schemas/trust.py
```

---

#### Utils

| # | 파일 | 이유 | 작업 |
|---|------|------|------|
| 1 | `app/utils/building_api.py` | 건물 API | 삭제 |
| 2 | `app/utils/data_collector.py` | 데이터 수집 | 삭제 |
| 3 | `app/utils/geocode_aprtments.py` | 지오코딩 | 삭제 |
| 4 | `app/utils/database_config.py` | DB 설정 (중복) | 삭제 |

**명령어**:
```bash
rm app/utils/building_api.py
rm app/utils/data_collector.py
rm app/utils/geocode_aprtments.py
rm app/utils/database_config.py
```

---

#### Scripts & Old

| # | 디렉토리/파일 | 이유 | 작업 |
|---|--------------|------|------|
| 1 | `backend/scripts/` | 데이터 임포트 스크립트 | 전체 삭제 |
| 2 | `app/agent/foundation/old/` | 구버전 코드 | 전체 삭제 |
| 3 | `app/api/old/` | 구버전 코드 | 전체 삭제 |
| 4 | `app/crud/` | 빈 디렉토리 | 전체 삭제 |

**명령어**:
```bash
rm -rf backend/scripts/
rm -rf app/agent/foundation/old/
rm -rf app/api/old/
rm -rf app/crud/
```

---

### 🆕 신규 생성

#### Base Classes

| # | 파일 | 목적 | 우선순위 |
|---|------|------|----------|
| 1 | `app/framework/agents/base/base_agent.py` | Abstract Agent | 최상 |
| 2 | `app/framework/agents/base/base_executor.py` | Abstract Executor | 최상 |
| 3 | `app/framework/agents/base/interfaces.py` | Agent Interfaces | 상 |
| 4 | `app/framework/tools/base_tool.py` | Abstract Tool | 최상 |
| 5 | `app/framework/tools/tool_registry.py` | Tool Registry | 최상 |

---

#### Configuration

| # | 파일 | 목적 | 우선순위 |
|---|------|------|----------|
| 1 | `config/app.yaml` | 애플리케이션 설정 | 최상 |
| 2 | `config/framework.yaml` | 프레임워크 설정 | 최상 |
| 3 | `config/intents.yaml` | Intent 정의 | 최상 |
| 4 | `config/agents.yaml` | Agent 설정 | 상 |
| 5 | `app/core/config_loader.py` | YAML 로더 | 최상 |
| 6 | `app/framework/agents/cognitive/intent_loader.py` | Intent 로더 | 최상 |

---

#### Prompts

| # | 파일 | 목적 | 우선순위 |
|---|------|------|----------|
| 1 | `config/prompts/intent_analysis.txt` | Intent 분석 | 상 |
| 2 | `config/prompts/plan_generation.txt` | 계획 생성 | 상 |
| 3 | `config/prompts/keyword_extraction.txt` | 키워드 추출 | 중 |
| 4 | `config/prompts/response_synthesis.txt` | 응답 합성 | 상 |
| 5 | `config/prompts/out_of_scope_message.txt` | 범위 외 안내 | 중 |
| 6 | `app/framework/llm/prompt_templates.py` | 템플릿 매니저 | 상 |

---

#### Examples

| # | 파일 | 목적 | 우선순위 |
|---|------|------|----------|
| 1 | `examples/quickstart.py` | 빠른 시작 | 최상 |
| 2 | `examples/custom_agent.py` | 커스텀 Agent | 상 |
| 3 | `examples/custom_tool.py` | 커스텀 Tool | 상 |
| 4 | `examples/custom_search_executor.py` | 검색 Executor | 상 |
| 5 | `examples/custom_analysis_executor.py` | 분석 Executor | 중 |
| 6 | `examples/hitl_workflow.py` | HITL 예제 | 상 |
| 7 | `examples/lease_contract_executor.py` | 계약서 생성 (부동산 예제) | 중 |

---

#### Documentation

| # | 파일 | 목적 | 우선순위 |
|---|------|------|----------|
| 1 | `docs/ARCHITECTURE.md` | 아키텍처 가이드 | 최상 |
| 2 | `docs/QUICKSTART.md` | 빠른 시작 가이드 | 최상 |
| 3 | `docs/CUSTOMIZATION.md` | 커스터마이징 가이드 | 상 |
| 4 | `docs/API_REFERENCE.md` | API 레퍼런스 | 상 |
| 5 | `docs/PROMPT_CUSTOMIZATION.md` | 프롬프트 가이드 | 중 |
| 6 | `docs/DEPLOYMENT.md` | 배포 가이드 | 중 |
| 7 | `README.md` | 프로젝트 소개 (수정) | 최상 |

---

#### Tests

| # | 파일 | 목적 | 우선순위 |
|---|------|------|----------|
| 1 | `tests/unit/test_base_tool.py` | BaseTool 테스트 | 상 |
| 2 | `tests/unit/test_tool_registry.py` | ToolRegistry 테스트 | 상 |
| 3 | `tests/unit/test_intent_loader.py` | IntentLoader 테스트 | 상 |
| 4 | `tests/unit/test_config_loader.py` | ConfigLoader 테스트 | 상 |
| 5 | `tests/integration/test_supervisor.py` | Supervisor 통합 테스트 | 상 |
| 6 | `tests/e2e/test_chat_flow.py` | 채팅 E2E 테스트 | 중 |

---

## 프론트엔드 파일 처리 계획

### ✅ 유지

| # | 파일 | 설명 | 비고 |
|---|------|------|------|
| 1 | `components/ui/*` | UI 라이브러리 | shadcn/ui |
| 2 | `components/progress-container.tsx` | 프로그레스 UI | 완벽함 |
| 3 | `components/step-item.tsx` | 단계 표시 | - |
| 4 | `components/session-list.tsx` | 세션 목록 | - |
| 5 | `lib/api.ts` | API 클라이언트 | - |
| 6 | `lib/utils.ts` | 유틸리티 | - |
| 7 | `lib/ws.ts` | WebSocket 클라이언트 | - |
| 8 | `hooks/use-toast.ts` | Toast hook | - |
| 9 | `hooks/use-mobile.ts` | Mobile hook | - |
| 10 | `hooks/use-session.ts` | Session hook | - |

---

### ⚠️ 리팩토링

#### 1. `components/chat-interface.tsx`

**문제점**:
```tsx
const exampleQuestions = [
  "강남구 아파트 전세 시세 알려주세요",  // ← 부동산 예제
  "전세금 5% 인상이 가능한가요?",
  "임대차 계약서 검토해주세요",
]
```

**수정**:
```tsx
interface ChatInterfaceProps {
  exampleQuestions?: string[]  // Props로 받기
  welcomeMessage?: string
  // ...
}

// 또는 API에서 로드
const [exampleQuestions, setExampleQuestions] = useState<string[]>([])

useEffect(() => {
  // Load from API
  fetch("/api/v1/config/example-questions")
    .then(res => res.json())
    .then(data => setExampleQuestions(data))
}, [])
```

**작업**:
- [ ] 부동산 예제 질문 제거
- [ ] Props 또는 API 로드로 변경
- [ ] Welcome 메시지 Props로 받기

---

#### 2. `components/answer-display.tsx`

**문제점**:
- 부동산 관련 아이콘/메시지 하드코딩

**수정**:
- 범용 아이콘으로 변경
- 조건부 렌더링

**작업**:
- [ ] 부동산 아이콘 제거
- [ ] 범용 아이콘으로 교체

---

#### 3. `lib/types.ts`

**문제점**:
```typescript
export type IntentType =
  | "legal_consult"    // ← 부동산 특화
  | "market_inquiry"
  | "loan_consult"
  | "contract_creation"
```

**수정**:
```typescript
export type IntentType = string  // 동적 타입

export interface IntentDefinition {
  name: string
  displayName: string
  description: string
}
```

**작업**:
- [ ] IntentType을 string으로 변경
- [ ] IntentDefinition 인터페이스 추가
- [ ] 타입 체크 수정

---

### ❌ 제거

| # | 파일/디렉토리 | 이유 | 작업 |
|---|--------------|------|------|
| 1 | `components/agents/` | 부동산 Agent UI | 전체 삭제 |
| 2 | `components/map-interface.tsx` | 지도 (도메인 특화) | 삭제 |
| 3 | `lib/district-coordinates.ts` | 지역 좌표 | 삭제 |
| 4 | `lib/clustering.ts` | 클러스터링 | 삭제 |

**명령어**:
```bash
rm -rf frontend/components/agents/
rm frontend/components/map-interface.tsx
rm frontend/lib/district-coordinates.ts
rm frontend/lib/clustering.ts
```

---

### 🔄 템플릿화 (예제로 이동)

| # | 파일/디렉토리 | 목적지 | 비고 |
|---|--------------|--------|------|
| 1 | `components/lease_contract/` | `examples/frontend/hitl-form-example/` | HITL 예제 |

**명령어**:
```bash
mkdir -p examples/frontend/hitl-form-example
mv frontend/components/lease_contract/* examples/frontend/hitl-form-example/
```

**README 작성**:
```bash
cat > examples/frontend/hitl-form-example/README.md << 'EOF'
# HITL Form 예제

Human-in-the-Loop 패턴을 사용한 폼 입력 워크플로우 예제

## 사용 방법
1. 이 디렉토리를 프로젝트에 복사
2. 도메인별로 필드 수정
3. 백엔드 HITL 노드와 연동

## 참고
- [HITL 가이드](../../../docs/HITL_GUIDE.md)
EOF
```

---

## 작업 순서 및 체크리스트

### Phase 1: 백업 및 준비

- [ ] Git 태그 생성: `git tag v0.1.0-real-estate`
- [ ] 전체 백업: `cp -r beta_v001 beta_v001_backup_$(date +%Y%m%d)`
- [ ] 브랜치 생성: `git checkout -b feature/generic-framework`

### Phase 2: 제거 작업

- [ ] Tools 디렉토리 정리 (11개 파일 삭제)
- [ ] Models/Schemas 정리 (4개 파일 삭제)
- [ ] Utils 정리 (4개 파일 삭제)
- [ ] Scripts/Old 정리 (3개 디렉토리 삭제)
- [ ] 프론트엔드 정리 (4개 파일/디렉토리 삭제/이동)
- [ ] Git commit: "chore: remove domain-specific code"

### Phase 3: 디렉토리 재구성

- [ ] `app/framework/` 디렉토리 생성
- [ ] 파일 이동 (agent → framework)
- [ ] `app/domain/` 디렉토리 생성
- [ ] `config/` 디렉토리 생성
- [ ] `examples/` 디렉토리 생성
- [ ] Git commit: "refactor: reorganize directory structure"

### Phase 4: Base Classes 생성

- [ ] `base_agent.py` 작성
- [ ] `base_executor.py` 작성
- [ ] `base_tool.py` 작성
- [ ] `tool_registry.py` 작성
- [ ] Unit tests 작성
- [ ] Git commit: "feat: add base classes and tool registry"

### Phase 5: Configuration 통합

- [ ] `config/app.yaml` 작성
- [ ] `config/framework.yaml` 작성
- [ ] `config/intents.yaml` 작성
- [ ] `config_loader.py` 작성
- [ ] `intent_loader.py` 작성
- [ ] 기존 config 파일 삭제
- [ ] Git commit: "refactor: unify configuration system"

### Phase 6: Intent System 리팩토링

- [ ] `planning_agent.py` 수정 (IntentType 제거)
- [ ] YAML 기반 Intent 로드 구현
- [ ] 기존 테스트 수정
- [ ] Git commit: "refactor: make intent system configurable"

### Phase 7: Executor 리팩토링

- [ ] `search_executor.py` 템플릿화
- [ ] `analysis_executor.py` 템플릿화
- [ ] `document_executor.py` 템플릿화
- [ ] 예제 파일 생성
- [ ] Git commit: "refactor: templatize executors"

### Phase 8: Import 경로 전체 수정

- [ ] 자동화 스크립트 작성 (`fix_imports.py`)
- [ ] 스크립트 실행
- [ ] 수동 검증 및 수정
- [ ] 테스트 실행
- [ ] Git commit: "refactor: fix all import paths"

### Phase 9: Prompt 템플릿화

- [ ] 프롬프트 추출 (5개 파일)
- [ ] `prompt_templates.py` 작성
- [ ] 코드 수정 (프롬프트 하드코딩 제거)
- [ ] Git commit: "refactor: templatize prompts"

### Phase 10: 프론트엔드 리팩토링

- [ ] `chat-interface.tsx` 수정
- [ ] `answer-display.tsx` 수정
- [ ] `types.ts` 범용화
- [ ] Build 테스트
- [ ] Git commit: "refactor: generalize frontend"

### Phase 11: 문서화

- [ ] `ARCHITECTURE.md` 작성
- [ ] `QUICKSTART.md` 작성
- [ ] `CUSTOMIZATION.md` 작성
- [ ] `API_REFERENCE.md` 작성
- [ ] `README.md` 업데이트
- [ ] Git commit: "docs: add comprehensive documentation"

### Phase 12: 예제 작성

- [ ] `quickstart.py` 작성 및 테스트
- [ ] `custom_agent.py` 작성
- [ ] `custom_tool.py` 작성
- [ ] 예제 README 작성
- [ ] Git commit: "docs: add examples"

### Phase 13: 테스트 작성

- [ ] Unit tests (5개 파일)
- [ ] Integration tests (3개 파일)
- [ ] E2E tests (2개 파일)
- [ ] 모든 테스트 통과
- [ ] Git commit: "test: add comprehensive tests"

### Phase 14: 최종 검증

- [ ] Linting (flake8, pylint)
- [ ] Type checking (mypy)
- [ ] Security scan (bandit)
- [ ] 문서 링크 확인
- [ ] 예제 실행 확인
- [ ] Git commit: "chore: final cleanup"

### Phase 15: 릴리즈

- [ ] `CHANGELOG.md` 작성
- [ ] Git 태그: `v1.0.0-generic`
- [ ] Pull Request 생성
- [ ] 코드 리뷰
- [ ] Merge to main

---

## 검증 스크립트

### 자동화된 검증

```bash
# scripts/verify_refactoring.sh
#!/bin/bash

echo "🔍 Starting verification..."

# 1. Check for domain-specific imports
echo "\n📦 Checking for domain-specific imports..."
grep -r "real_estate" backend/app/framework/ && echo "❌ Found real_estate imports" || echo "✅ No real_estate imports"
grep -r "loan" backend/app/framework/ && echo "❌ Found loan imports" || echo "✅ No loan imports"
grep -r "contract" backend/app/framework/ && echo "❌ Found contract imports" || echo "✅ No contract imports"

# 2. Check for hardcoded strings
echo "\n📝 Checking for hardcoded strings..."
grep -r "부동산" backend/app/framework/ && echo "❌ Found hardcoded Korean strings" || echo "✅ No hardcoded strings"
grep -r "전세" backend/app/framework/ && echo "❌ Found hardcoded rental terms" || echo "✅ No hardcoded terms"

# 3. Run tests
echo "\n🧪 Running tests..."
pytest backend/tests/ --cov=app --cov-report=term-missing

# 4. Check linting
echo "\n🎨 Running linters..."
flake8 backend/app/framework/
pylint backend/app/framework/

# 5. Check type hints
echo "\n🔤 Running type checker..."
mypy backend/app/framework/

echo "\n✅ Verification complete!"
```

---

**문서 버전**: 1.0
**최종 수정일**: 2025-10-28
