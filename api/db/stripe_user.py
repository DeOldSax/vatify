# app/db/helpers/stripe_user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User

async def find_user(db: AsyncSession, user_id: str) -> User:
    """Hole User via App-User-ID (UUID als str)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"User {user_id} not found")
    return user

async def find_user_by_customer(db: AsyncSession, customer_id: str) -> User:
    """Hole User via Stripe Customer ID."""
    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"No user for stripe_customer_id={customer_id}")
    return user

async def find_user_by_subscription(db: AsyncSession, subscription_id: str) -> User:
    """Hole User via Stripe Subscription ID."""
    result = await db.execute(select(User).where(User.stripe_subscription_id == subscription_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"No user for stripe_subscription_id={subscription_id}")
    return user
