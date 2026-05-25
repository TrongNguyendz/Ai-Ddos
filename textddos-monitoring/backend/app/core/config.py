from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "TextDDOS Monitoring API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "textddos_db"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    # WebSocket
    WS_MAX_CONNECTIONS: int = 1000
    WS_PING_INTERVAL: int = 30

    # AI Model
    MODEL_PATH: str = "./models/ddos_model.pkl"
    MODEL_THRESHOLD: float = 0.8

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Alert Thresholds
    ALERT_HIGH_CONFIDENCE: float = 0.9
    ALERT_MEDIUM_CONFIDENCE: float = 0.7
    ALERT_LOW_CONFIDENCE: float = 0.5
    
    CLOUDFLARE_API_TOKEN: str = "cfut_W4pYhc4ds7qOraCOjFtyCgmSvNWMkDvNt4dKPF2o6763c666"
    CLOUDFLARE_ACCOUNT_ID: str = "1e01e4800cf217d21be33e13d3446600"
    CLOUDFLARE_ZONE_ID: str = "your_zone_id_optional"
    
    REDIS_URL: str = "redis://localhost:6379/0"   # Hoặc redis://user:pass@host:port/0
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
