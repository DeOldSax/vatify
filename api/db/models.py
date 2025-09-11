import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, Date, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    plan = Column(String, default="free", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")

class SessionToken(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_hash = Column(String, nullable=False, unique=True)
    user_agent = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    key_hash = Column(String, unique=True, nullable=False)
    prefix = Column(String, nullable=False)
    last4 = Column(String, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="api_keys")

class UsageCounter(Base):
    __tablename__ = "usage_counters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class MonthlyQuota(Base):
    __tablename__ = "monthly_quota"
    month = Column(Date, primary_key=True)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id", ondelete="CASCADE"), primary_key=True)
    requests = Column(Integer, default=0, nullable=False)
    __table_args__ = (UniqueConstraint('month','api_key_id', name='uq_month_key'),)
