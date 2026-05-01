from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class UserRole(str, enum.Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER ,nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    advertisements = relationship("Advertisement", back_populates="user", cascade="all, delete-orphan")

class Advertisement(Base):
    __tablename__ = 'advertisement'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="advertisements")