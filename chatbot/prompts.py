"""
챗봇 프롬프트 템플릿
"""

SYSTEM_PROMPT = """
당신은 PT샵 관리를 도와주는 AI 어시스턴트입니다.
친절하고 전문적으로 응답하며, 다음과 같은 업무를 수행할 수 있습니다:

1. 회원 관리
   - 회원 검색 및 조회
   - 신규 회원 등록
   - 회원 정보 수정
   - 회원권 관리

2. 스케줄 관리
   - PT 세션 예약
   - 일정 조회 및 변경
   - 트레이너별 스케줄 확인

3. 계약서 관리
   - 전자 계약서 생성
   - 서명 링크 발송
   - 서명 상태 확인

4. 알림 관리
   - 카카오톡 메시지 전송
   - 예약 리마인더
   - 회원권 만료 알림

5. 통계 및 분석
   - 회원 통계
   - 매출 분석
   - 이용 현황

항상 정확한 정보를 제공하고, 필요한 경우 추가 확인을 요청하세요.
개인정보는 안전하게 처리하고, 민감한 정보는 신중히 다루세요.
"""

MEMBER_SEARCH_PROMPT = """
회원을 검색하고 있습니다.
검색어: {query}

다음 정보를 확인해주세요:
- 이름
- 전화번호
- 이메일
- 회원권 상태
"""

SCHEDULE_CREATE_PROMPT = """
PT 세션을 예약합니다.

회원: {member_name}
날짜: {date}
시간: {time}
트레이너: {trainer}

예약을 진행하시겠습니까?
"""

CONTRACT_CREATE_PROMPT = """
전자 계약서를 생성합니다.

회원: {member_name}
계약서 종류: {contract_type}

서명 링크를 생성하여 카카오톡으로 전송하시겠습니까?
"""

ERROR_PROMPT = """
요청을 처리하는 중 오류가 발생했습니다.

오류: {error}

다시 시도하거나 관리자에게 문의해주세요.
"""

def get_prompt_template(template_name: str, **kwargs) -> str:
    """프롬프트 템플릿 반환"""
    templates = {
        "system": SYSTEM_PROMPT,
        "member_search": MEMBER_SEARCH_PROMPT,
        "schedule_create": SCHEDULE_CREATE_PROMPT,
        "contract_create": CONTRACT_CREATE_PROMPT,
        "error": ERROR_PROMPT
    }
    
    template = templates.get(template_name, "")
    
    if kwargs:
        return template.format(**kwargs)
    
    return template

# 대화 예시
CONVERSATION_EXAMPLES = [
    {
        "user": "김철수 회원 검색해줘",
        "assistant": "김철수 회원을 검색하겠습니다... 1명의 회원을 찾았습니다:\n- 김철수 (010-1234-5678)\n  회원권: PT20, 잔여: 15회"
    },
    {
        "user": "내일 오전 10시에 PT 예약",
        "assistant": "PT 예약을 도와드리겠습니다. 회원님 성함을 알려주시겠어요?"
    },
    {
        "user": "오늘 PT 일정 보여줘",
        "assistant": "오늘(2024-01-15) PT 일정입니다:\n- 09:00 김철수 (김코치)\n- 10:00 이영희 (박코치)\n- 14:00 박민수 (김코치)"
    },
    {
        "user": "계약서 만들어줘",
        "assistant": "계약서를 생성하겠습니다. 어떤 회원의 계약서를 만들까요? 회원 이름을 알려주세요."
    },
    {
        "user": "전체 회원 수 알려줘",
        "assistant": "PT샵 현황:\n- 전체 회원: 152명\n- 활성 회원: 48명\n- 오늘 PT: 12건\n- 대기중 서명: 3건"
    }
]

# 의도 분류를 위한 키워드
INTENT_KEYWORDS = {
    "search_member": ["검색", "찾아", "조회", "확인", "회원"],
    "create_member": ["등록", "가입", "추가", "신규"],
    "create_schedule": ["예약", "PT", "세션", "스케줄"],
    "view_schedule": ["일정", "오늘", "내일", "이번주"],
    "create_contract": ["계약서", "서명", "동의서"],
    "send_message": ["카톡", "카카오톡", "메시지", "전송", "알림"],
    "statistics": ["통계", "현황", "전체", "총", "몇명"]
}