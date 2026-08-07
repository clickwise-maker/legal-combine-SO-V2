"""
Typist Models — Profiles, Document Orders
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..utils.database import Base


class OrderStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVISING = "revising"
    CANCELLED = "cancelled"


class TypistProfile(Base):
    __tablename__ = "typists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    specialization = Column(String(255), nullable=False)
    experience_years = Column(Integer, default=0)
    rate_per_page = Column(Float, default=0.0)
    rate_per_hour = Column(Float, default=0.0)
    is_available = Column(Boolean, default=True)
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="typist_profile")
    orders = relationship("DocumentOrder", back_populates="typist")


class DocumentOrder(Base):
    __tablename__ = "document_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    typist_id = Column(UUID(as_uuid=True), ForeignKey("typists.id", ondelete="CASCADE"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    order_type = Column(String(50), nullable=False)
    page_count = Column(Integer, default=1)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    instructions = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    typist = relationship("TypistProfile", back_populates="orders")
    document = relationship("Document")
