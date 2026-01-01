"""Configuration settings for AURA"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "aura_db"
    POSTGRES_USER: str = "aura_user"
    POSTGRES_PASSWORD: str = "aura_password"
    DATABASE_URL: str = ""
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # Google Speech-to-Text
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_PROJECT_ID: str = ""
    
    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Model Serving
    MODEL_SERVING_URL: str = "http://localhost:8501"
    
    # WebSocket
    WEBSOCKET_PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # RL Training
    RL_BATCH_SIZE: int = 1000
    RL_UPDATE_FREQUENCY: int = 1000
    RL_WEEKLY_RETRAIN_SIZE: int = 10000
    
    # Voice Activity Detection
    VAD_SILENCE_THRESHOLD_MS: int = 650  # 500-800ms range, using 650ms
    
    # Latency target
    MAX_LATENCY_MS: int = 3000  # 3 seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields like REACT_APP_* from .env
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )


settings = Settings()

