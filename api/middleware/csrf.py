# app/middleware/csrf.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # nur prüfen, wenn Cookie-Session genutzt wird
        has_access_cookie = "access_token" in request.cookies

        if has_access_cookie and request.method not in SAFE_METHODS:
            header = request.headers.get("x-csrf-token")
            cookie = request.cookies.get("csrf_token")
            if not header or not cookie or header != cookie:
                return JSONResponse({"error": "CSRF token mismatch"}, status_code=403)

        return await call_next(request)
