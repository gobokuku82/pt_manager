# 🏋️ PT Manager - AI 기반 PT샵 관리 시스템

> Google Sheets 기반 클라우드 PT샵 관리 및 모바일 전자서명 시스템

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6.6+-green.svg)](https://github.com/langchain-ai/langgraph)

## ✨ 주요 기능

### 🤖 AI 챗봇 (플로팅)
- 모든 페이지에서 접근 가능한 플로팅 챗봇
- LangGraph 기반 지능형 대화 시스템
- 음성 명령으로 모든 기능 제어 가능

### 👥 회원 관리
- 회원 등록/조회/수정/삭제
- 회원권 관리 및 잔여 횟수 추적
- 만료 알림 자동화

### 📅 스케줄 관리
- PT 세션 예약 및 관리
- 트레이너별 일정 관리
- 자동 리마인더 발송

### ✍️ 모바일 전자서명
- 계약서 템플릿 관리
- 고유 링크 생성 및 카카오톡 전송
- 터치 기반 서명 수집
- PDF 변환 및 저장

### 📱 카카오톡 연동
- 예약 알림 자동 발송
- 회원권 만료 알림
- 계약서 서명 요청

## 🚀 시작하기

### 필수 요구사항
- Python 3.11 이상
- Google Cloud 계정
- OpenAI API 키
- 카카오 개발자 계정 (선택사항)

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/pt-manager.git
cd pt-manager

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 패키지 설치
pip install -r requirements.txt
```

### 2. Google Sheets 설정

#### 2.1 Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성
3. Google Sheets API 활성화
4. 서비스 계정 생성 및 JSON 키 다운로드

#### 2.2 Google Sheets 생성
1. Google Drive에서 새 스프레드시트 생성
2. 시트명: `PT_Manager_DB`
3. 다음 시트 추가:
   - `Members` - 회원 정보
   - `Schedules` - 스케줄
   - `Contracts` - 계약서
   - `Signatures` - 서명 기록
4. 서비스 계정 이메일을 편집자로 공유

### 3. 환경 설정

`.streamlit/secrets.toml` 파일 생성:

```toml
# OpenAI
OPENAI_API_KEY = "sk-..."

# Google Sheets
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "..."
client_x509_cert_url = "..."

SPREADSHEET_ID = "your-spreadsheet-id"

# Kakao (선택사항)
KAKAO_REST_API_KEY = "..."
KAKAO_ADMIN_KEY = "..."
```

### 4. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📁 프로젝트 구조

```
pt_manager/
├── app.py                 # 메인 애플리케이션
├── pages/                 # Streamlit 페이지
│   ├── 1_👥_회원관리.py
│   ├── 2_📅_스케줄.py
│   ├── 3_📝_계약서.py
│   └── sign.py           # 모바일 서명 페이지
├── chatbot/              # AI 챗봇 모듈
│   ├── agent.py         # LangGraph 에이전트
│   └── tools.py         # 도구 정의
├── database/             # Google Sheets DB
│   ├── gsheets.py       # 연결 및 CRUD
│   └── models.py        # 데이터 모델
├── utils/                # 유틸리티
│   ├── signature.py     # 서명 처리
│   └── kakao.py         # 카카오 API
└── static/               # 정적 파일
    ├── css/
    └── js/
```

## 🌐 Streamlit Cloud 배포

1. GitHub에 저장소 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. 새 앱 배포 → GitHub 저장소 연결
4. Secrets 설정 (secrets.toml 내용 복사)
5. 배포 완료!

## 💡 사용 예시

### 챗봇 명령어
- "김철수 회원 조회"
- "오늘 PT 일정 보여줘"
- "새 회원 등록"
- "계약서 생성해서 카톡으로 보내줘"
- "이번 달 매출 통계"

### 모바일 서명 프로세스
1. 계약서 페이지에서 템플릿 선택
2. 회원 정보 입력
3. 서명 링크 생성
4. 카카오톡으로 링크 전송
5. 회원이 모바일에서 서명
6. 서명 완료 알림 수신

## 🤝 기여하기

버그 리포트나 기능 제안은 [Issues](https://github.com/yourusername/pt-manager/issues)에 등록해주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 📞 문의

- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

---

Made with ❤️ using Streamlit & LangGraph