from datetime import datetime, timedelta, timezone
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import User, SessionToken
from schemas.auth import RegisterIn, LoginIn, UserOut
from core.security import hash_password, verify_password, create_token
from core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    exists = await db.scalar(select(User).where((User.email == data.email) | (User.username == data.username)))
    if exists:
        raise HTTPException(400, "Email or username already exists")
    user = User(email=data.email, username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut(id=str(user.id), email=user.email, username=user.username, plan=user.plan, email_verified=user.email_verified)

@router.post("/login", response_model=UserOut)
async def login(data: LoginIn, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    q = select(User).where((User.email == data.email_or_username) | (User.username == data.email_or_username))
    user = await db.scalar(q)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Access + Refresh
    access = create_token(sub=str(user.id), minutes=settings.ACCESS_TOKEN_MINUTES)
    refresh = create_token(sub=str(user.id), minutes=settings.REFRESH_TOKEN_DAYS*24*60)

    # Refresh-Session serverseitig speichern (hash)
    refresh_hash = hashlib.sha256(refresh.encode()).hexdigest()
    session = SessionToken(user_id=user.id,
                           refresh_hash=refresh_hash,
                           user_agent=request.headers.get("user-agent"),
                           expires_at=datetime.now(timezone.utc)+timedelta(days=settings.REFRESH_TOKEN_DAYS))
    db.add(session); await db.commit()

    # Cookies setzen (optional; alternativ Header zurückgeben)
    cookie_params = {"httponly": True, "secure": settings.COOKIE_SECURE, "samesite": settings.COOKIE_SAMESITE}
    if settings.COOKIE_DOMAIN: cookie_params["domain"] = settings.COOKIE_DOMAIN
    response.set_cookie("access_token", access, **cookie_params, max_age=settings.ACCESS_TOKEN_MINUTES*60)
    response.set_cookie("refresh_token", refresh, **cookie_params, max_age=settings.REFRESH_TOKEN_DAYS*24*3600)

    import secrets
    csrf = secrets.token_urlsafe(32)
    response.set_cookie(
        "csrf_token", csrf,
        httponly=False,  # MUSS lesbar sein
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN or None,
        max_age=settings.ACCESS_TOKEN_MINUTES*60
    )

    return UserOut(id=str(user.id), email=user.email, username=user.username, plan=user.plan, email_verified=user.email_verified)

@router.post("/refresh", response_model=UserOut)
async def refresh_token(response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    import jwt
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(401, "Missing refresh token")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except Exception:
        raise HTTPException(401, "Invalid refresh token")
    user_id = payload["sub"]

    # prüfen, ob Session existiert
    import hashlib
    refresh_hash = hashlib.sha256(token.encode()).hexdigest()
    sess = await db.scalar(select(SessionToken).where(SessionToken.refresh_hash == refresh_hash))
    if not sess or sess.expires_at < datetime.now(timezone.utc):
        raise HTTPException(401, "Refresh session invalid")

    # neues Access
    access = create_token(sub=user_id, minutes=settings.ACCESS_TOKEN_MINUTES)
    cookie_params = {"httponly": True, "secure": settings.COOKIE_SECURE, "samesite": settings.COOKIE_SAMESITE}
    if settings.COOKIE_DOMAIN: cookie_params["domain"] = settings.COOKIE_DOMAIN
    response.set_cookie("access_token", access, **cookie_params, max_age=settings.ACCESS_TOKEN_MINUTES*60)

    # user laden
    user = await db.get(User, user_id)
    return UserOut(id=str(user.id), email=user.email, username=user.username, plan=user.plan, email_verified=user.email_verified)

@router.post("/logout")
async def logout(response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    # refresh session invalidieren (hash entfernen)
    token = request.cookies.get("refresh_token")
    if token:
        import hashlib
        h = hashlib.sha256(token.encode()).hexdigest()
        await db.execute(SessionToken.__table__.delete().where(SessionToken.refresh_hash == h))
        await db.commit()
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"ok": True}
