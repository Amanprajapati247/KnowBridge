from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    PROJECT_NAME: str = "KnowBridge"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "knowbridge-super-secret-jwt-key-2026-secure-tech-titan")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./knowbridge.db")
    
    # AI Engine & RAG Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

    # Connectors Configuration
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN", None)
    JIRA_INSTANCE_URL: Optional[str] = os.getenv("JIRA_INSTANCE_URL", None)
    JIRA_API_TOKEN: Optional[str] = os.getenv("JIRA_API_TOKEN", None)
    LINEAR_API_KEY: Optional[str] = os.getenv("LINEAR_API_KEY", None)

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
