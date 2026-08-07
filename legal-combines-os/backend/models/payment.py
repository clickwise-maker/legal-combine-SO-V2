from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid


class PlanType(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"
    PENDING = "pending"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class PaymentMethod(str, Enum):
    RAZORPAY = "razorpay"
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class SubscriptionPlan:
    """Predefined subscription plans for Legal Combines OS."""

    PLANS = {
        "basic_monthly": {
            "id": "plan_basic_monthly",
            "name": "Basic",
            "description": "Perfect for individuals",
            "price": 999,  # INR
            "price_display": "₹999/month",
            "duration_days": 30,
            "plan_type": PlanType.MONTHLY,
            "features": [
                "5 document reviews/month",
                "Basic legal research",
                "Email support",
            ],
            "limits": {
                "document_reviews": 5,
                "research_requests": 10,
                "form_fills": 3,
            },
        },
        "pro_monthly": {
            "id": "plan_pro_monthly",
            "name": "Professional",
            "description": "For legal professionals",
            "price": 2499,
            "price_display": "₹2,499/month",
            "duration_days": 30,
            "plan_type": PlanType.MONTHLY,
            "features": [
                "25 document reviews/month",
                "Advanced legal research",
                "Priority support",
                "Form auto-fill",
            ],
            "limits": {
                "document_reviews": 25,
                "research_requests": 50,
                "form_fills": 15,
            },
        },
        "enterprise_monthly": {
            "id": "plan_enterprise_monthly",
            "name": "Enterprise",
            "description": "For law firms",
            "price": 7999,
            "price_display": "₹7,999/month",
            "duration_days": 30,
            "plan_type": PlanType.MONTHLY,
            "features": [
                "Unlimited document reviews",
                "Advanced AI research",
                "24/7 priority support",
                "Custom integrations",
                "Team management",
            ],
            "limits": {
                "document_reviews": -1,  # Unlimited
                "research_requests": -1,
                "form_fills": -1,
            },
        },
        "basic_yearly": {
            "id": "plan_basic_yearly",
            "name": "Basic Annual",
            "description": "Basic plan billed annually (2 months free)",
            "price": 9990,
            "price_display": "₹9,990/year",
            "duration_days": 365,
            "plan_type": PlanType.YEARLY,
            "features": [
                "5 document reviews/month",
                "Basic legal research",
                "Email support",
            ],
            "limits": {
                "document_reviews": 5,
                "research_requests": 10,
                "form_fills": 3,
            },
        },
        "pro_yearly": {
            "id": "plan_pro_yearly",
            "name": "Professional Annual",
            "description": "Pro plan billed annually (2 months free)",
            "price": 24990,
            "price_display": "₹24,990/year",
            "duration_days": 365,
            "plan_type": PlanType.YEARLY,
            "features": [
                "25 document reviews/month",
                "Advanced legal research",
                "Priority support",
                "Form auto-fill",
            ],
            "limits": {
                "document_reviews": 25,
                "research_requests": 50,
                "form_fills": 15,
            },
        },
    }

    @classmethod
    def get_plan(cls, plan_id: str) -> Optional[dict]:
        return cls.PLANS.get(plan_id)

    @classmethod
    def get_all_plans(cls) -> list:
        return list(cls.PLANS.values())


class Subscription:
    """User subscription model."""

    def __init__(
        self,
        user_id: str,
        plan_id: str,
        subscription_id: Optional[str] = None,
        status: SubscriptionStatus = SubscriptionStatus.PENDING,
        razorpay_subscription_id: Optional[str] = None,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
        cancel_at_period_end: bool = False,
        canceled_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = subscription_id or str(uuid.uuid4())
        self.user_id = user_id
        self.plan_id = plan_id
        self.status = status
        self.razorpay_subscription_id = razorpay_subscription_id
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end
        self.cancel_at_period_end = cancel_at_period_end
        self.canceled_at = canceled_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE

    @property
    def is_expired(self) -> bool:
        if self.current_period_end:
            return datetime.utcnow() > self.current_period_end
        return False

    @property
    def days_remaining(self) -> int:
        if self.current_period_end:
            delta = self.current_period_end - datetime.utcnow()
            return max(0, delta.days)
        return 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "razorpay_subscription_id": self.razorpay_subscription_id,
            "current_period_start": (
                self.current_period_start.isoformat() if self.current_period_start else None
            ),
            "current_period_end": (
                self.current_period_end.isoformat() if self.current_period_end else None
            ),
            "cancel_at_period_end": self.cancel_at_period_end,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "is_active": self.is_active,
            "is_expired": self.is_expired,
            "days_remaining": self.days_remaining,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Subscription":
        return cls(
            subscription_id=data.get("id"),
            user_id=data["user_id"],
            plan_id=data["plan_id"],
            status=SubscriptionStatus(data.get("status", "pending")),
            razorpay_subscription_id=data.get("razorpay_subscription_id"),
            current_period_start=data.get("current_period_start"),
            current_period_end=data.get("current_period_end"),
            cancel_at_period_end=data.get("cancel_at_period_end", False),
            canceled_at=data.get("canceled_at"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class Payment:
    """Payment transaction model."""

    def __init__(
        self,
        user_id: str,
        subscription_id: str,
        amount: int,
        currency: str = "INR",
        payment_id: Optional[str] = None,
        razorpay_payment_id: Optional[str] = None,
        razorpay_order_id: Optional[str] = None,
        status: PaymentStatus = PaymentStatus.PENDING,
        payment_method: Optional[PaymentMethod] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        refunded_at: Optional[datetime] = None,
    ):
        self.id = payment_id or str(uuid.uuid4())
        self.user_id = user_id
        self.subscription_id = subscription_id
        self.amount = amount
        self.currency = currency
        self.razorpay_payment_id = razorpay_payment_id
        self.razorpay_order_id = razorpay_order_id
        self.status = status
        self.payment_method = payment_method
        self.description = description
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.completed_at = completed_at
        self.refunded_at = refunded_at

    @property
    def is_completed(self) -> bool:
        return self.status == PaymentStatus.COMPLETED

    @property
    def amount_display(self) -> str:
        return f"₹{self.amount / 100:.2f}" if self.currency == "INR" else f"{self.amount / 100:.2f}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscription_id": self.subscription_id,
            "amount": self.amount,
            "amount_display": self.amount_display,
            "currency": self.currency,
            "razorpay_payment_id": self.razorpay_payment_id,
            "razorpay_order_id": self.razorpay_order_id,
            "status": self.status.value,
            "payment_method": self.payment_method.value if self.payment_method else None,
            "description": self.description,
            "metadata": self.metadata,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "refunded_at": self.refunded_at.isoformat() if self.refunded_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Payment":
        return cls(
            payment_id=data.get("id"),
            user_id=data["user_id"],
            subscription_id=data["subscription_id"],
            amount=data["amount"],
            currency=data.get("currency", "INR"),
            razorpay_payment_id=data.get("razorpay_payment_id"),
            razorpay_order_id=data.get("razorpay_order_id"),
            status=PaymentStatus(data.get("status", "pending")),
            payment_method=PaymentMethod(data["payment_method"]) if data.get("payment_method") else None,
            description=data.get("description"),
            metadata=data.get("metadata"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            refunded_at=data.get("refunded_at"),
        )


class Commission:
    """Marketplace commission tracking."""

    COMMISSION_RATE = 0.12  # 12%

    @staticmethod
    def calculate(amount: int) -> dict:
        """Calculate commission for a transaction."""
        gross = amount
        commission = int(gross * Commission.COMMISSION_RATE)
        net = gross - commission

        return {
            "gross_amount": gross,
            "commission_rate": Commission.COMMISSION_RATE,
            "commission_amount": commission,
            "net_amount": net,
        }
