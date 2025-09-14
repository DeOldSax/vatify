import os, stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from deps import get_current_user
from db.stripe_user import (
    find_user, find_user_by_customer, find_user_by_subscription
)
from core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/billing", tags=["billing"])

# ---------- Models ----------
class CreatePortalIn(BaseModel):
    return_path: str = "/dashboard/billing"

# ---------- DB helpers ----------
async def ensure_stripe_customer(db: AsyncSession, user_id: str) -> str:
    user = await find_user(db, user_id)
    if user.stripe_customer_id:
        return user.stripe_customer_id
    cust = stripe.Customer.create(email=user.email, metadata={"app_user_id": user_id})
    user.stripe_customer_id = cust.id
    await db.commit()
    return cust.id

async def upsert_user_subscription(db: AsyncSession, customer_id: str, subscription_id: str, status: str, current_period_end: int | None = None):
    user = await find_user_by_customer(db, customer_id)
    user.stripe_subscription_id = subscription_id
    user.subscription_status = status
    if current_period_end:
        from datetime import datetime, timezone
        user.current_period_end = datetime.fromtimestamp(current_period_end, tz=timezone.utc)
    await db.commit()

async def update_subscription_status(db: AsyncSession, subscription_id: str, status: str, current_period_end: int | None = None):
    user = await find_user_by_subscription(db, subscription_id)
    user.subscription_status = status
    if current_period_end:
        from datetime import datetime, timezone
        user.current_period_end = datetime.fromtimestamp(current_period_end, tz=timezone.utc)
    await db.commit()

# ---------- Endpoints ----------
@router.post("/checkout/session")
async def create_checkout_session(db: AsyncSession = Depends(get_db), user=Depends(get_current_user),):
    user_id = user.id
    customer_id = await ensure_stripe_customer(db, user_id)

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": settings.STRIPE_PRICE_BASIC, "quantity": 1}],
        success_url=settings.BASE_URL,
        cancel_url=settings.BASE_URL,
        allow_promotion_codes=False,
        metadata={"app_user_id": user_id, "plan": "Vatify Pro Tier"},
    )
    print(session.url)
    print(session)
    return {"id": session.id, "url": session.url}

@router.post("/portal/session")
async def create_portal_session(data: CreatePortalIn, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    user_id = user.id
    customer_id = await ensure_stripe_customer(db, user_id)
    portal = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=settings.BASE_URL + data.return_path,
    )
    return {"url": portal.url}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    print("Webhook received")
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    type_ = event["type"]
    obj = event["data"]["object"]

    if type_ == "checkout.session.completed":
        # Nach Checkout ist ein Subscription-Objekt vorhanden
        customer_id = obj["customer"]
        subscription_id = obj.get("subscription")
        # hole Subscription, um period_end zu bekommen
        if subscription_id:
            sub = stripe.Subscription.retrieve(subscription_id)
            await upsert_user_subscription(
                db,
                customer_id=customer_id,
                subscription_id=subscription_id,
                status=sub["status"],
                current_period_end=sub.get("current_period_end"),
            )

    elif type_ == "customer.subscription.updated":
        await update_subscription_status(
            db,
            subscription_id=obj["id"],
            status=obj["status"],
            current_period_end=obj.get("current_period_end"),
        )

    elif type_ == "customer.subscription.deleted":
        await update_subscription_status(db, subscription_id=obj["id"], status="canceled")

    return {"received": True}
