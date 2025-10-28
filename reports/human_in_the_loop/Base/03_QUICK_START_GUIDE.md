# 빠른 시작 가이드 - 초기화 작업

**목적**: 최소한의 단계로 초기화 작업을 시작할 수 있도록 돕습니다.

**예상 소요 시간**: 첫 2일 작업 (Phase 1-2)

---

## 📌 시작하기 전에

### 필수 확인 사항

- [ ] Git이 설치되어 있고 사용 가능
- [ ] Python 3.10+ 설치
- [ ] Node.js 18+ 설치
- [ ] 현재 애플리케이션이 정상 동작 확인
- [ ] 백업 공간 확보 (최소 2GB)

### 권장 도구

- VSCode (Python, TypeScript 확장 설치)
- Git GUI (GitKraken, SourceTree 등)
- PostgreSQL Client (pgAdmin, DBeaver 등)

---

## 🚀 5단계로 시작하기

### Step 1: 백업 생성 (10분)

```bash
# 1. 현재 디렉토리 확인
cd C:/kdy/Projects/AI_PTmanager/beta_v001

# 2. Git 상태 확인
git status
# 변경사항이 있으면 먼저 커밋

# 3. 현재 버전 태그 생성
git tag -a v0.1.0-real-estate -m "부동산 챗봇 완성 버전 - 초기화 전 백업"
git push origin v0.1.0-real-estate

# 4. 전체 디렉토리 백업
cd ..
cp -r beta_v001 beta_v001_backup_20251028

# 5. 백업 확인
ls -la beta_v001_backup_20251028/
```

**검증**:
- [ ] Git 태그 생성 확인: `git tag -l`
- [ ] 백업 디렉토리 존재 확인
- [ ] 백업 용량 확인 (500MB~2GB)

---

### Step 2: 작업 브랜치 생성 (5분)

```bash
# 현재 디렉토리로 돌아오기
cd beta_v001

# 새 브랜치 생성 및 체크아웃
git checkout -b feature/generic-framework-refactoring

# 브랜치 확인
git branch
# * feature/generic-framework-refactoring 표시 확인
```

**검증**:
- [ ] 브랜치가 생성되었는지 확인
- [ ] 현재 브랜치가 feature/* 인지 확인

---

### Step 3: 첫 번째 정리 - 완전 제거 대상 (30분)

**목표**: 확실히 불필요한 파일들을 먼저 제거

```bash
# 백엔드 디렉토리로 이동
cd backend

# 1. 데이터 임포트 스크립트 제거
rm -rf scripts/
echo "✅ scripts/ 디렉토리 삭제 완료"

# 2. 구버전 코드 제거
rm -rf app/agent/foundation/old/
rm -rf app/api/old/
echo "✅ old/ 디렉토리들 삭제 완료"

# 3. 빈 디렉토리 제거
rm -rf app/crud/
echo "✅ 빈 crud/ 디렉토리 삭제 완료"

# 4. Git 상태 확인
git status

# 5. 첫 번째 커밋
git add .
git commit -m "chore: remove unnecessary directories (scripts, old, crud)"
```

**검증**:
```bash
# 삭제 확인
ls backend/scripts/ 2>/dev/null && echo "❌ 아직 존재함" || echo "✅ 정상 삭제"
ls app/agent/foundation/old/ 2>/dev/null && echo "❌ 아직 존재함" || echo "✅ 정상 삭제"
ls app/api/old/ 2>/dev/null && echo "❌ 아직 존재함" || echo "✅ 정상 삭제"

# 애플리케이션 실행 테스트
cd ..
python -m pytest tests/ || echo "⚠️ 테스트 실패 (정상 - 다음 단계에서 수정)"
```

---

### Step 4: 도메인 특화 Tools 제거 (20분)

**목표**: 부동산 관련 Tool 파일들 제거

```bash
cd app/agent/tools

# 제거할 파일 목록 확인
ls -la *.py

# 하나씩 확인하며 제거 (안전)
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

# analysis_tools.py는 유지 (범용)
ls -la
# analysis_tools.py, __init__.py만 남아있어야 함

# __init__.py 수정
cat > __init__.py << 'EOF'
"""
Tools Package

사용자 정의 Tool을 추가하려면:
1. app/domain/tools/에 Tool 클래스 작성
2. app/domain/__init__.py에서 ToolRegistry.register() 호출

예제:
    from app.framework.tools.base_tool import BaseTool
    from app.framework.tools.tool_registry import ToolRegistry

    class MyTool(BaseTool):
        # 구현
        pass

    ToolRegistry.register(MyTool())
"""

# TODO: 범용 Tool 예제 추가
EOF

# 커밋
cd ../../../..
git add .
git commit -m "chore: remove domain-specific tools"
```

**검증**:
```bash
# Tools 디렉토리 확인
ls app/agent/tools/
# analysis_tools.py, __init__.py만 있어야 함

# Import 에러 확인
python -c "import app.agent.tools" && echo "✅ Import 성공" || echo "❌ Import 실패"
```

---

### Step 5: 첫 진행 상황 확인 (10분)

```bash
# 변경 사항 요약
git log --oneline -5

# 삭제된 파일 개수 확인
git diff v0.1.0-real-estate..HEAD --stat | tail -5

# 브랜치 상태
git status
```

**예상 결과**:
```
 backend/scripts/                     | 50 files deleted
 app/agent/foundation/old/            | 5 files deleted
 app/api/old/                         | 3 files deleted
 app/crud/                            | 1 file deleted
 app/agent/tools/                     | 11 files deleted
 Total: 70 files changed, 0 insertions(+), 5000 deletions(-)
```

**체크리스트**:
- [ ] 약 70개 파일 삭제 확인
- [ ] 2개의 커밋 완료
- [ ] Git 태그 백업 존재
- [ ] 실제 디렉토리 백업 존재

---

## 🎯 다음 단계

### 다음 작업 (Day 2)

1. **도메인 특화 모델/스키마 제거** (30분)
   ```bash
   rm app/models/service/real_estate.py
   rm app/models/service/trust.py
   rm app/schemas/real_estate.py
   rm app/schemas/trust.py
   ```

2. **Utility 정리** (20분)
   ```bash
   rm app/utils/building_api.py
   rm app/utils/data_collector.py
   rm app/utils/geocode_aprtments.py
   rm app/utils/database_config.py
   ```

3. **프론트엔드 정리** (40분)
   ```bash
   cd ../frontend
   rm -rf components/agents/
   rm components/map-interface.tsx
   rm lib/district-coordinates.ts
   rm lib/clustering.ts

   # 계약서 페이지 이동
   mkdir -p ../examples/frontend/hitl-form-example
   mv components/lease_contract/* ../examples/frontend/hitl-form-example/
   ```

4. **Phase 2 완료 커밋**
   ```bash
   git add .
   git commit -m "chore: complete Phase 2 - remove all domain-specific code"
   git tag phase-2-complete
   ```

### 상세 작업 계획

**Phase 2 완료 후**: [02_FILE_PROCESSING_PLAN.md](02_FILE_PROCESSING_PLAN.md#phase-3-디렉토리-재구성) Phase 3로 이동

**전체 계획**: [01_INITIALIZATION_MASTER_PLAN.md](01_INITIALIZATION_MASTER_PLAN.md) 참조

---

## 🆘 문제 해결

### 자주 발생하는 문제

#### 1. Git 태그 생성 실패
```bash
# 에러: tag 'v0.1.0-real-estate' already exists
git tag -d v0.1.0-real-estate  # 로컬 태그 삭제
git push origin :refs/tags/v0.1.0-real-estate  # 원격 태그 삭제
# 다시 시도
```

#### 2. 파일 삭제 후 Import 에러
```bash
# 임시 해결: 삭제한 파일의 import를 주석 처리
# 나중에 Phase 8에서 일괄 수정됨

# 예시:
# from app.agent.tools.contract_analysis_tool import ContractAnalysisTool  # ← 주석 처리
```

#### 3. 테스트 실패
```
# Phase 1-2에서는 테스트 실패가 정상입니다.
# Phase 8-9에서 수정됩니다.

# 현재 단계에서는 애플리케이션 시작만 확인:
uvicorn app.main:app --reload
# 에러 없이 시작되면 OK
```

#### 4. 백업 용량 부족
```bash
# 선택적 백업
cp -r beta_v001/backend beta_v001_backend_backup/
cp -r beta_v001/frontend beta_v001_frontend_backup/
# node_modules는 제외 (나중에 npm install로 복구 가능)
```

---

## 📋 일일 체크리스트

### Day 1 완료 체크리스트

- [ ] Git 태그 생성 (v0.1.0-real-estate)
- [ ] 디렉토리 백업 (beta_v001_backup_*)
- [ ] 작업 브랜치 생성 (feature/generic-framework-refactoring)
- [ ] scripts/ 디렉토리 삭제
- [ ] old/ 디렉토리들 삭제
- [ ] crud/ 디렉토리 삭제
- [ ] Tools 파일 11개 삭제
- [ ] 2개 커밋 완료
- [ ] 변경 사항 확인

---

## 💡 팁

### 효율적인 작업을 위한 팁

1. **작은 단위로 커밋**
   - 파일 5-10개 삭제할 때마다 커밋
   - 문제 발생 시 롤백 용이

2. **체크리스트 활용**
   - 각 단계마다 체크리스트 작성
   - 완료 여부 표시

3. **백업 확인 습관**
   - 큰 작업 전 Git 태그 생성
   - 중요한 단계마다 브랜치 백업

4. **문서와 코드 동시 수정**
   - 파일 삭제 시 관련 문서도 업데이트
   - README, CHANGELOG 등

5. **테스트 주기적 실행**
   - 파일 10개 삭제할 때마다 테스트
   - Import 에러 즉시 발견

---

## 📚 참고 자료

- [마스터 플랜 전체](01_INITIALIZATION_MASTER_PLAN.md)
- [파일별 상세 계획](02_FILE_PROCESSING_PLAN.md)
- [Git 기본 사용법](https://git-scm.com/book/ko/v2)

---

**다음**: Day 2 작업으로 이어서 진행

**질문이나 문제 발생 시**: [02_FILE_PROCESSING_PLAN.md](02_FILE_PROCESSING_PLAN.md)의 해당 섹션 참조
