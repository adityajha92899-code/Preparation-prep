from pydantic_settings import BaseSettings
from typing import Dict, Any
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    GOOGLE_AI_KEY: str = ""
    GOOGLE_AI_MODEL: str = "models/chat-bison-001"

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/maang_prep"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "change-this-secret-key"

    # Models
    PRIMARY_MODEL: str = "models/chat-bison-001"
    CODING_MODEL: str = "models/chat-bison-001"
    FAST_MODEL: str = "models/chat-bison-001"
    LOCAL_MODEL: str = "codellama:34b"

    # Vector store
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX: str = "maang-prep"

    # App settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7

    COMPANY_DATA: Dict[str, Any] = {
        "Google": {
            "tier": "MAANG",
            "avg_lpa": 55,
            "max_lpa": 100,
            "rounds": 5,
            "focus": ["Graph", "DP", "String", "System Design"],
            "values": ["Googleyness", "Leadership", "Collaboration"],
            "interview_style": "whiteboard + google docs",
        },
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
