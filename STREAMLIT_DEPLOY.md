# Streamlit Cloud 배포 가이드

## 1. GitHub Repository 준비

### 1.1 Repository 생성
1. GitHub에 새 repository 생성 (예: `pt-shop-management`)
2. Public 또는 Private 선택 가능

### 1.2 파일 업로드
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/pt-shop-management.git
git push -u origin main
```

### 1.3 .gitignore 확인
- `.env` 파일이 제외되는지 확인
- `*.db` 파일이 제외되는지 확인

## 2. Streamlit Cloud 설정

### 2.1 Streamlit Cloud 가입
1. https://streamlit.io/cloud 접속
2. GitHub 계정으로 로그인

### 2.2 앱 배포
1. "New app" 클릭
2. Repository 선택
3. Branch: `main`
4. Main file path: `app/main.py`
5. App URL 설정 (예: `ptshop`)

## 3. Secrets 설정 (중요!)

### 3.1 Streamlit Cloud에서 Secrets 추가
1. 배포된 앱의 Settings → Secrets 클릭
2. 아래 TOML 형식으로 입력:

```toml
# OpenAI API 설정
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxx"

# 카카오 API 설정
KAKAO_REST_API_KEY = "5a201bf00d05ec92dc0764c29048c173"
KAKAO_JAVASCRIPT_KEY = "7c3d01f7ed24ac5354305d69c988b80b"
KAKAO_ADMIN_KEY = "c2665c2f1c22b4fce3beb207fc8b2a71"
KAKAO_REDIRECT_URI = "https://ptshop.streamlit.app/auth/kakao/callback"
KAKAO_CHANNEL_ID = "_xxxxx"

# 데이터베이스 설정
DATABASE_URL = "sqlite:///database/pt_shop.db"

# 애플리케이션 설정
APP_NAME = "PT Shop Management System"
APP_VERSION = "1.0.0"
DEBUG_MODE = false

# 세션 설정
SESSION_SECRET_KEY = "your-super-secret-key-here"
```

### 3.2 주의사항
- **절대 GitHub에 실제 API 키를 커밋하지 마세요**
- Secrets는 Streamlit Cloud에서만 관리
- 로컬 테스트는 `.env` 파일 사용

## 4. 카카오 API 설정 변경

### 4.1 Redirect URI 변경
1. 카카오 개발자센터 접속
2. 앱 설정 → 카카오 로그인 → Redirect URI
3. Streamlit 앱 URL 추가:
   ```
   https://ptshop.streamlit.app/auth/kakao/callback
   ```

### 4.2 도메인 등록
1. 플랫폼 → Web 플랫폼 설정
2. 사이트 도메인 추가:
   ```
   https://ptshop.streamlit.app
   ```

## 5. 데이터베이스 고려사항

### 5.1 SQLite 제한사항
- Streamlit Cloud는 임시 파일 시스템 사용
- **앱 재시작시 데이터베이스가 초기화됨**

### 5.2 프로덕션 대안
1. **PostgreSQL** (권장)
   - Heroku Postgres
   - Supabase
   - Railway

2. **Cloud Database**
   - AWS RDS
   - Google Cloud SQL
   - Azure Database

### 5.3 PostgreSQL 전환 예시
```python
# requirements.txt에 추가
psycopg2-binary>=2.9.9

# secrets.toml
DATABASE_URL = "postgresql://user:password@host:5432/dbname"
```

## 6. 배포 후 확인사항

### 6.1 기능 테스트
- [ ] 로그인 페이지 접근
- [ ] 회원 등록 기능
- [ ] AI 챗봇 응답
- [ ] 카카오 알림 발송

### 6.2 로그 확인
- Streamlit Cloud 대시보드에서 로그 확인
- 오류 발생시 Secrets 설정 재확인

## 7. 문제 해결

### 7.1 ModuleNotFoundError
- `requirements.txt` 확인
- 모든 패키지가 포함되었는지 확인

### 7.2 Secrets 오류
- TOML 형식이 올바른지 확인
- 따옴표 처리 확인

### 7.3 데이터베이스 오류
- SQLite 파일 경로 확인
- 권한 문제 확인

## 8. 업데이트 방법

### 8.1 코드 업데이트
```bash
git add .
git commit -m "Update message"
git push origin main
```
- Streamlit Cloud가 자동으로 재배포

### 8.2 Secrets 업데이트
- Settings → Secrets에서 직접 수정
- 저장 후 앱 재시작

## 9. 보안 권장사항

1. **API 키 관리**
   - 주기적으로 키 갱신
   - 각 환경별 다른 키 사용

2. **접근 제어**
   - Streamlit의 인증 기능 활용
   - IP 제한 설정 고려

3. **데이터 백업**
   - 정기적인 데이터베이스 백업
   - 외부 저장소 활용

## 10. 성능 최적화

1. **캐싱 활용**
   ```python
   @st.cache_data
   def load_data():
       return data
   ```

2. **리소스 관리**
   - 불필요한 재실행 방지
   - Session State 효율적 사용

3. **외부 리소스**
   - CDN 활용
   - 이미지 최적화