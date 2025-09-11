import hmac, hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from passlib.hash import bcrypt
from core.config import settings

def hash_password(pw: str) -> str:
      return bcrypt.hash(pw)

def verify_password(pw: str, pw_hash: str) -> bool:
      return bcrypt.verify(pw, pw_hash)

def create_token(sub: str, minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=minutes)).timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])

# ---- API Keys ----
API_KEY_PREFIX = "vk_live_"

def generate_api_key() -> tuple[str, str, str]:
    """returns (display_key, prefix, last4) and you store only hash + meta"""
    secret_part = secrets.token_urlsafe(32)
    display = API_KEY_PREFIX + secret_part
    last4 = display[-4:]
    return display, API_KEY_PREFIX, last4

def hash_api_key(display_key: str) -> str:
    # schneidet Prefix ab und HMAC't den Rest
    if not display_key.startswith(API_KEY_PREFIX):
        raise ValueError("Bad key format")
    secret_part = display_key[len(API_KEY_PREFIX):]
    return hmac.new(settings.KEY_HASH_SECRET.encode(), secret_part.encode(), hashlib.sha256).hexdigest()
