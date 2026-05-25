from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request

# ==================== SỬA Ở ĐÂY ====================
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",          # ← Dùng memory thay vì Redis
    default_limits=["100/minute"],
    headers_enabled=True
    # storage_uri=settings.REDIS_URL,   # comment tạm dòng này
)
# =================================================

def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Quá nhiều yêu cầu. Vui lòng thử lại sau.",
            "type": "rate_limit_exceeded",
            "limit": str(exc.detail)
        }
    )