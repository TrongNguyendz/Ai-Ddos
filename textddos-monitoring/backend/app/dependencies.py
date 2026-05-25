from typing import Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import Depends, HTTPException, status,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from fastapi import Request, Depends

from app.core.config import settings
from app.core.database import get_flows_collection

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validate JWT token and return user ID
    This is a placeholder - implement proper authentication
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

# Dependency để inject rate limit (nếu cần dùng trong một số router)
async def rate_limit_dependency(request: Request):
    # SlowAPI sẽ tự handle qua decorator, hàm này chỉ để check nếu cần
    pass

# Dependency injection helpers
async def get_db():
    """Get database instance"""
    from app.core.database import get_database
    return await get_database()

# Common validation helpers
def validate_flow_data(flow_data: dict) -> dict:
    """Validate and sanitize flow data"""
    from app.utils.helpers import validate_ip, parse_protocol

    required_fields = ["switch", "src_ip", "dst_ip", "protocol", "pktrate", "tot_kbps", "pktcount", "bytecount"]

    for field in required_fields:
        if field not in flow_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )

    # Validate IPs
    if not validate_ip(flow_data["src_ip"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source IP address"
        )

    if not validate_ip(flow_data["dst_ip"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid destination IP address"
        )

    # Parse protocol
    flow_data["protocol"] = parse_protocol(flow_data["protocol"])

    return flow_data
