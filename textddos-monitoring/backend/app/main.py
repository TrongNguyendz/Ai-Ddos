# FastAPI DDoS Monitoring Backend

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger
from slowapi.middleware import SlowAPIMiddleware

from app.core.database import connect_to_mongo, close_mongo_connection
from app.routers import flows, dashboard, alerts, rules
from app.services.websocket_manager import websocket_manager
from app.services.packet_sniffer import ContinuousPacketSniffer
from slowapi.errors import RateLimitExceeded
# Import limiter
# Import limiter
from app.core.rate_limiter import limiter, _rate_limit_exceeded_handler
import sys
import os
from pathlib import Path
# Thêm đường dẫn để Python tìm thấy module
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from app.core.config import settings
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Real-time DDoS Monitoring API with AI-powered detection",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== RATE LIMITING ====================
app.state.limiter = limiter
# Thêm middleware SlowAPI
app.add_middleware(SlowAPIMiddleware)   # ← Thiếu dòng này!
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Static files for model files
app.mount("/models", StaticFiles(directory="models"), name="models")

# Include routers
app.include_router(flows.router, prefix="/api/v1", tags=["flows"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(rules.router, prefix="/api/v1", tags=["rules"])

# WebSocket endpoint for real-time flow updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):   # ← Thêm ": WebSocket" ở đây
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Nếu không cần nhận message từ client, có thể comment dòng này
            data = await websocket.receive_text()  
            # await websocket_manager.broadcast(data)
    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(websocket)
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "database": "connected" if await connect_to_mongo() else "disconnected"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    global packet_sniffer
    logger.info("Starting DDoS Monitoring API...")
    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    # Khởi động Packet Sniffer
    # Kiểm tra Redis connection (tùy chọn)
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        logger.info("✅ Connected to Redis for Rate Limiting")
    except Exception as e:
        logger.warning(f"Redis connection warning: {e}")
    packet_sniffer = ContinuousPacketSniffer(target_port=8000,interface="MediaTek Wi-Fi 6 MT7921 Wireless LAN Card")
    packet_sniffer.start()
    logger.info("✅ Packet Sniffer + MongoDB connected")

@app.on_event("shutdown")
async def shutdown_event():
    global packet_sniffer
    logger.info("Shutting down DDoS Monitoring API...")
    if packet_sniffer:
        packet_sniffer.stop()
    await close_mongo_connection()
    await websocket_manager.close_all()
    logger.info("Shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
