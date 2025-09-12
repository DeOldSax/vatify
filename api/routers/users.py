from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from deps import get_current_user
from db.session import get_db
from db.models import ApiKey, MonthlyQuota, MonthlyQuotaUser
from schemas.user import UsageOut
from core.config import settings

router = APIRouter()

@router.get("")
async def me(user=Depends(get_current_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "plan": user.plan,
        "emailVerified": user.email_verified
    }

@router.get("/usage", response_model=UsageOut)
async def my_usage(month: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from datetime import datetime
    m = date.today().replace(day=1) if month is None else datetime.strptime(month, "%Y-%m").date().replace(day=1)

    user_keys = await db.execute(select(ApiKey.id).where(ApiKey.user_id == user.id))

    total = 0
    api_quota = await db.execute(select(func.sum(MonthlyQuota.requests))
                                    .where(MonthlyQuota.month == m)
                                    .where(MonthlyQuota.api_key_id.in_(user_keys.scalars())))
    s = api_quota.scalar() or 0

    app_user_quota = await db.execute(select(func.sum(MonthlyQuotaUser.requests))
                                      .where(MonthlyQuotaUser.month == m)
                                      .where(MonthlyQuotaUser.user_id == user.id))
    t = app_user_quota.scalar() or 0

    total = int(s) + int(t)
    return UsageOut(total=total, by_endpoint={})
