# PT Shop Management System

PT샵을 위한 LangGraph 기반 회원 관리 및 AI 상담 챗봇 시스템

## 🚀 주요 기능

- **회원 관리**: 회원 등록, 조회, 수정, 삭제
- **회원권 관리**: 회원권 생성, 잔여 횟수 관리
- **PT 세션 관리**: 예약, 취소, 일정 관리
- **AI 상담 챗봇**: LangGraph 기반 지능형 대화 시스템
- **카카오톡 알림**: 예약 알림, 회원권 만료 알림 등
- **통계 및 분석**: 회원 활동 통계, 매출 분석

## 📋 요구사항

- Python 3.11 또는 3.12
- SQLite3
- 카카오 API 키 (알림 기능용)
- OpenAI API 키 (AI 챗봇용)

## 🛠 설치 방법

1. 저장소 클론
```bash
cd C:\kdy\Projects\AI_PTmanager\beta_v001
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
# config/.env.example을 .env로 복사
copy config\.env.example .env
# .env 파일을 열어 API 키 설정
```

5. 애플리케이션 실행
```bash
python run.py
```

## 📁 프로젝트 구조

```
beta_v001/
├── agents/              # LangGraph 에이전트
│   ├── state.py        # 에이전트 상태 정의
│   ├── tools.py        # 도구 정의
│   ├── main_agent.py   # 메인 에이전트 로직
│   └── graph.py        # LangGraph 그래프 구성
├── app/                # Streamlit 애플리케이션
│   ├── main.py         # 메인 대시보드
│   └── pages/          # 페이지별 모듈
│       └── chat.py     # AI 챗봇 인터페이스
├── database/           # 데이터베이스
│   └── models.py       # SQLAlchemy 모델
├── utils/              # 유틸리티
│   ├── kakao_api.py    # 카카오 API 연동
│   └── member_manager.py # 회원 관리 헬퍼
├── styles/             # CSS 스타일
│   └── style.css       # 커스텀 CSS
├── config/             # 설정 파일
│   └── .env.example    # 환경 변수 예시
├── requirements.txt    # 패키지 목록
├── run.py             # 실행 스크립트
└── README.md          # 문서

```

## 💡 사용 방법

### 회원 등록
1. 사이드바에서 "회원 관리" 선택
2. "회원 등록" 탭 클릭
3. 필수 정보 입력 후 "회원 등록" 버튼 클릭

### AI 챗봇 사용
1. 사이드바에서 "AI 챗봇" 선택
2. 메시지 입력창에 질문이나 명령 입력
3. 예시: "김철수 회원 검색", "PT 세션 예약", "회원권 등록"

### 카카오톡 알림 설정
1. .env 파일에 카카오 API 키 설정
2. 회원 정보에 카카오 ID 등록
3. 알림 자동 전송 또는 수동 전송 가능

## 🔧 환경 설정

### 필수 API 키
- `OPENAI_API_KEY`: OpenAI API 키
- `KAKAO_REST_API_KEY`: 카카오 REST API 키
- `KAKAO_ADMIN_KEY`: 카카오 Admin 키
- `KAKAO_CHANNEL_ID`: 카카오톡 채널 ID

## 📝 라이선스

이 프로젝트는 비공개 프로젝트입니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 연락주세요.