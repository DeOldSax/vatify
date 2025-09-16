from fastapi.params import Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime, date
import asyncio

from deps import get_current_user
from db.session import AsyncSessionLocal
from db.models import ApiKey, MonthlyQuota, UsageCounter, User
from core.config import settings
from core.security import API_KEY_PREFIX, hash_api_key

class APIKeyAuthQuotaMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_prefixes: list[str]):
        super().__init__(app)
        self.protected_prefixes = protected_prefixes

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not any(path.startswith(p) for p in self.protected_prefixes):
            return await call_next(request)
        
        # Header lesen
        key = request.headers.get("x-api-key")
        if not key and (auth := request.headers.get("Authorization", "")):
            if auth.startswith("Bearer "):
                key = auth[7:]
        if not key:
            return JSONResponse({"error":"Missing API key"}, status_code=401)

        # Key validieren
        try:
            key_hash = hash_api_key(key)
        except Exception:
            return JSONResponse({"error":"Invalid API key format"}, status_code=401)

        async with AsyncSessionLocal() as db:  # eigener Session-Scope
            rec = await db.scalar(select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.revoked == False))
            if not rec:
                return JSONResponse({"error":"Invalid API key"}, status_code=401)

            # Quota prüfen
            month = date.today().replace(day=1)
            agg = await db.get(MonthlyQuota, {"month": month, "api_key_id": rec.id})
            used = agg.requests if agg else 0
            
            user = await get_current_user(request=request, db=db)
            if user.subscription_status == "active":
                limit = 1000  # für Pro-User
            else:
                limit = settings.FREE_MONTHLY_QUOTA  # für MVP: planabhängig => Join User + plan
            
            if used >= limit:
                return JSONResponse({"error":"Free Monthly quota exceeded"}, status_code=429)

            # Rate Limit (einfaches In-Memory Token-Bucket pro Worker – für Prod besser Redis)
            # Für MVP: überspringen oder minimaler Sleep/Counter -> hier weggelassen.

            # Zählung (idealerweise asynchron/Queue; MVP: direkt)
            now = datetime.utcnow()
            endpoint = path
            db.add(UsageCounter(api_key_id=rec.id, endpoint=endpoint, timestamp=now))
            if agg:
                await db.execute(text("UPDATE monthly_quota SET requests = requests + 1 WHERE month=:m AND api_key_id=:k"),
                                 {"m": month, "k": str(rec.id)})
            else:
                db.add(MonthlyQuota(month=month, api_key_id=rec.id, requests=1))
            await db.commit()

        # weiter zum Endpoint
        response = await call_next(request)
        return response
