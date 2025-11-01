# 최종 리팩토링 실행 계획서

**작성일:** 2025-11-01
**결정사항:**
- `framework` → `agent_system`
- `supervisor/` 폴더명 유지
- `team_supervisor.py` → `main.py`

---

## 📋 최종 구조

### 변경 전 (Before)
```
backend/app/framework/
├── agents/
├── foundation/
├── llm/
├── supervisor/
│   └── team_supervisor.py    # TeamBasedSupervisor 클래스
└── tools/
```

### 변경 후 (After)
```
backend/app/agent_system/      # ✅ framework → agent_system
├── agents/
├── foundation/
├── llm/
├── supervisor/               # ✅ 폴더명 유지
│   └── main.py              # ✅ team_supervisor.py → main.py
└── tools/
```

### Import 경로 변경

**Before:**
```python
from app.framework.supervisor.team_supervisor import TeamBasedSupervisor
```

**After:**
```python
from app.agent_system.supervisor.main import TeamBasedSupervisor
# 또는 클래스명도 변경 시
from app.agent_system.supervisor.main import MainGraph
```

---

## 🎯 변경 범위

### 영향 받는 파일 (추정 25-30개)

**Import 경로 변경 필요:**
```python
# 1. API 레이어
app/api/chat_api.py
app/api/ws_manager.py

# 2. Agent 시스템 내부
app/agent_system/agents/cognitive/*.py
app/agent_system/agents/execution/*.py
app/agent_system/foundation/*.py

# 3. 테스트
backend/tests/test_team_supervisor.py
backend/tests/test_*.py

# 4. 설정 및 유틸리티
app/main.py
app/core/config.py
```

---

## 🚀 실행 계획 (3단계, 1시간)

### Phase 1: 디렉토리 및 파일 이동 (10분)

```bash
cd C:\kdy\projects\ptmanager\pt_manager\backend\app

# Step 1: framework → agent_system
git mv framework agent_system

# Step 2: team_supervisor.py → main.py
cd agent_system/supervisor
git mv team_supervisor.py main.py

# Step 3: 변경사항 확인
git status

# Step 4: 커밋 (import 수정 전에 커밋하지 않음 - 나중에 일괄 커밋)
# git commit -m "Refactor: Rename framework to agent_system, team_supervisor to main"
```

### Phase 2: Import 경로 자동 수정 (30분)

#### 2.1 자동 수정 스크립트 작성

**파일 위치:** `backend/scripts/refactor_imports.py`

```python
"""
Import 경로 자동 수정 스크립트
framework → agent_system
team_supervisor → main
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# 변경 패턴 정의
REPLACEMENTS: List[Tuple[str, str]] = [
    # 1. 디렉토리 변경: framework → agent_system
    (r'from app\.framework\.', 'from app.agent_system.'),
    (r'import app\.framework\.', 'import app.agent_system.'),
    (r'from\s+app\.framework\s+import', 'from app.agent_system import'),

    # 2. 파일명 변경: team_supervisor → main (supervisor 폴더는 유지)
    (r'from app\.agent_system\.supervisor\.team_supervisor\s+import',
     'from app.agent_system.supervisor.main import'),
    (r'import app\.agent_system\.supervisor\.team_supervisor',
     'import app.agent_system.supervisor.main'),
]

def refactor_file(file_path: Path) -> bool:
    """
    단일 파일의 import 경로를 수정

    Args:
        file_path: 수정할 파일 경로

    Returns:
        변경 여부 (True: 변경됨, False: 변경 안 됨)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return False

    original_content = content

    # 모든 패턴 적용
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)

    # 변경사항이 있으면 파일 저장
    if content != original_content:
        try:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Refactored: {file_path.relative_to(Path.cwd())}")
            return True
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return False

    return False

def find_python_files(root_dir: Path) -> List[Path]:
    """
    Python 파일 목록 찾기

    Args:
        root_dir: 검색 시작 디렉토리

    Returns:
        Python 파일 경로 리스트
    """
    return list(root_dir.rglob("*.py"))

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Import 경로 자동 수정 시작")
    print("=" * 60)

    # 루트 디렉토리 설정
    backend_dir = Path(__file__).parent.parent
    app_dir = backend_dir / "app"
    tests_dir = backend_dir / "tests"

    # Python 파일 수집
    python_files = []
    python_files.extend(find_python_files(app_dir))
    python_files.extend(find_python_files(tests_dir))

    print(f"\n📁 검색된 Python 파일: {len(python_files)}개")
    print("-" * 60)

    # 파일별 수정
    changed_count = 0
    for py_file in python_files:
        if refactor_file(py_file):
            changed_count += 1

    print("-" * 60)
    print(f"\n✨ 완료: {changed_count}개 파일 수정됨")
    print("=" * 60)

    if changed_count > 0:
        print("\n다음 단계:")
        print("1. 수정된 파일 확인: git diff")
        print("2. 테스트 실행: pytest backend/tests/ -v")
        print("3. 커밋: git add . && git commit -m 'Refactor: Update imports for agent_system'")

if __name__ == "__main__":
    main()
```

#### 2.2 스크립트 실행

```bash
# 1. 스크립트 디렉토리 생성
mkdir -p backend/scripts

# 2. 스크립트 파일 생성 (위 코드 복사)
# backend/scripts/refactor_imports.py

# 3. 실행
cd backend
python scripts/refactor_imports.py

# 예상 출력:
# ============================================================
# Import 경로 자동 수정 시작
# ============================================================
#
# 📁 검색된 Python 파일: 85개
# ------------------------------------------------------------
# ✅ Refactored: app/api/chat_api.py
# ✅ Refactored: app/api/ws_manager.py
# ✅ Refactored: app/agent_system/agents/cognitive/planning_agent.py
# ...
# ------------------------------------------------------------
#
# ✨ 완료: 28개 파일 수정됨
# ============================================================
```

#### 2.3 수동 확인 (중요!)

**자동 스크립트가 놓칠 수 있는 패턴:**

```python
# 1. __init__.py에서 re-export
# app/agent_system/__init__.py
from .supervisor.main import TeamBasedSupervisor  # 수동 확인 필요

# 2. 문자열 내 경로
# app/core/config.py
SUPERVISOR_MODULE = "app.agent_system.supervisor.main"  # 수동 확인 필요

# 3. 주석
# 주석에 app.framework.supervisor.team_supervisor 언급 → 수동 수정
```

### Phase 3: 테스트 및 검증 (20분)

#### 3.1 Import 테스트
```bash
# Python 인터프리터에서 import 확인
python -c "from app.agent_system.supervisor.main import TeamBasedSupervisor; print('✅ Import OK')"

# 출력: ✅ Import OK
```

#### 3.2 단위 테스트
```bash
# 전체 테스트 실행
pytest backend/tests/ -v

# 특정 테스트만 실행
pytest backend/tests/test_team_supervisor.py -v
pytest backend/tests/test_agents/ -v
```

#### 3.3 정적 분석
```bash
# 1. Syntax 체크
python -m py_compile backend/app/agent_system/supervisor/main.py

# 2. Import 체크 (모든 파일)
find backend/app -name "*.py" -exec python -m py_compile {} \;

# 3. Flake8 (선택)
flake8 backend/app/agent_system/ --max-line-length=120

# 4. MyPy (선택)
mypy backend/app/agent_system/
```

#### 3.4 실행 테스트
```bash
# 서버 실행 확인
cd backend
uvicorn app.main:app --reload

# 출력 확인:
# INFO:     Started server process
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### 3.5 변경 파일 확인
```bash
# 변경된 파일 목록
git status

# 상세 변경 내용
git diff

# 변경 요약
git diff --stat
```

---

## 📝 체크리스트

### Phase 1: 디렉토리 이동
- [ ] `framework/` → `agent_system/` 이동 완료
- [ ] `team_supervisor.py` → `main.py` 이름 변경 완료
- [ ] `git status`로 변경사항 확인

### Phase 2: Import 수정
- [ ] 자동 수정 스크립트 실행 완료
- [ ] 수정된 파일 개수 확인 (예상: 25-30개)
- [ ] `__init__.py` 파일 수동 확인
- [ ] 문자열 경로 수동 확인
- [ ] 주석 내 경로 수동 확인 (선택)

### Phase 3: 검증
- [ ] Import 테스트 통과
- [ ] 단위 테스트 통과 (`pytest`)
- [ ] 정적 분석 통과 (`py_compile`)
- [ ] 서버 실행 정상
- [ ] API 엔드포인트 동작 확인 (Postman/curl)

### 최종 커밋
- [ ] `git diff` 리뷰 완료
- [ ] 불필요한 변경 제거
- [ ] 커밋 메시지 작성
- [ ] 커밋 및 푸시

---

## 🎯 예상 결과

### Import 경로 비교

**Before:**
```python
from app.framework.supervisor.team_supervisor import TeamBasedSupervisor
from app.framework.foundation.separated_states import MainSupervisorState
from app.framework.agents.execution.search_executor import SearchExecutor
from app.framework.llm.llm_service import LLMService
```

**After:**
```python
from app.agent_system.supervisor.main import TeamBasedSupervisor
from app.agent_system.foundation.separated_states import MainSupervisorState
from app.agent_system.agents.execution.search_executor import SearchExecutor
from app.agent_system.llm.llm_service import LLMService
```

### 디렉토리 구조

```
backend/app/agent_system/          # ✅ 변경됨 (framework → agent_system)
├── agents/
│   ├── base/
│   ├── cognitive/
│   └── execution/
├── foundation/
├── llm/
├── supervisor/                    # ✅ 유지됨
│   ├── __init__.py
│   └── main.py                   # ✅ 변경됨 (team_supervisor.py → main.py)
└── tools/
```

---

## ⚠️ 주의사항

### 1. Git 작업 시
```bash
# ❌ 잘못된 방법: 파일 삭제 후 새로 생성
rm -rf framework
mkdir agent_system
# → Git 히스토리 손실!

# ✅ 올바른 방법: git mv 사용
git mv framework agent_system
# → Git 히스토리 유지!
```

### 2. IDE 캐시 정리
```bash
# VSCode
# Ctrl+Shift+P → "Python: Clear Cache and Reload Window"

# PyCharm
# File → Invalidate Caches / Restart
```

### 3. Virtual Environment 재생성 (선택)
```bash
# Import 경로가 캐시되어 있을 수 있음
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

## 🔄 롤백 방법

### Git으로 롤백 (변경 전)
```bash
# 1. 변경사항 확인
git status

# 2. 롤백 (커밋 전)
git reset --hard HEAD

# 3. 롤백 (커밋 후)
git revert <commit-hash>
```

### 수동 롤백
```bash
# 1. 이전 백업 복원
git checkout HEAD -- .

# 2. 디렉토리 복원
git mv agent_system framework
cd supervisor
git mv main.py team_supervisor.py
```

---

## 🚀 실행 명령어 요약

```bash
# === Phase 1: 디렉토리 이동 (10분) ===
cd C:\kdy\projects\ptmanager\pt_manager\backend\app
git mv framework agent_system
cd agent_system/supervisor
git mv team_supervisor.py main.py

# === Phase 2: Import 자동 수정 (30분) ===
cd C:\kdy\projects\ptmanager\pt_manager\backend
python scripts/refactor_imports.py

# === Phase 3: 검증 (20분) ===
# Import 테스트
python -c "from app.agent_system.supervisor.main import TeamBasedSupervisor; print('✅ OK')"

# 단위 테스트
pytest tests/ -v

# 서버 실행
uvicorn app.main:app --reload

# === 최종 커밋 ===
git add .
git commit -m "Refactor: Rename framework to agent_system, team_supervisor to main

- framework/ → agent_system/ (명확성 개선)
- supervisor/team_supervisor.py → supervisor/main.py (간결화)
- Update all import paths across the codebase
- All tests passing"

git push origin main
```

---

## 📊 진행 상황 추적

### 현재 진행률: 0%

- [ ] Phase 1: 디렉토리 이동 (0/2)
  - [ ] framework → agent_system
  - [ ] team_supervisor.py → main.py

- [ ] Phase 2: Import 수정 (0/3)
  - [ ] 자동 스크립트 실행
  - [ ] 수동 확인
  - [ ] IDE 캐시 정리

- [ ] Phase 3: 검증 (0/5)
  - [ ] Import 테스트
  - [ ] 단위 테스트
  - [ ] 정적 분석
  - [ ] 서버 실행
  - [ ] API 동작 확인

- [ ] 최종 커밋 및 푸시

---

**작성자:** AI Assistant
**예상 소요 시간:** 1시간
**다음 단계:** LangGraph 1.0 마이그레이션과 병행 가능
