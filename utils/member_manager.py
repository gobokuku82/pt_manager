from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database.models import Member, Membership, PTSession, get_db
from datetime import datetime, timedelta

class MemberManager:
    def __init__(self):
        self.db = None
    
    def __enter__(self):
        self.db = next(get_db())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
    
    def create_member(self, member_data: Dict) -> Member:
        """새 회원 생성"""
        member = Member(
            name=member_data.get("name"),
            phone=member_data.get("phone"),
            kakao_id=member_data.get("kakao_id"),
            email=member_data.get("email"),
            birth_date=member_data.get("birth_date"),
            gender=member_data.get("gender"),
            address=member_data.get("address"),
            notes=member_data.get("notes")
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member
    
    def get_member_by_id(self, member_id: int) -> Optional[Member]:
        """ID로 회원 조회"""
        return self.db.query(Member).filter(Member.id == member_id).first()
    
    def get_member_by_phone(self, phone: str) -> Optional[Member]:
        """전화번호로 회원 조회"""
        return self.db.query(Member).filter(Member.phone == phone).first()
    
    def get_member_by_kakao_id(self, kakao_id: str) -> Optional[Member]:
        """카카오 ID로 회원 조회"""
        return self.db.query(Member).filter(Member.kakao_id == kakao_id).first()
    
    def search_members(self, query: str) -> List[Member]:
        """회원 검색 (이름, 전화번호, 카카오ID)"""
        return self.db.query(Member).filter(
            (Member.name.like(f"%{query}%")) |
            (Member.phone.like(f"%{query}%")) |
            (Member.kakao_id.like(f"%{query}%"))
        ).all()
    
    def get_all_members(self, status: Optional[str] = None) -> List[Member]:
        """모든 회원 조회"""
        query = self.db.query(Member)
        if status:
            query = query.filter(Member.membership_status == status)
        return query.all()
    
    def update_member(self, member_id: int, update_data: Dict) -> Optional[Member]:
        """회원 정보 업데이트"""
        member = self.get_member_by_id(member_id)
        if member:
            for key, value in update_data.items():
                if hasattr(member, key):
                    setattr(member, key, value)
            self.db.commit()
            self.db.refresh(member)
        return member
    
    def delete_member(self, member_id: int) -> bool:
        """회원 삭제"""
        member = self.get_member_by_id(member_id)
        if member:
            self.db.delete(member)
            self.db.commit()
            return True
        return False
    
    def get_member_membership(self, member_id: int) -> Optional[Membership]:
        """회원의 현재 활성 회원권 조회"""
        return self.db.query(Membership).filter(
            Membership.member_id == member_id,
            Membership.remaining_sessions > 0
        ).order_by(Membership.created_at.desc()).first()
    
    def get_member_sessions(self, member_id: int, status: Optional[str] = None) -> List[PTSession]:
        """회원의 PT 세션 조회"""
        query = self.db.query(PTSession).filter(PTSession.member_id == member_id)
        if status:
            query = query.filter(PTSession.status == status)
        return query.order_by(PTSession.session_date.desc()).all()
    
    def get_upcoming_sessions(self, member_id: int) -> List[PTSession]:
        """회원의 예정된 세션 조회"""
        return self.db.query(PTSession).filter(
            PTSession.member_id == member_id,
            PTSession.status == "scheduled",
            PTSession.session_date >= datetime.now()
        ).order_by(PTSession.session_date).all()
    
    def get_expiring_memberships(self, days: int = 7) -> List[Dict]:
        """만료 예정 회원권 조회"""
        expiry_date = datetime.now() + timedelta(days=days)
        memberships = self.db.query(Membership).filter(
            Membership.end_date <= expiry_date,
            Membership.remaining_sessions > 0
        ).all()
        
        result = []
        for membership in memberships:
            member = self.get_member_by_id(membership.member_id)
            if member:
                result.append({
                    "member": member,
                    "membership": membership,
                    "days_until_expiry": (membership.end_date - datetime.now()).days
                })
        return result
    
    def get_members_with_low_sessions(self, threshold: int = 3) -> List[Dict]:
        """잔여 세션이 적은 회원 조회"""
        memberships = self.db.query(Membership).filter(
            Membership.remaining_sessions > 0,
            Membership.remaining_sessions <= threshold
        ).all()
        
        result = []
        for membership in memberships:
            member = self.get_member_by_id(membership.member_id)
            if member:
                result.append({
                    "member": member,
                    "membership": membership,
                    "remaining_sessions": membership.remaining_sessions
                })
        return result
    
    def get_inactive_members(self, days: int = 30) -> List[Member]:
        """비활성 회원 조회 (최근 N일 동안 세션 없음)"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 최근 세션이 있는 회원 ID 목록
        active_member_ids = self.db.query(PTSession.member_id).filter(
            PTSession.session_date >= cutoff_date,
            PTSession.status == "completed"
        ).distinct().all()
        active_member_ids = [id[0] for id in active_member_ids]
        
        # 활성 회원권이 있지만 최근 세션이 없는 회원
        return self.db.query(Member).filter(
            Member.membership_status == "active",
            ~Member.id.in_(active_member_ids) if active_member_ids else True
        ).all()
    
    def get_member_statistics(self, member_id: int) -> Dict:
        """회원 통계 정보"""
        member = self.get_member_by_id(member_id)
        if not member:
            return {}
        
        total_sessions = self.db.query(PTSession).filter(
            PTSession.member_id == member_id
        ).count()
        
        completed_sessions = self.db.query(PTSession).filter(
            PTSession.member_id == member_id,
            PTSession.status == "completed"
        ).count()
        
        cancelled_sessions = self.db.query(PTSession).filter(
            PTSession.member_id == member_id,
            PTSession.status == "cancelled"
        ).count()
        
        total_memberships = self.db.query(Membership).filter(
            Membership.member_id == member_id
        ).count()
        
        return {
            "member_id": member_id,
            "member_name": member.name,
            "registration_date": member.registration_date,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "cancelled_sessions": cancelled_sessions,
            "attendance_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "total_memberships": total_memberships,
            "current_status": member.membership_status
        }