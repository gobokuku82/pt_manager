# PTManager Database Migration Manual

## 현재 상태 (Migration 준비 완료)

### ✅ 완료된 작업

1. **프로젝트 이름 변경**
   - `backend/app/core/config.py` - PROJECT_NAME: "HolmesNyangz" → "PTManager"
   - `backend/.env` - 주석 및 설정 업데이트

2. **데이터베이스 설정**
   - PostgreSQL 데이터베이스 설정 완료
     - `real_estate`: 기존 운영 중 (건드리지 않음)
     - `ptmanager`: 새로 생성, 비어있음 (Migration 대기 중)
   - `backend/app/core/config.py` - POSTGRES_DB: "ptmanager"
   - `backend/.env` - DATABASE_URL: `postgresql+psycopg://postgres:root1234@localhost:5432/ptmanager`

3. **백업 생성**
   - `backend/.env.backup` - 원본 .env 파일 백업

---

## 📂 핵심 파일 구조

### 유지해야 할 Model 파일
```
backend/app/models/service/
├── chat.py         # ChatSession, Message 모델 (채팅 이력)
└── users.py        # User, UserAuth, UserProfile 모델 (사용자 관리)
```

### Config 파일
```
backend/
├── .env                    # 환경 변수 (DATABASE_URL 설정됨)
├── .env.backup            # 백업
└── app/
    └── core/
        └── config.py      # 앱 설정 (POSTGRES_DB="ptmanager")
```

---

## 🎯 다음 단계: Migration 설정 및 실행

### 1단계: Schema 설계

새로운 도메인에 맞는 테이블 구조를 결정하세요.

**기본 모델 (이미 존재):**
- `users` - 사용자 정보
- `user_auth` - 인증 정보
- `user_profiles` - 프로필
- `chat_sessions` - 채팅 세션
- `messages` - 메시지

**추가할 모델 예시:**
```python
# backend/app/models/service/your_domain.py
from sqlalchemy import Column, Integer, String, DateTime
from backend.app.models.base import Base

class YourModel(Base):
    __tablename__ = "your_table"

    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    created_at = Column(DateTime, server_default="NOW()")
```

---

### 2단계: Alembic 초기화

```bash
cd backend
alembic init alembic
```

**생성되는 구조:**
```
backend/
├── alembic/
│   ├── env.py              # Alembic 환경 설정
│   ├── script.py.mako      # Migration 템플릿
│   └── versions/           # Migration 파일들
└── alembic.ini             # Alembic 설정 파일
```

---

### 3단계: Alembic 설정

**1) `alembic.ini` 수정**

```ini
# Line 63: 데이터베이스 URL 설정
sqlalchemy.url = postgresql+psycopg://postgres:root1234@localhost:5432/ptmanager
```

또는 환경 변수 사용 (권장):
```ini
# sqlalchemy.url = (주석 처리 또는 삭제)
```

**2) `alembic/env.py` 수정**

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import your Base and models
from app.models.base import Base
from app.models.service.users import User, UserAuth, UserProfile
from app.models.service.chat import ChatSession, Message
# Import all your models here

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

# Environment variable 사용 시
from app.core.config import Settings
settings = Settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

### 4단계: 첫 Migration 생성

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
```

**생성 결과:**
```
backend/alembic/versions/xxxx_initial_migration.py
```

**Migration 파일 확인:**
```python
def upgrade() -> None:
    # 테이블 생성 SQL
    op.create_table('users', ...)
    op.create_table('chat_sessions', ...)
    ...

def downgrade() -> None:
    # 테이블 삭제 SQL (롤백용)
    op.drop_table('users')
    ...
```

---

### 5단계: Migration 실행

```bash
cd backend
alembic upgrade head
```

**실행 결과:**
- `ptmanager` 데이터베이스에 테이블 생성
- `alembic_version` 테이블 생성 (migration 버전 추적)

**확인:**
```bash
# PostgreSQL 접속
psql -U postgres -d ptmanager

# 테이블 목록 확인
\dt

# 결과 예시:
#  Schema |      Name       | Type  |  Owner
# --------+-----------------+-------+----------
#  public | alembic_version | table | postgres
#  public | chat_sessions   | table | postgres
#  public | messages        | table | postgres
#  public | users           | table | postgres
#  ...
```

---

## 🔧 자주 사용하는 Alembic 명령어

### Migration 생성
```bash
alembic revision --autogenerate -m "Add new table"
```

### Migration 실행
```bash
alembic upgrade head          # 최신 버전으로
alembic upgrade +1            # 1단계 업그레이드
alembic upgrade <revision>    # 특정 버전으로
```

### Migration 롤백
```bash
alembic downgrade -1          # 1단계 다운그레이드
alembic downgrade base        # 모든 migration 취소
alembic downgrade <revision>  # 특정 버전으로
```

### Migration 확인
```bash
alembic current               # 현재 버전
alembic history               # Migration 이력
alembic show <revision>       # 특정 revision 상세
```

---

## ⚠️ 주의사항

### 1. Model Import 확인
- `alembic/env.py`에 모든 Model 클래스를 import해야 함
- Import 누락 시 해당 테이블이 migration에서 제외됨

### 2. psycopg3 사용
- 현재 설정: `postgresql+psycopg://` (psycopg3)
- LangGraph의 `AsyncPostgresSaver`와 호환

### 3. Base 클래스 확인
- 모든 모델이 동일한 `Base` 클래스를 상속해야 함
- 위치: `backend/app/models/base.py`

### 4. Foreign Key 관계
- User → ChatSession: `user_id`
- ChatSession → Message: `session_id`
- 관계 설정 확인 필요

---

## 🗂️ 현재 Model 구조

### User 관련 (users.py)
```python
User
├── id (PK)
├── email
├── type (USER/ADMIN)
├── Relations:
    ├── profile: UserProfile
    ├── auth: UserAuth
    └── chat_sessions: List[ChatSession]

UserAuth
├── id (PK)
├── user_id (FK → users.id)
└── hashed_password

UserProfile
├── id (PK)
├── user_id (FK → users.id)
└── display_name
```

### Chat 관련 (chat.py)
```python
ChatSession
├── session_id (PK, String(100))
├── user_id (FK → users.id)
├── title
├── created_at
├── updated_at
└── Relations:
    └── messages: List[Message]

Message
├── id (PK)
├── session_id (FK → chat_sessions.session_id)
├── content
├── sender (user/bot)
├── timestamp
└── metadata (JSON)
```

---

## 📝 체크리스트

### Migration 시작 전
- [ ] 새로운 도메인 Schema 설계 완료
- [ ] 필요한 Model 파일 작성 (`backend/app/models/service/`)
- [ ] Base 클래스 상속 확인
- [ ] Foreign Key 관계 설정 확인

### Migration 설정
- [ ] `alembic init alembic` 실행
- [ ] `alembic.ini` 설정 (DATABASE_URL)
- [ ] `alembic/env.py` 수정 (Base import, 모든 Model import)

### Migration 실행
- [ ] `alembic revision --autogenerate -m "Initial migration"` 실행
- [ ] 생성된 migration 파일 검토
- [ ] `alembic upgrade head` 실행
- [ ] PostgreSQL에서 테이블 생성 확인

### 테스트
- [ ] 애플리케이션 실행 테스트
- [ ] CRUD 작업 테스트
- [ ] LangGraph Checkpointing 테스트 (AsyncPostgresSaver)

---

## 🚀 시작하기

Schema 설계가 완료되면 다음 명령어로 시작하세요:

```bash
cd backend
alembic init alembic
```

그 다음 이 매뉴얼의 **3단계: Alembic 설정**부터 진행하면 됩니다.
