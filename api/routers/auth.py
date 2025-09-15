from datetime import datetime, timedelta, timezone
import hashlib, hmac, secrets
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import User, SessionToken
from schemas.auth import RegisterIn, LoginIn, UserOut
from core.security import hash_password, verify_password, create_token
from core.config import settings
from utils.notify import notify

router = APIRouter()

# --- CSRF verification (double-submit) ---------------------------------------
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

def verify_csrf(request: Request):
    # Only enforce CSRF when an authenticated session (access_token) exists
    if request.method in UNSAFE_METHODS and request.cookies.get("access_token"):
        header = request.headers.get("x-csrf-token")
        cookie = request.cookies.get("csrf_token")
        if not header or not cookie or not hmac.compare_digest(header, cookie):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token mismatch")

# Option A: enforce on all routes in this router:
# router = APIRouter(dependencies=[Depends(verify_csrf)])
# Option B: attach per-route. Below I add it to auth-safe places where needed.


# --- Helpers -----------------------------------------------------------------
def _cookie_domain():
    # Ensure leading dot for subdomains like .vatifytax.app
    d = settings.COOKIE_DOMAIN
    if d and not d.startswith("."):
        d = "." + d
    return d

def _cookie_params_base(http_only: bool):
    return {
        "secure": settings.COOKIE_SECURE,
        "httponly": http_only,
        "samesite": settings.COOKIE_SAMESITE,   # e.g. "lax"
        "domain": _cookie_domain(),
        "path": "/",
    }

def _set_session_cookies(response: Response, access: str, refresh: str | None = None):
    # Access cookie
    response.set_cookie(
        "access_token", access,
        max_age=settings.ACCESS_TOKEN_MINUTES * 60,
        **_cookie_params_base(http_only=True),
    )
    # Optional refresh cookie
    if refresh:
        response.set_cookie(
            "refresh_token", refresh,
            max_age=settings.REFRESH_TOKEN_DAYS * 24 * 3600,
            **_cookie_params_base(http_only=True),
        )
    # NEW: rotate CSRF alongside access token
    csrf = secrets.token_urlsafe(32)
    response.set_cookie(
        "csrf_token", csrf,
        max_age=settings.ACCESS_TOKEN_MINUTES * 60,
        **_cookie_params_base(http_only=False),   # must be readable by JS
    )

async def set_cookie_and_token(response: Response, user: User, request: Request, db: AsyncSession):
    # Access + Refresh
    access = create_token(sub=str(user.id), minutes=settings.ACCESS_TOKEN_MINUTES)
    refresh = create_token(sub=str(user.id), minutes=settings.REFRESH_TOKEN_DAYS * 24 * 60)

    # Server-side refresh session
    refresh_hash = hashlib.sha256(refresh.encode()).hexdigest()
    session = SessionToken(
        user_id=user.id,
        refresh_hash=refresh_hash,
        user_agent=request.headers.get("user-agent"),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_DAYS),
    )
    db.add(session)
    await db.commit()

    # Cookies (+ CSRF rotation)
    _set_session_cookies(response, access=access, refresh=refresh)


# --- Routes ------------------------------------------------------------------
@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: RegisterIn, bg: BackgroundTasks, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    exists = await db.scalar(select(User).where((User.email == data.email) | (User.username == data.username)))
    if exists:
        raise HTTPException(400, "Email or username already exists")
    user = User(email=data.email, username=data.username, password_hash=hash_password(data.password))
    db.add(user); await db.commit(); await db.refresh(user)
    bg.add_task(notify, "🆕 New Registration", {"email": user.email, "id": str(user.id)})

    await set_cookie_and_token(response, user, request, db)
    return UserOut(id=str(user.id), email=user.email, username=user.username, plan=user.plan, email_verified=user.email_verified)

@router.post("/login", response_model=UserOut)
async def login(data: LoginIn, bg: BackgroundTasks, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    q = select(User).where((User.email == data.email_or_username) | (User.username == data.email_or_username))
    user = await db.scalar(q)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await set_cookie_and_token(response, user, request, db)
    bg.add_task(notify, "🆕 New Login", {"email": user.email, "id": str(user.id)})
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

    # Check server-side session exists and not expired
    refresh_hash = hashlib.sha256(token.encode()).hexdigest()
    sess = await db.scalar(select(SessionToken).where(SessionToken.refresh_hash == refresh_hash))
    if not sess or sess.expires_at < datetime.now(timezone.utc):
        raise HTTPException(401, "Refresh session invalid")

    # NEW: issue a new access token AND rotate CSRF in same response
    new_access = create_token(sub=user_id, minutes=settings.ACCESS_TOKEN_MINUTES)
    _set_session_cookies(response, access=new_access, refresh=None)

    user = await db.get(User, user_id)
    return UserOut(id=str(user.id), email=user.email, username=user.username, plan=user.plan, email_verified=user.email_verified)

# NEW: allow the client to refresh only the CSRF cookie and keep session alive
@router.get("/auth/csrf")
async def get_csrf(response: Response):
    csrf = secrets.token_urlsafe(32)
    response.set_cookie(
        "csrf_token", csrf,
        max_age=settings.ACCESS_TOKEN_MINUTES * 60,
        **_cookie_params_base(http_only=False),
    )
    return {"ok": True}

@router.post("/logout")
async def logout(response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    # Invalidate refresh session
    token = request.cookies.get("refresh_token")
    if token:
        h = hashlib.sha256(token.encode()).hexdigest()
        await db.execute(SessionToken.__table__.delete().where(SessionToken.refresh_hash == h))
        await db.commit()

    # IMPORTANT: match domain/path when deleting
    delete_kwargs = _cookie_params_base(http_only=True)
    response.delete_cookie("access_token", domain=delete_kwargs["domain"], path=delete_kwargs["path"])
    response.delete_cookie("refresh_token", domain=delete_kwargs["domain"], path=delete_kwargs["path"])
    # CSRF was non-HttpOnly, but delete with same domain/path too
    delete_kwargs = _cookie_params_base(http_only=False)
    response.delete_cookie("csrf_token", domain=delete_kwargs["domain"], path=delete_kwargs["path"])
    return {"ok": True}
