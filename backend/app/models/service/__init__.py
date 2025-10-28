"""
Service Models Package

범용 에이전트 프레임워크 - 데이터베이스 모델

범용 모델만 포함됩니다:
- Users: 사용자 관리
- Chat: 채팅 세션 및 메시지

도메인 특화 모델은 제거되었습니다:
- RealEstate, Region, Transaction (부동산 관련)
- TrustScore (신탁 관련)
"""

# Import all models to ensure they are registered with SQLAlchemy
from app.models.service.users import User, UserProfile, LocalAuth, SocialAuth, UserFavorite
from app.models.service.chat import ChatSession, ChatMessage

__all__ = [
    # Users
    "User",
    "UserProfile",
    "LocalAuth",
    "SocialAuth",
    "UserFavorite",
    # Chat
    "ChatSession",
    "ChatMessage",
]
