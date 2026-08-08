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

    # Plan catalog (pricing in INR paise is handled by callers)
    _CATALOG = {
        "free": {"id": "free", "name": "Free", "price": 0, "duration_days": 36500},
        "basic": {"id": "basic", "name": "Basic", "price": 499, "duration_days": 30},
        "pro": {"id": "pro", "name": "Professional", "price": 1499, "duration_days": 30},
        "enterprise": {"id": "enterprise", "name": "Enterprise", "price": 4999, "duration_days": 365},
    }

    @classmethod
    def get_plan(cls, plan_id: str):
        """Return plan catalog dict for a given plan id, or None."""
        return cls._CATALOG.get(plan_id)

    @classmethod
    def get_all_plans(cls):
        """Return all plan catalog dicts."""
        return list(cls._CATALOG.values())


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

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "order_id": self.order_id,
            "payment_id": self.payment_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status.value if self.status else None,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


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

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "payment_id": str(self.payment_id) if self.payment_id else None,
            "plan": self.plan.value if self.plan else None,
            "interval": self.interval.value if self.interval else None,
            "amount": self.amount,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "auto_renew": self.auto_renew,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


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

    COMMISSION_PERCENTAGE = 12.0

    @classmethod
    def calculate(cls, amount: float) -> dict:
        """Calculate commission for an amount (classmethod).

        `amount` is in the smallest currency unit (paise) for payments,
        or base currency for marketplace transactions.
        """
        commission_amount = amount * (cls.COMMISSION_PERCENTAGE / 100)
        gross_amount = amount
        net_amount = amount - commission_amount
        return {
            "gross_amount": gross_amount,
            "commission_amount": commission_amount,
            "net_amount": net_amount,
            "commission_percentage": cls.COMMISSION_PERCENTAGE,
        }

    def calculate_commission(self, total: float) -> dict:
        platform_fee = total * (self.commission_percentage / 100)
        lawyer_earning = total - platform_fee
        return {
            "total": total,
            "platform_fee": platform_fee,
            "lawyer_earning": lawyer_earning,
            "commission_percentage": self.commission_percentage
        }

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "booking_id": str(self.booking_id) if self.booking_id else None,
            "lawyer_id": str(self.lawyer_id) if self.lawyer_id else None,
            "amount": self.amount,
            "commission_percentage": self.commission_percentage,
            "platform_fee": self.platform_fee,
            "lawyer_earning": self.lawyer_earning,
            "status": self.status,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
