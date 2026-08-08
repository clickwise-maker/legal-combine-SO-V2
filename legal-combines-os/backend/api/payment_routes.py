import hashlib
import hmac
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

import razorpay
from fastapi import APIRouter, HTTPException, Depends, Header, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.payment import (
    SubscriptionPlan,
    Subscription,
    Payment,
    Commission,
    PaymentStatus,
    SubscriptionInterval,
)
from ..models.user import User
from ..utils.database import get_db


router = APIRouter(tags=["Payments"])


RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "webhook_secret_here")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-domain.com/api/payments/webhook")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID or "", RAZORPAY_KEY_SECRET or ""))


class CreateSubscriptionRequest(BaseModel):
    plan_id: str


class CancelSubscriptionRequest(BaseModel):
    immediate: bool = False


class ConfirmSubscriptionRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str


class PaymentIntentResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    key_id: str


class SubscriptionResponse(BaseModel):
    subscription: dict
    plan: Optional[dict] = None


class WebhookPayload(BaseModel):
    event: str
    payload: dict


def get_current_user_id() -> str:
    """Mock function to get current authenticated user ID."""
    return "user_123"


def verify_razorpay_signature(payload: str, signature: str) -> bool:
    """Verify Razorpay webhook signature."""
    try:
        return hmac.compare_digest(
            hmac.new(
                RAZORPAY_WEBHOOK_SECRET.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest(),
            signature
        )
    except Exception:
        return False


def _is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def _user_uuid(user_id: str):
    """Convert user_id string to UUID if valid, else None."""
    return uuid.UUID(user_id) if _is_valid_uuid(user_id) else None


@router.get("/plans")
async def get_subscription_plans():
    """Get all available subscription plans."""
    plans = SubscriptionPlan.get_all_plans()
    return {"plans": plans}


@router.get("/plans/{plan_id}")
async def get_plan_details(plan_id: str):
    """Get details of a specific plan."""
    plan = SubscriptionPlan.get_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return {"plan": plan}


@router.post("/subscriptions/create-order")
async def create_payment_intent(
    request: CreateSubscriptionRequest,
    db: Session = Depends(get_db),
):
    """Create a Razorpay order for subscription payment."""
    user_id = get_current_user_id()
    plan = SubscriptionPlan.get_plan(request.plan_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )

    amount = plan["price"] * 100

    try:
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": f"subscription_{user_id}_{plan['id']}_{datetime.utcnow().timestamp()}",
            "notes": {
                "user_id": user_id,
                "plan_id": plan["id"],
                "plan_name": plan["name"],
            },
        })

        payment = Payment(
            user_id=_user_uuid(user_id),
            order_id=razorpay_order["id"],
            amount=amount,
            currency="INR",
            status=PaymentStatus.PENDING,
            description=f"Subscription to {plan['name']}",
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return PaymentIntentResponse(
            order_id=razorpay_order["id"],
            amount=amount,
            currency="INR",
            key_id=RAZORPAY_KEY_ID or "",
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.post("/subscriptions/confirm")
async def confirm_subscription(
    request: ConfirmSubscriptionRequest,
    db: Session = Depends(get_db),
):
    """Confirm subscription after successful payment."""
    user_id = get_current_user_id()

    payment = db.query(Payment).filter(
        Payment.order_id == request.razorpay_order_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    try:
        razorpay_payment = client.payment.fetch(request.razorpay_payment_id)

        plan = SubscriptionPlan.get_plan(
            razorpay_payment.get("notes", {}).get("plan_id", "")
        )
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan"
            )

        subscription = Subscription(
            user_id=payment.user_id,
            payment_id=payment.id,
            plan=SubscriptionPlan(plan["id"]),
            interval=SubscriptionInterval.MONTHLY,
            amount=plan["price"],
            starts_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=plan["duration_days"]),
            is_active=True,
            auto_renew=True,
        )
        db.add(subscription)

        payment.payment_id = request.razorpay_payment_id
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(subscription)
        db.refresh(payment)

        return {
            "subscription": subscription.to_dict(),
            "plan": plan,
            "payment": payment.to_dict(),
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        payment.status = PaymentStatus.FAILED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm subscription: {str(e)}"
        )


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_razorpay_signature: Optional[str] = Header(None),
):
    """Handle Razorpay webhook events."""
    body = await request.body()
    payload = body.decode("utf-8")

    if x_razorpay_signature:
        if not verify_razorpay_signature(payload, x_razorpay_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )

    import json
    event_data = json.loads(payload)
    event = event_data.get("event")
    payload_data = event_data.get("payload", {})

    try:
        if event == "payment.captured":
            payment_entity = payload_data.get("payment", {})
            order_entity = payload_data.get("order", {})

            razorpay_payment_id = payment_entity.get("id")
            razorpay_order_id = order_entity.get("id")

            payment = db.query(Payment).filter(
                Payment.order_id == razorpay_order_id
            ).first()
            if payment:
                payment.payment_id = razorpay_payment_id
                payment.status = PaymentStatus.COMPLETED
                payment.completed_at = datetime.utcnow()

        elif event == "payment.failed":
            payment_entity = payload_data.get("payment", {})
            razorpay_payment_id = payment_entity.get("id")

            payment = db.query(Payment).filter(
                Payment.payment_id == razorpay_payment_id
            ).first()
            if payment:
                payment.status = PaymentStatus.FAILED

        elif event == "subscription.charged":
            subscription_entity = payload_data.get("subscription", {})
            razorpay_subscription_id = subscription_entity.get("id")

            subscription = db.query(Subscription).filter(
                Subscription.id == razorpay_subscription_id
            ).first()
            if subscription:
                plan = SubscriptionPlan.get_plan(
                    subscription.plan.value if subscription.plan else ""
                )
                if plan:
                    subscription.expires_at = (
                        subscription.expires_at or datetime.utcnow()
                    ) + timedelta(days=plan["duration_days"])
                    subscription.is_active = True

        elif event == "subscription.canceled":
            subscription_entity = payload_data.get("subscription", {})
            razorpay_subscription_id = subscription_entity.get("id")

            subscription = db.query(Subscription).filter(
                Subscription.id == razorpay_subscription_id
            ).first()
            if subscription:
                subscription.is_active = False
                subscription.auto_renew = False
                subscription.canceled_at = datetime.utcnow()

        db.commit()
        return {"status": "success"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/subscriptions/current")
async def get_current_subscription(db: Session = Depends(get_db)):
    """Get current user's active subscription."""
    user_id = get_current_user_id()

    subscription = db.query(Subscription).filter(
        Subscription.user_id == _user_uuid(user_id),
        Subscription.is_active == True,  # noqa: E712
    ).first()

    if subscription:
        plan = SubscriptionPlan.get_plan(
            subscription.plan.value if subscription.plan else ""
        )
        return {
            "subscription": subscription.to_dict(),
            "plan": plan,
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No active subscription found"
    )


@router.post("/subscriptions/cancel")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    db: Session = Depends(get_db),
):
    """Cancel current subscription."""
    user_id = get_current_user_id()

    subscription = db.query(Subscription).filter(
        Subscription.user_id == _user_uuid(user_id),
        Subscription.is_active == True,  # noqa: E712
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    if request.immediate:
        subscription.is_active = False
        subscription.auto_renew = False
        subscription.canceled_at = datetime.utcnow()
    else:
        subscription.auto_renew = False

    db.commit()
    db.refresh(subscription)

    return {
        "subscription": subscription.to_dict(),
        "message": (
            "Subscription canceled immediately"
            if request.immediate
            else "Subscription will be canceled at the end of the current period"
        ),
    }


@router.post("/subscriptions/reactivate")
async def reactivate_subscription(db: Session = Depends(get_db)):
    """Reactivate a canceled subscription."""
    user_id = get_current_user_id()

    subscription = db.query(Subscription).filter(
        Subscription.user_id == _user_uuid(user_id),
        Subscription.auto_renew == False,  # noqa: E712
        Subscription.is_active == True,  # noqa: E712
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription scheduled for cancellation found"
        )

    subscription.auto_renew = True
    db.commit()
    db.refresh(subscription)

    return {
        "subscription": subscription.to_dict(),
        "message": "Subscription reactivated successfully",
    }


@router.get("/history")
async def get_payment_history(db: Session = Depends(get_db)):
    """Get user's payment history."""
    user_id = get_current_user_id()

    user_payments = [
        payment.to_dict()
        for payment in db.query(Payment).filter(
            Payment.user_id == _user_uuid(user_id),
        ).all()
    ]

    return {"payments": user_payments}


@router.post("/subscriptions/upgrade")
async def upgrade_subscription(
    request: CreateSubscriptionRequest,
    db: Session = Depends(get_db),
):
    """Upgrade to a different plan."""
    user_id = get_current_user_id()
    new_plan = SubscriptionPlan.get_plan(request.plan_id)

    if not new_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )

    current_subscription = db.query(Subscription).filter(
        Subscription.user_id == _user_uuid(user_id),
        Subscription.is_active == True,  # noqa: E712
    ).first()

    if not current_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to upgrade"
        )

    current_plan = SubscriptionPlan.get_plan(
        current_subscription.plan.value if current_subscription.plan else ""
    )
    if current_plan and new_plan["price"] <= current_plan["price"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New plan must have a higher price than current plan"
        )

    current_subscription.plan = SubscriptionPlan(new_plan["id"])
    current_subscription.amount = new_plan["price"]
    current_subscription.expires_at = datetime.utcnow() + timedelta(
        days=new_plan["duration_days"]
    )

    db.commit()
    db.refresh(current_subscription)

    return {
        "subscription": current_subscription.to_dict(),
        "plan": new_plan,
        "message": "Subscription upgraded successfully",
    }


@router.get("/commission/calculate")
async def calculate_commission(amount: int):
    """Calculate commission for a marketplace transaction."""
    commission = Commission.calculate(amount)
    return commission
