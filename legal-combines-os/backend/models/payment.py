"""
Payment Models — Razorpay Integration, Subscriptions, Commissions
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..utils.database import Base


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class SubscriptionPlan(str, PyEnum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionInterval(str, PyEnum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    order_id = Column(String(255), unique=True, nullable=False)
    payment_id = Column(String(255), unique=True, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    description = Column(String(255), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    webhook_data = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payment", uselist=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"))
    plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    interval = Column(Enum(SubscriptionInterval), default=SubscriptionInterval.MONTHLY)
    amount = Column(Float, nullable=False)
    starts_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=True)
    canceled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    payment = relationship("Payment", back_populates="subscription")

    def is_expired(self) -> bool:
        if self.expires_at:
            return self.expires_at < datetime.utcnow()
        return False

    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired()


class Commission(Base):
    __tablename__ = "commissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"))
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id"))
    amount = Column(Float, nullable=False)
    commission_percentage = Column(Float, default=12.0)
    platform_fee = Column(Float, nullable=False)
    lawyer_earning = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def calculate_commission(self, total: float) -> dict:
        platform_fee = total * (self.commission_percentage / 100)
        lawyer_earning = total - platform_fee
        return {
            "total": total,
            "platform_fee": platform_fee,
            "lawyer_earning": lawyer_earning,
            "commission_percentage": self.commission_percentage
        }
