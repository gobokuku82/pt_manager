# LangGraph 1.0 빠른 마이그레이션 가이드

**목표:** 최소 시간으로 안전하게 LangGraph 0.6 → 1.0 업그레이드

---

## 🚀 빠른 시작 (30분)

### 1단계: 백업 (5분)
```bash
# 의존성 백업
pip freeze > requirements_backup.txt

# Git 태그
git tag langgraph-0.6-backup
git push --tags

# DB 백업
pg_dump -U postgres -d ptmanager > backup.sql
```

### 2단계: Python 버전 확인 (5분)
```bash
python --version
# ⚠️ 3.10 이상 필수!
# 3.9 이하면 Python 업그레이드 필요
```

### 3단계: 패키지 업데이트 (10분)
```bash
pip install --upgrade langgraph>=1.0.0
pip install --upgrade langgraph-checkpoint-postgres>=3.0.0
pip install --upgrade langchain-core>=1.0.0

# 테스트
python -c "from langgraph.graph import StateGraph; print('✅ OK')"
python -c "from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver; print('✅ OK')"
```

### 4단계: 테스트 실행 (10분)
```bash
pytest backend/tests/ -v
# 모든 테스트 통과 확인
```

---

## ✅ 변경사항 체크리스트

**코드 변경 필요 없음:**
- ✅ `StateGraph` - API 동일
- ✅ `AsyncPostgresSaver` - 기존 패턴 호환
- ✅ `from_conn_string()` - Context manager 패턴 유지
- ✅ `setup()` - 그대로 사용
- ✅ TypedDict 상태 - 변경 없음

**확인 필요:**
- ⚠️ Python 3.10 이상 사용 중인가?
- ⚠️ `create_react_agent` 사용 중인가? (현재 미사용 ✅)

---

## 🔥 주요 변경사항

### 1. Python 버전 요구사항 (중요!)
```
기존: Python 3.9+
신규: Python 3.10+ ⚠️
```

### 2. 브레이킹 체인지
**없음!** 🎉
- Core API 변경 없음
- StateGraph 동일
- Checkpointer 패턴 동일

### 3. 폐기된 API (영향 없음)
- `create_react_agent` → 현재 미사용 ✅
- `MessageGraph` → 이미 `StateGraph` 사용 중 ✅
- `HumanInterruptConfig` → 현재 미사용 ✅

---

## 📊 영향 받는 파일

| 파일 | 변경 필요 | 작업 내용 |
|------|----------|----------|
| `team_supervisor.py` | ❌ 없음 | 의존성 업데이트만 |
| `checkpointer.py` | ❌ 없음 | 의존성 업데이트만 |
| `separated_states.py` | ❌ 없음 | 변경 불필요 |
| `execution_orchestrator.py` | ❌ 없음 | StateGraph 미사용 |
| `*_executor.py` | ❌ 없음 | StateGraph 미사용 |

**결론: 코드 변경 0개!** 🎉

---

## 🆕 선택적 신규 기능

### 1. Encrypted Serializer (권장)
**목적:** 계약서, 개인정보 암호화

```python
# checkpointer.py 수정
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer

serde = EncryptedSerializer.from_pycryptodome_aes()
checkpointer = AsyncPostgresSaver.from_conn_string(
    conn_string,
    serde=serde  # 암호화 활성화
)
```

```bash
# .env 추가
LANGGRAPH_AES_KEY=your-32-byte-key-here
```

### 2. Time Travel (디버깅용)
**목적:** 이전 대화 상태로 복원

```python
# 특정 checkpoint에서 재실행
config = {
    "configurable": {
        "thread_id": "chat_123",
        "checkpoint_id": "previous_checkpoint_id"  # 🆕
    }
}
result = await supervisor.app.ainvoke(state, config)
```

---

## 🧪 테스트 시나리오

### 기본 동작 테스트
```python
# 1. 기본 쿼리
result = await supervisor.process_query_streaming(
    query="강남구 전세 시세 알려주세요",
    session_id="test_001"
)
assert result["status"] == "completed"

# 2. Checkpoint 저장 확인
state = await supervisor.app.aget_state(
    {"configurable": {"thread_id": "test_001"}}
)
assert state is not None

# 3. HITL 동작 확인
result = await supervisor.process_query_streaming(
    query="계약서 작성해주세요",
    session_id="test_002"
)
# HITL 인터럽트 발생하는지 확인
```

---

## 🚨 롤백 방법 (5분)

```bash
# 1. 패키지 롤백
pip install -r requirements_backup.txt

# 2. Git 롤백 (필요 시)
git checkout langgraph-0.6-backup

# 3. DB 복원 (필요 시)
psql -U postgres -d ptmanager < backup.sql

# 4. 서비스 재시작
systemctl restart ptmanager-backend
```

---

## 📈 배포 전략

### Option A: 간단 배포 (소규모)
```bash
# 개발 → 스테이징 → 프로덕션
1. 개발: 패키지 업데이트 + 테스트
2. 스테이징: 1일 모니터링
3. 프로덕션: 배포
```

### Option B: Blue-Green 배포 (권장)
```bash
# Green 환경에 1.0 배포
1. Green에 배포
2. 트래픽 10% → Green
3. 30분 모니터링
4. 트래픽 100% → Green
5. Blue 환경 제거
```

---

## ⚡ 예상 소요 시간

| 단계 | 시간 | 누적 |
|------|------|------|
| 백업 | 10분 | 10분 |
| 패키지 업데이트 | 10분 | 20분 |
| 테스트 | 30분 | 50분 |
| 스테이징 배포 | 1시간 | 2시간 |
| 모니터링 (1일) | 1일 | - |
| 프로덕션 배포 | 1시간 | - |

**최소 소요 시간:** 2시간 (테스트 포함)
**권장 소요 시간:** 2-3일 (스테이징 검증 포함)

---

## 🎯 성공 기준

**필수:**
- [ ] Python 3.10+ 사용
- [ ] 모든 테스트 통과
- [ ] Checkpoint 정상 동작
- [ ] HITL 정상 동작

**권장:**
- [ ] 스테이징 1일 무장애
- [ ] 성능 기존 대비 ±10% 이내
- [ ] 에러율 1% 미만

---

## 📞 문제 해결

### Q1: Python 3.9 사용 중인데?
**A:** Python 3.10+ 업그레이드 필수
```bash
# pyenv 사용 시
pyenv install 3.10.15
pyenv local 3.10.15

# Docker 사용 시
FROM python:3.10-slim
```

### Q2: Import 에러 발생
```python
ModuleNotFoundError: No module named 'langgraph'
```
**A:** 가상환경 확인
```bash
pip list | grep langgraph
# 없으면 재설치
pip install langgraph>=1.0.0
```

### Q3: Checkpoint 에러
```
AsyncPostgresSaver setup failed
```
**A:** PostgreSQL 연결 확인
```python
# .env 확인
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 테이블 존재 확인
psql -c "\dt" | grep checkpoint
```

---

## 📚 참고 자료

- [공식 마이그레이션 가이드](https://docs.langchain.com/oss/python/migrate/langgraph-v1)
- [LangGraph 1.0 릴리스 노트](https://docs.langchain.com/oss/python/releases/langgraph-v1)
- [Persistence 가이드](https://docs.langchain.com/oss/python/langgraph/persistence)

---

**마지막 업데이트:** 2025-11-01
**상세 계획서:** `LANGGRAPH_1.0_MIGRATION_PLAN.md`
