from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    kakao_id = Column(String(100), unique=True)
    email = Column(String(100))
    birth_date = Column(String(10))
    gender = Column(String(10))
    address = Column(Text)
    registration_date = Column(DateTime, default=datetime.now)
    membership_status = Column(String(20), default='active')  # active, inactive, paused
    notes = Column(Text)
    
    memberships = relationship("Membership", back_populates="member")
    sessions = relationship("PTSession", back_populates="member")
    consultations = relationship("Consultation", back_populates="member")

class Membership(Base):
    __tablename__ = 'memberships'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    membership_type = Column(String(50))  # PT10, PT20, PT30, Monthly, etc.
    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime)
    total_sessions = Column(Integer)
    remaining_sessions = Column(Integer)
    price = Column(Float)
    payment_status = Column(String(20))  # paid, pending, partial
    payment_method = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    
    member = relationship("Member", back_populates="memberships")

class PTSession(Base):
    __tablename__ = 'pt_sessions'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    trainer_id = Column(Integer, ForeignKey('trainers.id'))
    session_date = Column(DateTime)
    session_type = Column(String(50))  # PT, Group, Special
    duration = Column(Integer)  # minutes
    status = Column(String(20))  # scheduled, completed, cancelled, no-show
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    member = relationship("Member", back_populates="sessions")
    trainer = relationship("Trainer", back_populates="sessions")

class Trainer(Base):
    __tablename__ = 'trainers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True)
    email = Column(String(100))
    specialization = Column(String(200))
    hire_date = Column(DateTime)
    status = Column(String(20), default='active')
    
    sessions = relationship("PTSession", back_populates="trainer")

class Consultation(Base):
    __tablename__ = 'consultations'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    consultation_date = Column(DateTime, default=datetime.now)
    consultation_type = Column(String(50))  # kakao, phone, in-person
    subject = Column(String(200))
    content = Column(Text)
    response = Column(Text)
    status = Column(String(20))  # open, in-progress, resolved
    handler = Column(String(100))
    
    member = relationship("Member", back_populates="consultations")

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    notification_type = Column(String(50))  # session_reminder, payment_due, promotion
    title = Column(String(200))
    message = Column(Text)
    kakao_template_id = Column(String(100))
    scheduled_time = Column(DateTime)
    sent_time = Column(DateTime)
    status = Column(String(20))  # pending, sent, failed
    created_at = Column(DateTime, default=datetime.now)

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'pt_shop.db')
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()