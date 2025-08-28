from langchain.tools import tool
from typing import Dict, List, Optional
from database.models import Member, Membership, PTSession, Consultation, get_db
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

@tool
def search_member(query: str) -> List[Dict]:
    """회원 검색 (이름, 전화번호, 카카오ID로 검색)"""
    db = next(get_db())
    try:
        members = db.query(Member).filter(
            (Member.name.like(f"%{query}%")) |
            (Member.phone.like(f"%{query}%")) |
            (Member.kakao_id.like(f"%{query}%"))
        ).all()
        
        result = []
        for member in members:
            result.append({
                "id": member.id,
                "name": member.name,
                "phone": member.phone,
                "kakao_id": member.kakao_id,
                "membership_status": member.membership_status,
                "registration_date": member.registration_date.isoformat() if member.registration_date else None
            })
        return result
    finally:
        db.close()

@tool
def register_member(member_data: str) -> Dict:
    """새 회원 등록"""
    db = next(get_db())
    try:
        data = json.loads(member_data)
        new_member = Member(
            name=data.get("name"),
            phone=data.get("phone"),
            kakao_id=data.get("kakao_id"),
            email=data.get("email"),
            birth_date=data.get("birth_date"),
            gender=data.get("gender"),
            address=data.get("address"),
            notes=data.get("notes")
        )
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        
        return {
            "success": True,
            "member_id": new_member.id,
            "message": f"{new_member.name}님이 성공적으로 등록되었습니다."
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

@tool
def update_member_status(member_id: int, status: str) -> Dict:
    """회원 상태 업데이트 (active, inactive, paused)"""
    db = next(get_db())
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if member:
            member.membership_status = status
            db.commit()
            return {
                "success": True,
                "message": f"{member.name}님의 상태가 {status}로 변경되었습니다."
            }
        else:
            return {
                "success": False,
                "error": "회원을 찾을 수 없습니다."
            }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

@tool
def create_membership(membership_data: str) -> Dict:
    """회원권 생성"""
    db = next(get_db())
    try:
        data = json.loads(membership_data)
        new_membership = Membership(
            member_id=data.get("member_id"),
            membership_type=data.get("membership_type"),
            start_date=datetime.fromisoformat(data.get("start_date")) if data.get("start_date") else datetime.now(),
            end_date=datetime.fromisoformat(data.get("end_date")) if data.get("end_date") else None,
            total_sessions=data.get("total_sessions"),
            remaining_sessions=data.get("remaining_sessions", data.get("total_sessions")),
            price=data.get("price"),
            payment_status=data.get("payment_status", "pending"),
            payment_method=data.get("payment_method")
        )
        db.add(new_membership)
        db.commit()
        
        return {
            "success": True,
            "membership_id": new_membership.id,
            "message": f"회원권이 성공적으로 생성되었습니다."
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

@tool
def schedule_pt_session(session_data: str) -> Dict:
    """PT 세션 예약"""
    db = next(get_db())
    try:
        data = json.loads(session_data)
        new_session = PTSession(
            member_id=data.get("member_id"),
            trainer_id=data.get("trainer_id"),
            session_date=datetime.fromisoformat(data.get("session_date")),
            session_type=data.get("session_type", "PT"),
            duration=data.get("duration", 60),
            status="scheduled",
            notes=data.get("notes")
        )
        db.add(new_session)
        
        # 회원권 세션 차감
        membership = db.query(Membership).filter(
            Membership.member_id == data.get("member_id"),
            Membership.remaining_sessions > 0
        ).first()
        
        if membership:
            membership.remaining_sessions -= 1
        
        db.commit()
        
        return {
            "success": True,
            "session_id": new_session.id,
            "message": f"PT 세션이 예약되었습니다.",
            "remaining_sessions": membership.remaining_sessions if membership else None
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

@tool
def cancel_pt_session(session_id: int, reason: str = "") -> Dict:
    """PT 세션 취소"""
    db = next(get_db())
    try:
        session = db.query(PTSession).filter(PTSession.id == session_id).first()
        if session:
            session.status = "cancelled"
            session.notes = f"{session.notes}\n취소 사유: {reason}" if session.notes else f"취소 사유: {reason}"
            
            # 회원권 세션 복구
            membership = db.query(Membership).filter(
                Membership.member_id == session.member_id
            ).first()
            
            if membership:
                membership.remaining_sessions += 1
            
            db.commit()
            
            return {
                "success": True,
                "message": "PT 세션이 취소되었습니다.",
                "remaining_sessions": membership.remaining_sessions if membership else None
            }
        else:
            return {
                "success": False,
                "error": "세션을 찾을 수 없습니다."
            }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

@tool
def get_member_info(member_id: int) -> Dict:
    """회원 상세 정보 조회"""
    db = next(get_db())
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if member:
            # 현재 활성 회원권 정보
            active_membership = db.query(Membership).filter(
                Membership.member_id == member_id,
                Membership.remaining_sessions > 0
            ).first()
            
            # 예정된 세션
            upcoming_sessions = db.query(PTSession).filter(
                PTSession.member_id == member_id,
                PTSession.status == "scheduled",
                PTSession.session_date >= datetime.now()
            ).all()
            
            return {
                "id": member.id,
                "name": member.name,
                "phone": member.phone,
                "kakao_id": member.kakao_id,
                "email": member.email,
                "membership_status": member.membership_status,
                "active_membership": {
                    "type": active_membership.membership_type,
                    "remaining_sessions": active_membership.remaining_sessions,
                    "end_date": active_membership.end_date.isoformat() if active_membership.end_date else None
                } if active_membership else None,
                "upcoming_sessions": len(upcoming_sessions)
            }
        else:
            return {"error": "회원을 찾을 수 없습니다."}
    finally:
        db.close()

@tool
def create_consultation(consultation_data: str) -> Dict:
    """상담 기록 생성"""
    db = next(get_db())
    try:
        data = json.loads(consultation_data)
        new_consultation = Consultation(
            member_id=data.get("member_id"),
            consultation_type=data.get("consultation_type", "kakao"),
            subject=data.get("subject"),
            content=data.get("content"),
            response=data.get("response"),
            status=data.get("status", "open"),
            handler=data.get("handler", "AI Assistant")
        )
        db.add(new_consultation)
        db.commit()
        
        return {
            "success": True,
            "consultation_id": new_consultation.id,
            "message": "상담 기록이 저장되었습니다."
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

# 도구 리스트
tools = [
    search_member,
    register_member,
    update_member_status,
    create_membership,
    schedule_pt_session,
    cancel_pt_session,
    get_member_info,
    create_consultation
]