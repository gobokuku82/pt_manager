# 범용 에이전트 프레임워크 초기화 문서

이 디렉토리에는 부동산 챗봇 "홈즈냥즈"를 범용 멀티 에이전트 프레임워크로 전환하기 위한 계획서가 포함되어 있습니다.

---

## 📚 문서 목록

### 1. [마스터 플랜](01_INITIALIZATION_MASTER_PLAN.md)
**목적**: 전체 초기화 프로젝트의 로드맵

**포함 내용**:
- 프로젝트 현황 분석
- 초기화 목표 및 원칙
- 아키텍처 설계
- 10단계 실행 계획 (23일 소요)
- 검증 계획
- 리스크 관리

**읽어야 할 사람**: 모든 팀원, 프로젝트 매니저

---

### 2. [파일별 처리 계획](02_FILE_PROCESSING_PLAN.md)
**목적**: 각 파일별 상세 처리 방법

**포함 내용**:
- 백엔드 파일 분류 (✅유지 / ⚠️리팩토링 / ❌제거 / 🆕신규)
- 프론트엔드 파일 분류
- 파일별 수정 방법 및 코드 예제
- 작업 순서 체크리스트
- 검증 스크립트

**읽어야 할 사람**: 개발자, 리팩토링 담당자

---

## 🚀 빠른 시작

### 계획서 읽는 순서

1. **처음 읽는 사람**:
   ```
   README.md (이 파일)
   → 01_INITIALIZATION_MASTER_PLAN.md (섹션 1-3)
   → 02_FILE_PROCESSING_PLAN.md (해당 작업 영역만)
   ```

2. **프로젝트 매니저**:
   ```
   01_INITIALIZATION_MASTER_PLAN.md (전체)
   → 섹션 5 (단계별 실행 계획)
   → 섹션 8 (타임라인)
   → 섹션 9 (리스크 관리)
   ```

3. **개발자**:
   ```
   01_INITIALIZATION_MASTER_PLAN.md (섹션 3: 아키텍처)
   → 02_FILE_PROCESSING_PLAN.md (상세 작업 방법)
   → 해당 Phase 작업 수행
   ```

---

## 📋 작업 흐름

```
┌─────────────────┐
│  1. 계획서 읽기  │
│  (이 문서들)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 백업 생성   │
│  (Git 태그)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Phase 별    │
│     작업 수행   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. 검증 및     │
│     테스트      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. 문서화 및   │
│     릴리즈      │
└─────────────────┘
```

---

## 🎯 핵심 목표

1. **도메인 독립성 확보**
   - 부동산 관련 모든 코드 제거 또는 템플릿화
   - 설정 기반으로 도메인 정의 가능

2. **현재 완성도 유지**
   - LangGraph 0.6 HITL 패턴 유지
   - 3-layer progress tracking 유지
   - Long-term memory 시스템 유지

3. **확장성 및 재사용성**
   - 플러그인 방식의 Tool 시스템
   - 설정 파일 기반 Intent 정의
   - Template 기반 Agent 생성

---

## 📊 진행 상황 추적

### Phase 완료 체크리스트

- [ ] Phase 1: 준비 및 백업 (1일)
- [ ] Phase 2: 불필요한 코드 제거 (2일)
- [ ] Phase 3: 디렉토리 재구성 (1일)
- [ ] Phase 4: 코어 리팩토링 (5일)
- [ ] Phase 5: 프롬프트 템플릿화 (2일)
- [ ] Phase 6: 프론트엔드 리팩토링 (2일)
- [ ] Phase 7: 문서화 (3일)
- [ ] Phase 8: 예제 및 템플릿 (2일)
- [ ] Phase 9: 테스트 작성 (3일)
- [ ] Phase 10: 검증 및 마무리 (2일)

**총 예상 기간**: 23일

---

## 🔍 주요 변경 사항

### 아키텍처 변경

**Before (부동산 특화)**:
```
backend/app/
  ├── agent/
  │   ├── tools/           # 부동산 Tool들
  │   ├── cognitive_agents/
  │   └── execution_agents/
  └── core/config.py       # 부동산 설정
```

**After (범용 프레임워크)**:
```
backend/
  ├── app/
  │   ├── framework/       # 🆕 범용 프레임워크
  │   │   ├── foundation/
  │   │   ├── agents/
  │   │   │   ├── base/    # 🆕 Abstract classes
  │   │   │   ├── cognitive/
  │   │   │   └── execution/
  │   │   └── tools/
  │   │       ├── base_tool.py      # 🆕
  │   │       └── tool_registry.py  # 🆕
  │   └── domain/          # 🆕 도메인 코드 (사용자 정의)
  │       ├── intents.py
  │       ├── agents/
  │       └── tools/
  ├── config/              # 🆕 설정 파일
  │   ├── app.yaml
  │   ├── framework.yaml
  │   ├── intents.yaml
  │   └── prompts/
  └── examples/            # 🆕 예제 코드
      └── quickstart.py
```

### 코드 변경 예시

**Before (하드코딩)**:
```python
class IntentType(Enum):
    LEGAL_CONSULT = "법률상담"
    MARKET_INQUIRY = "시세조회"
    # ... 부동산 전용
```

**After (설정 기반)**:
```yaml
# config/intents.yaml
intents:
  - name: "information_inquiry"
    display_name: "정보 조회"
    keywords: ["조회", "검색", "찾기"]
    suggested_agents: ["search_team"]
```

```python
# 동적 로드
class PlanningAgent:
    def __init__(self, config_path="config/intents.yaml"):
        self.intents = IntentLoader.load_from_yaml(config_path)
```

---

## ⚠️ 주의사항

### 작업 전 필수 확인

1. **백업 생성**
   ```bash
   git tag v0.1.0-real-estate
   cp -r beta_v001 beta_v001_backup_$(date +%Y%m%d)
   ```

2. **브랜치 생성**
   ```bash
   git checkout -b feature/generic-framework
   ```

3. **테스트 환경 준비**
   - 개발 환경에서만 작업
   - 프로덕션 영향 없음 확인

### 작업 중 주의사항

1. **단계별 커밋**
   - 각 Phase 완료 시 커밋
   - 커밋 메시지 명확하게

2. **테스트 실행**
   - 파일 삭제/이동 후 즉시 테스트
   - Import 에러 즉시 수정

3. **문서 업데이트**
   - 코드 변경 시 문서 동시 업데이트

---

## 🤝 기여 방법

### Phase 작업 진행

1. **담당 Phase 확인**
2. **해당 문서 읽기**
   - 01_INITIALIZATION_MASTER_PLAN.md 해당 Phase
   - 02_FILE_PROCESSING_PLAN.md 상세 작업

3. **체크리스트 작성**
   ```markdown
   ## Phase X: [제목]

   - [ ] 작업 1
   - [ ] 작업 2
   - [ ] 테스트
   - [ ] 문서 업데이트
   - [ ] Git commit
   ```

4. **작업 수행 및 검증**

5. **Pull Request 생성**

---

## 📞 문의

- **프로젝트 관련**: [GitHub Issues](https://github.com/your-repo/issues)
- **문서 오류**: 이 디렉토리에 Issue 파일 생성
- **긴급 문의**: 프로젝트 매니저에게 연락

---

## 📈 버전 히스토리

| 버전 | 날짜 | 변경 사항 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-10-28 | 초기 계획서 작성 | Claude |

---

## 🔗 관련 링크

- [LangGraph 0.6 문서](https://langchain-ai.github.io/langgraph/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [React 문서](https://react.dev/)

---

**다음 단계**: [마스터 플랜](01_INITIALIZATION_MASTER_PLAN.md) 읽기
