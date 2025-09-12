import uuid
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from core.security import decode_token
from db.models import User

from fastapi import Depends, HTTPException, status
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db
from db.models import MonthlyQuotaUser
from core.config import settings


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    # Access Token aus Authorization Bearer ODER Cookie 'access_token'
    token = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_token(token)
        sub = payload["sub"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # sub -> UUID konvertieren
    try:
        user_id = uuid.UUID(sub)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user



async def check_and_increment_user_quota(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    month = date.today().replace(day=1)

    # Summe aller API-Key-Nutzungen des Users im Monat
    sum_keys_sql = text("""
        SELECT COALESCE(SUM(mq.requests), 0)
        FROM monthly_quota mq
        JOIN api_keys k ON k.id = mq.api_key_id
        WHERE k.user_id = :uid AND mq.month = :m
    """)
    used_keys = (await db.execute(sum_keys_sql, {"uid": str(user.id), "m": month})).scalar() or 0

    # Bisherige App-Nutzung des Users
    row = await db.get(MonthlyQuotaUser, {"month": month, "user_id": user.id})
    used_app = row.requests if row else 0

    used_total = used_keys + used_app
    limit = settings.FREE_MONTHLY_QUOTA  # optional: planabhängig erweitern

    if used_total >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Monthly quota exceeded")

    # ✅ jetzt den App-Call zählen
    if row:
        await db.execute(
            text("UPDATE monthly_quota_user SET requests = requests + 1 WHERE month=:m AND user_id=:u"),
            {"m": month, "u": str(user.id)}
        )
    else:
        db.add(MonthlyQuotaUser(month=month, user_id=user.id, requests=1))
    await db.commit()

