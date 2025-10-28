"""
Schemas Package

범용 에이전트 프레임워크 - API 스키마

범용 스키마만 포함됩니다:
- Users: 사용자 관리
- Chat: 채팅 세션 및 메시지
"""

from app.schemas.users import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithProfile,
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    LocalAuthCreate,
    SocialAuthCreate,
    UserFavoriteCreate,
    UserFavoriteResponse,
)

from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatSessionWithMessages,
    ChatMessageCreate,
    ChatMessageResponse,
)

__all__ = [
    # Users
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithProfile",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfileResponse",
    "LocalAuthCreate",
    "SocialAuthCreate",
    "UserFavoriteCreate",
    "UserFavoriteResponse",
    # Chat
    "ChatSessionCreate",
    "ChatSessionUpdate",
    "ChatSessionResponse",
    "ChatSessionWithMessages",
    "ChatMessageCreate",
    "ChatMessageResponse",
]
