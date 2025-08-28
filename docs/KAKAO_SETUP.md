# 카카오 API 설정 가이드

## 1. 카카오 개발자 앱 생성

### 1.1 카카오 개발자센터 접속
1. [카카오 개발자센터](https://developers.kakao.com) 접속
2. 카카오 계정으로 로그인

### 1.2 애플리케이션 생성
1. "내 애플리케이션" → "애플리케이션 추가하기" 클릭
2. 앱 정보 입력:
   - 앱 이름: PT Shop Management
   - 사업자명: (사업자명 입력)
   - 카테고리: 비즈니스

## 2. API 키 발급

### 2.1 앱 키 확인
생성된 앱의 "앱 키" 메뉴에서 다음 키들을 확인:

- **REST API 키**: 서버 사이드 API 호출용
- **JavaScript 키**: 웹 프론트엔드용
- **Admin 키**: 관리자 권한 필요 기능용

### 2.2 환경변수 설정
`.env` 파일 생성:
```bash
cp config/.env.example .env
```

발급받은 키 입력:
```env
KAKAO_REST_API_KEY=5a201bf00d05ec92dc0764c29048c173
KAKAO_JAVASCRIPT_KEY=7c3d01f7ed24ac5354305d69c988b80b
KAKAO_ADMIN_KEY=c2665c2f1c22b4fce3beb207fc8b2a71
```

## 3. 플랫폼 등록

### 3.1 웹 플랫폼 등록
1. "플랫폼" 메뉴 → "Web 플랫폼 등록"
2. 사이트 도메인 입력:
   - 개발: `http://localhost:8501`
   - 운영: `https://your-domain.com`

### 3.2 Redirect URI 설정
1. "카카오 로그인" → "Redirect URI 등록"
2. URI 추가:
   ```
   http://localhost:8501/auth/kakao/callback
   ```

## 4. 카카오톡 채널 연동

### 4.1 카카오톡 채널 생성
1. [카카오톡 채널 관리자센터](https://center-pf.kakao.com) 접속
2. "새 채널 만들기" 클릭
3. 채널 정보 입력:
   - 채널명: PT Shop
   - 검색용 아이디: @ptshop (예시)

### 4.2 채널 ID 확인
1. 채널 관리자센터 → 관리 → 상세설정
2. 채널 URL에서 ID 확인 (_xxxxx 형식)
3. `.env` 파일에 추가:
   ```env
   KAKAO_CHANNEL_ID=_AbCdEf
   ```

## 5. 권한 설정

### 5.1 카카오 로그인 활성화
1. "카카오 로그인" → "활성화 설정" ON
2. 동의항목 설정:
   - 닉네임: 필수
   - 이메일: 선택
   - 프로필 사진: 선택

### 5.2 카카오톡 메시지 설정
1. "카카오톡 메시지" → "설정"
2. 메시지 템플릿 생성:
   - PT 세션 알림
   - 회원권 만료 알림
   - 결제 안내

## 6. 테스트

### 6.1 개발자 테스트
1. "카카오 로그인" → "팀 관리"
2. 테스트할 카카오 계정 추가
3. 해당 계정으로 로그인 테스트

### 6.2 메시지 발송 테스트
```python
# Python 테스트 코드
import requests

url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
headers = {
    "Authorization": f"Bearer {access_token}"
}
data = {
    "template_object": json.dumps({
        "object_type": "text",
        "text": "PT Shop 테스트 메시지입니다.",
        "link": {
            "web_url": "http://localhost:8501"
        }
    })
}
response = requests.post(url, headers=headers, data=data)
```

## 7. 주의사항

### 보안 주의사항
- **절대 Git에 실제 API 키를 커밋하지 마세요**
- `.env` 파일은 `.gitignore`에 추가
- Admin 키는 서버 사이드에서만 사용

### 사용 제한
- 일일 API 호출 제한 확인
- 메시지 발송 쿼터 확인
- 비즈니스 인증 시 제한 해제 가능

## 8. 문제 해결

### 자주 발생하는 오류

#### 401 Unauthorized
- API 키 확인
- 토큰 만료 확인

#### 403 Forbidden
- 권한 설정 확인
- 플랫폼 등록 확인

#### KOE006: Invalid redirect_uri
- Redirect URI 등록 확인
- http/https 프로토콜 확인

## 9. 참고 링크
- [카카오 개발자 문서](https://developers.kakao.com/docs)
- [REST API 레퍼런스](https://developers.kakao.com/docs/latest/ko/reference/rest-api-reference)
- [카카오톡 메시지 가이드](https://developers.kakao.com/docs/latest/ko/message/common)