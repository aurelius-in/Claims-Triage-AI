"""
Configuration management for the Claims Triage AI platform.
"""

import os
from functools import lru_cache
from typing import Optional, List
from pydantic import BaseSettings, Field, validator
from pydantic.types import SecretStr


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Claims Triage AI"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # API
    api_v1_prefix: str = "/api/v1"
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Security
    secret_key: SecretStr = Field(env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Database
    database_url: str = Field(env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # ML Models
    model_registry_path: str = Field(default="./ml/models", env="MODEL_REGISTRY_PATH")
    feature_store_path: str = Field(default="./ml/features", env="FEATURE_STORE_PATH")
    
    # LLM Configuration
    openai_api_key: Optional[SecretStr] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[SecretStr] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_llm_provider: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")
    
    # OPA (Open Policy Agent)
    opa_url: str = Field(default="http://localhost:8181", env="OPA_URL")
    opa_policies_path: str = Field(default="./policies", env="OPA_POLICIES_PATH")
    
    # Vector Store
    vector_store_url: str = Field(default="http://localhost:6333", env="VECTOR_STORE_URL")
    vector_store_api_key: Optional[SecretStr] = Field(default=None, env="VECTOR_STORE_API_KEY")
    
    # Monitoring
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    grafana_port: int = Field(default=3000, env="GRAFANA_PORT")
    
    # File Storage
    upload_path: str = Field(default="./uploads", env="UPLOAD_PATH")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Triage Configuration
    risk_threshold_high: float = Field(default=0.7, env="RISK_THRESHOLD_HIGH")
    risk_threshold_medium: float = Field(default=0.4, env="RISK_THRESHOLD_MEDIUM")
    confidence_threshold: float = Field(default=0.8, env="CONFIDENCE_THRESHOLD")
    
    # Teams and Queues
    default_teams: List[str] = Field(default=[
        "Tier-1", "Tier-2", "Specialist", "Fraud-Review", "Escalation"
    ], env="DEFAULT_TEAMS")
    
    # Compliance
    audit_log_retention_days: int = Field(default=365, env="AUDIT_LOG_RETENTION_DAYS")
    pii_detection_enabled: bool = Field(default=True, env="PII_DETECTION_ENABLED")
    
    # CORS
    allowed_origins: List[str] = Field(default=["http://localhost:3000"], env="ALLOWED_ORIGINS")
    
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("default_teams", pre=True)
    def parse_default_teams(cls, v):
        if isinstance(v, str):
            return [team.strip() for team in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
