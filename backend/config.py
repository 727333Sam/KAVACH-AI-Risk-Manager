"""
Configuration management for AI Risk Manager
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    environment: str = "development"

    # Database
    database_url: str = "postgresql://riskmanager:riskmanager_dev@localhost:5432/razorpay_risk"

    # Redis
    redis_url: str = "redis://localhost:6379"
    cache_expiry_seconds: int = 3600

    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    # ML Configuration
    ml_model_path: str = "./backend/ml/models"

    # Risk thresholds (defaults)
    fraud_threshold: float = 0.75
    chargeback_threshold: float = 0.65
    return_fraud_threshold: float = 0.70

    # False-positive tolerance
    max_fpr: float = 0.005  # 0.5%
    fpr_alert_threshold: float = 0.01  # 1%

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
