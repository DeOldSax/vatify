from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from core.security import decode_token
from db.models import User

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

    user = await db.scalar(select(User).where(User.id.cast(str) == sub))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
