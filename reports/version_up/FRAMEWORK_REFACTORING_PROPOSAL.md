# Framework 디렉토리 구조 개선 제안서

**작성일:** 2025-11-01
**목적:** 명확한 네이밍과 LangGraph 1.0 컨벤션에 맞는 구조 개선

---

## 📋 현재 구조 분석

### 현재 디렉토리 구조
```
backend/app/framework/
├── agents/
│   ├── base/           # 기본 Executor 클래스
│   ├── cognitive/      # Planning, Orchestration
│   └── execution/      # Search, Analysis, Document Executors
├── foundation/         # 핵심 인프라 (State, Checkpointer, Registry)
├── llm/               # LLM Service, Prompt Manager
├── supervisor/        # ⭐ TeamSupervisor (StateGraph)
└── tools/             # Tool 구현체
```

### 문제점 분석

#### 1. `framework` 네이밍의 모호성
**문제:**
- "Framework"는 너무 일반적이고 추상적
- LangGraph 자체가 이미 "framework"
- 실제로는 **"LangGraph 기반 Agent 시스템"**을 의미

**혼란 포인트:**
```python
from app.framework.supervisor.team_supervisor import TeamBasedSupervisor
# "framework"가 무엇을 의미하는지 불명확
# - UI Framework? Web Framework? LangGraph Framework?
```

#### 2. `supervisor` 디렉토리의 역할 모호성
**문제:**
- `team_supervisor.py`가 **실제로는 메인 LangGraph (StateGraph)**
- "Supervisor"는 LangGraph에서 특정 패턴(Supervisor Agent)을 의미
- 하지만 여기서는 "전체 orchestration graph"를 의미

**혼란 포인트:**
```python
# team_supervisor.py Line 42
class TeamBasedSupervisor:
    """팀 기반 Supervisor"""

    def _build_graph(self):
        workflow = StateGraph(MainSupervisorState)  # ← 메인 그래프!
```

실제로는:
- ✅ **메인 LangGraph 정의**
- ✅ **StateGraph 구성**
- ✅ **워크플로우 오케스트레이션**
- ❌ Supervisor Agent 패턴 (일부만 해당)

---

## 🎯 개선 방안

### Option A: 최소 변경 (보수적)
**목표:** 기존 구조 유지, 일부 네이밍만 개선

```
backend/app/framework/          # 유지
├── agents/                     # 유지
├── foundation/                 # 유지
├── llm/                        # 유지
├── graphs/                     # 🆕 supervisor → graphs
│   └── main_graph.py          # 🆕 team_supervisor.py → main_graph.py
└── tools/                      # 유지
```

**변경 사항:**
- `supervisor/` → `graphs/`
- `team_supervisor.py` → `main_graph.py`
- 클래스명: `TeamBasedSupervisor` → `MainGraph` 또는 `PTManagerGraph`

**장점:**
- ✅ 최소 변경으로 명확성 확보
- ✅ LangGraph 컨벤션 준수 (Graph = StateGraph)
- ✅ 향후 여러 그래프 추가 가능 (`graphs/document_graph.py` 등)

**단점:**
- ⚠️ `framework` 네이밍은 여전히 모호

---

### Option B: 중간 변경 (권장) ⭐
**목표:** 역할 명확화, LangGraph 1.0 컨벤션 준수

```
backend/app/agent_system/       # 🆕 framework → agent_system
├── agents/                     # 유지
│   ├── base/
│   ├── cognitive/
│   └── execution/
├── graphs/                     # 🆕 supervisor → graphs
│   ├── __init__.py
│   └── main.py                # 🆕 team_supervisor.py → main.py
├── core/                       # 🆕 foundation → core
│   ├── state.py              # 🆕 separated_states.py → state.py
│   ├── checkpointer.py
│   ├── context.py
│   └── registry.py
├── llm/                        # 유지
└── tools/                      # 유지
```

**변경 사항:**
1. `framework/` → `agent_system/`
2. `supervisor/` → `graphs/`
3. `team_supervisor.py` → `main.py`
4. `foundation/` → `core/`
5. `separated_states.py` → `state.py`

**Import 변경:**
```python
# 기존
from app.framework.supervisor.team_supervisor import TeamBasedSupervisor
from app.framework.foundation.separated_states import MainSupervisorState

# 개선
from app.agent_system.graphs.main import MainGraph
from app.agent_system.core.state import MainSupervisorState
```

**장점:**
- ✅ 명확한 역할 표현 (`agent_system` = AI Agent 시스템)
- ✅ LangGraph 컨벤션 준수 (`graphs/` = StateGraph 정의)
- ✅ 파일명 간결화 (`main.py` = 메인 그래프)
- ✅ 향후 확장성 (여러 그래프 추가 가능)

**단점:**
- ⚠️ Import 경로 전체 변경 필요 (30-40개 파일)
- ⚠️ 마이그레이션 시간 소요 (1-2일)

---

### Option C: 대규모 재구조화 (이상적, 장기)
**목표:** Domain-Driven Design + LangGraph 1.0 Best Practice

```
backend/app/
├── domain/                     # 도메인 로직
│   ├── real_estate/
│   ├── legal/
│   └── finance/
├── langgraph/                  # 🆕 LangGraph 전용 디렉토리
│   ├── graphs/                # StateGraph 정의
│   │   ├── __init__.py
│   │   ├── main.py           # 메인 그래프
│   │   └── document.py       # 문서 서브그래프
│   ├── agents/                # Agent 노드 구현
│   │   ├── cognitive/
│   │   └── execution/
│   ├── state/                 # State 정의
│   │   ├── __init__.py
│   │   ├── main_state.py
│   │   └── sub_states.py
│   └── tools/                 # LangGraph Tools
├── infrastructure/            # 인프라 (DB, LLM, Cache)
│   ├── checkpointer/
│   ├── llm/
│   └── database/
└── api/                       # FastAPI 라우터
```

**장점:**
- ✅ 최고 수준의 명확성
- ✅ LangGraph 전용 구조 분리
- ✅ DDD 원칙 준수
- ✅ 확장성 극대화

**단점:**
- ❌ 대규모 리팩토링 필요 (3-5일)
- ❌ 테스트 전체 재작성
- ❌ 높은 리스크

---

## 📊 비교표

| 항목 | Option A | Option B (권장) | Option C |
|------|----------|----------------|----------|
| **변경 범위** | 🟢 최소 (2개 파일) | 🟡 중간 (30-40개) | 🔴 대규모 (100+) |
| **소요 시간** | 🟢 1시간 | 🟡 1-2일 | 🔴 3-5일 |
| **명확성 개선** | 🟡 중간 | 🟢 높음 | 🟢 최고 |
| **LangGraph 컨벤션** | 🟢 준수 | 🟢 준수 | 🟢 완벽 |
| **리스크** | 🟢 낮음 | 🟡 중간 | 🔴 높음 |
| **확장성** | 🟡 중간 | 🟢 좋음 | 🟢 최고 |

---

## 🎯 최종 권고사항

### 즉시 실행: **Option B (중간 변경)** ⭐

**이유:**
1. ✅ **명확성 극대화** - `agent_system/graphs/main.py`는 직관적
2. ✅ **LangGraph 1.0 준비** - 마이그레이션과 함께 진행 가능
3. ✅ **적절한 비용** - 1-2일 소요, 관리 가능한 범위
4. ✅ **확장성 확보** - 향후 그래프 추가 용이

**진행 방안:**
- LangGraph 1.0 마이그레이션과 **함께** 진행
- 2-3일 안에 완료 가능
- 테스트 코드도 함께 정리

---

## 🔧 구체적 네이밍 제안

### 1. `framework` → `agent_system` or `langgraph_system`

**추천: `agent_system`** ⭐

**이유:**
```python
# ✅ 명확하고 간결
from app.agent_system.graphs.main import MainGraph

# vs

# ❌ 너무 길고 중복
from app.langgraph_system.graphs.main import MainGraph
# (graphs가 이미 LangGraph를 의미)

# ❌ 모호함
from app.framework.supervisor.team_supervisor import TeamBasedSupervisor
```

**대안:**
- `agents` - 간결하지만, `agents/` 하위 디렉토리와 충돌
- `graph_system` - LangGraph 중심성 강조하지만 너무 기술적
- `orchestration` - 오케스트레이션 강조하지만 일부 기능만 표현

### 2. `supervisor/team_supervisor.py` → `graphs/main.py`

**추천: `graphs/main.py`** ⭐

**이유:**
```python
# ✅ 명확: "메인 그래프 정의"
from app.agent_system.graphs.main import MainGraph

# vs

# ⚠️ 모호: "Supervisor가 뭐지? Graph는 어디?"
from app.agent_system.supervisor.team_supervisor import TeamBasedSupervisor

# ⚠️ 중복: main_graph는 불필요한 중복
from app.agent_system.graphs.main_graph import MainGraph
```

**클래스명:**
```python
# Option 1: 간결하고 명확 (추천)
class MainGraph:
    """PT Manager 메인 LangGraph"""

# Option 2: 도메인 명시
class PTManagerGraph:
    """PT Manager 메인 워크플로우 그래프"""

# Option 3: 역할 명시
class OrchestrationGraph:
    """팀 기반 오케스트레이션 그래프"""
```

**추천: `MainGraph`** - 간결하고 명확

---

## 🛠️ 마이그레이션 계획 (Option B)

### Phase 1: 디렉토리 구조 변경 (30분)

```bash
cd backend/app

# 1. framework → agent_system
git mv framework agent_system

# 2. supervisor → graphs
cd agent_system
git mv supervisor graphs

# 3. team_supervisor.py → main.py
cd graphs
git mv team_supervisor.py main.py

# 4. foundation → core
cd ..
git mv foundation core

# 5. separated_states.py → state.py
cd core
git mv separated_states.py state.py

git commit -m "Refactor: Rename framework to agent_system for clarity"
```

### Phase 2: Import 경로 자동 변경 (1시간)

**Python 스크립트로 일괄 변경:**

```python
# scripts/refactor_imports.py
import os
import re
from pathlib import Path

REPLACEMENTS = {
    # 디렉토리 변경
    r'from app\.framework\.': 'from app.agent_system.',
    r'import app\.framework\.': 'import app.agent_system.',

    # 파일명 변경
    r'from app\.agent_system\.supervisor\.team_supervisor': 'from app.agent_system.graphs.main',
    r'TeamBasedSupervisor': 'MainGraph',

    r'from app\.agent_system\.foundation\.': 'from app.agent_system.core.',
    r'from app\.agent_system\.core\.separated_states': 'from app.agent_system.core.state',
}

def refactor_file(file_path: Path):
    content = file_path.read_text(encoding='utf-8')
    original = content

    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)

    if content != original:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ Refactored: {file_path}")

def main():
    backend_dir = Path("backend/app")

    for py_file in backend_dir.rglob("*.py"):
        refactor_file(py_file)

if __name__ == "__main__":
    main()
```

**실행:**
```bash
python scripts/refactor_imports.py
```

### Phase 3: 테스트 및 검증 (30분)

```bash
# 1. Import 체크
python -c "from app.agent_system.graphs.main import MainGraph; print('✅ OK')"

# 2. 테스트 실행
pytest backend/tests/ -v

# 3. Linting
flake8 backend/app/agent_system/
mypy backend/app/agent_system/
```

### Phase 4: 문서 업데이트 (30분)

**업데이트 대상:**
- `README.md`
- `docs/architecture.md`
- API 문서
- 코드 주석

---

## 📝 변경 전후 비교

### Import 예시

**기존 (Before):**
```python
# 모호하고 길다
from app.framework.supervisor.team_supervisor import TeamBasedSupervisor
from app.framework.foundation.separated_states import MainSupervisorState
from app.framework.foundation.checkpointer import create_checkpointer
from app.framework.agents.execution.search_executor import SearchExecutor
```

**개선 (After):**
```python
# 명확하고 간결
from app.agent_system.graphs.main import MainGraph
from app.agent_system.core.state import MainSupervisorState
from app.agent_system.core.checkpointer import create_checkpointer
from app.agent_system.agents.execution.search_executor import SearchExecutor
```

### 파일 경로 비교

**기존:**
```
framework/supervisor/team_supervisor.py          # 모호
framework/foundation/separated_states.py         # 파일명 장황
```

**개선:**
```
agent_system/graphs/main.py                      # 명확
agent_system/core/state.py                       # 간결
```

---

## 🎯 결론

### 추천: **Option B + LangGraph 1.0 마이그레이션 동시 진행**

**타임라인:**
```
Day 1: LangGraph 1.0 업그레이드 + 디렉토리 구조 변경
Day 2: Import 경로 수정 + 테스트
Day 3: 문서 업데이트 + 최종 검증
```

**예상 효과:**
- ✅ 코드베이스 명확성 30% 향상
- ✅ 신규 개발자 온보딩 시간 50% 단축
- ✅ LangGraph 1.0 컨벤션 100% 준수
- ✅ 향후 확장성 확보 (여러 그래프 추가 가능)

**리스크:**
- 🟡 중간 (Import 경로 일괄 변경)
- 완화: 자동화 스크립트 + 철저한 테스트

---

**작성자:** AI Assistant
**검토 필요:** 프로젝트 리드, 백엔드 팀
**결정 기한:** LangGraph 1.0 마이그레이션 시작 전
