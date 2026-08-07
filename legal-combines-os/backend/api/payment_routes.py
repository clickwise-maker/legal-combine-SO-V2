import hashlib
import hmac
import os
from datetime import datetime, timedelta
from typing import Optional

import razorpay
from fastapi import APIRouter, HTTPException, Depends, Header, Request, status
from pydantic import BaseModel

from backend.models.payment import (
    SubscriptionPlan,
    Subscription,
    Payment,
    Commission,
    SubscriptionStatus,
    PaymentStatus,
    PaymentMethod,
)
from backend.models.user import User


router = APIRouter(prefix="/api/payments", tags=["Payments"])


RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_xxxxxxxxxxxx")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "webhook_secret_xxxxxxxxxxxxx")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-domain.com/api/payments/webhook")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


MOCK_SUBSCRIPTIONS_DB = {}
MOCK_PAYMENTS_DB = {}


class CreateSubscriptionRequest(BaseModel):
    plan_id: str


class CancelSubscriptionRequest(BaseModel):
    immediate: bool = False


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
async def create_payment_intent(request: CreateSubscriptionRequest):
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
            user_id=user_id,
            subscription_id="pending",
            amount=amount,
            razorpay_order_id=razorpay_order["id"],
            description=f"Subscription to {plan['name']}",
            metadata={"plan_id": plan["id"], "plan_name": plan["name"]},
        )
        MOCK_PAYMENTS_DB[payment.id] = payment

        return PaymentIntentResponse(
            order_id=razorpay_order["id"],
            amount=amount,
            currency="INR",
            key_id=RAZORPAY_KEY_ID,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.post("/subscriptions/confirm")
async def confirm_subscription(
    razorpay_payment_id: str,
    razorpay_order_id: str,
):
    """Confirm subscription after successful payment."""
    user_id = get_current_user_id()

    payment = None
    for p in MOCK_PAYMENTS_DB.values():
        if p.razorpay_order_id == razorpay_order_id:
            payment = p
            break

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    try:
        razorpay_payment = client.payment.fetch(razorpay_payment_id)

        plan = SubscriptionPlan.get_plan(payment.metadata.get("plan_id", ""))
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan"
            )

        subscription = Subscription(
            user_id=user_id,
            plan_id=plan["id"],
            status=SubscriptionStatus.ACTIVE,
            razorpay_subscription_id=razorpay_payment_id,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=plan["duration_days"]),
        )
        MOCK_SUBSCRIPTIONS_DB[subscription.id] = subscription

        payment.subscription_id = subscription.id
        payment.razorpay_payment_id = razorpay_payment_id
        payment.status = PaymentStatus.COMPLETED
        payment.payment_method = PaymentMethod(razorpay_payment.get("method", "card"))
        payment.completed_at = datetime.utcnow()

        return {
            "subscription": subscription.to_dict(),
            "plan": plan,
            "payment": payment.to_dict(),
        }

    except Exception as e:
        payment.status = PaymentStatus.FAILED
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm subscription: {str(e)}"
        )


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
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
            notes = order_entity.get("notes", {})
            
            for payment in MOCK_PAYMENTS_DB.values():
                if payment.razorpay_order_id == razorpay_order_id:
                    payment.razorpay_payment_id = razorpay_payment_id
                    payment.status = PaymentStatus.COMPLETED
                    payment.completed_at = datetime.utcnow()

        elif event == "payment.failed":
            payment_entity = payload_data.get("payment", {})
            razorpay_payment_id = payment_entity.get("id")
            
            for payment in MOCK_PAYMENTS_DB.values():
                if payment.razorpay_payment_id == razorpay_payment_id:
                    payment.status = PaymentStatus.FAILED

        elif event == "subscription.charged":
            subscription_entity = payload_data.get("subscription", {})
            razorpay_subscription_id = subscription_entity.get("id")
            
            for subscription in MOCK_SUBSCRIPTIONS_DB.values():
                if subscription.razorpay_subscription_id == razorpay_subscription_id:
                    plan = SubscriptionPlan.get_plan(subscription.plan_id)
                    if plan:
                        subscription.current_period_end = (
                            subscription.current_period_end or datetime.utcnow()
                        ) + timedelta(days=plan["duration_days"])
                        subscription.status = SubscriptionStatus.ACTIVE

        elif event == "subscription.canceled":
            subscription_entity = payload_data.get("subscription", {})
            razorpay_subscription_id = subscription_entity.get("id")
            
            for subscription in MOCK_SUBSCRIPTIONS_DB.values():
                if subscription.razorpay_subscription_id == razorpay_subscription_id:
                    subscription.status = SubscriptionStatus.CANCELED
                    subscription.canceled_at = datetime.utcnow()

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/subscriptions/current")
async def get_current_subscription():
    """Get current user's active subscription."""
    user_id = get_current_user_id()

    for subscription in MOCK_SUBSCRIPTIONS_DB.values():
        if subscription.user_id == user_id and subscription.is_active:
            plan = SubscriptionPlan.get_plan(subscription.plan_id)
            return {
                "subscription": subscription.to_dict(),
                "plan": plan,
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No active subscription found"
    )


@router.post("/subscriptions/cancel")
async def cancel_subscription(request: CancelSubscriptionRequest):
    """Cancel current subscription."""
    user_id = get_current_user_id()

    subscription = None
    for sub in MOCK_SUBSCRIPTIONS_DB.values():
        if sub.user_id == user_id and sub.is_active:
            subscription = sub
            break

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    if request.immediate:
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()
    else:
        subscription.cancel_at_period_end = True

    return {
        "subscription": subscription.to_dict(),
        "message": (
            "Subscription canceled immediately"
            if request.immediate
            else "Subscription will be canceled at the end of the current period"
        ),
    }


@router.post("/subscriptions/reactivate")
async def reactivate_subscription():
    """Reactivate a canceled subscription."""
    user_id = get_current_user_id()

    subscription = None
    for sub in MOCK_SUBSCRIPTIONS_DB.values():
        if sub.user_id == user_id and sub.cancel_at_period_end:
            subscription = sub
            break

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription scheduled for cancellation found"
        )

    subscription.cancel_at_period_end = False

    return {
        "subscription": subscription.to_dict(),
        "message": "Subscription reactivated successfully",
    }


@router.get("/history")
async def get_payment_history():
    """Get user's payment history."""
    user_id = get_current_user_id()

    user_payments = [
        payment.to_dict()
        for payment in MOCK_PAYMENTS_DB.values()
        if payment.user_id == user_id
    ]

    return {"payments": user_payments}


@router.post("/subscriptions/upgrade")
async def upgrade_subscription(request: CreateSubscriptionRequest):
    """Upgrade to a different plan."""
    user_id = get_current_user_id()
    new_plan = SubscriptionPlan.get_plan(request.plan_id)

    if not new_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )

    current_subscription = None
    for sub in MOCK_SUBSCRIPTIONS_DB.values():
        if sub.user_id == user_id and sub.is_active:
            current_subscription = sub
            break

    if not current_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to upgrade"
        )

    current_plan = SubscriptionPlan.get_plan(current_subscription.plan_id)
    if current_plan and new_plan["price"] <= current_plan["price"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New plan must have a higher price than current plan"
        )

    current_subscription.plan_id = new_plan["id"]
    current_subscription.current_period_end = datetime.utcnow() + timedelta(
        days=new_plan["duration_days"]
    )

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
