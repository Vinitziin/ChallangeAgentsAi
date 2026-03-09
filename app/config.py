"""Arquivo para centralizar as configurações"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings sourced from .env file."""

    # LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()

    # Tavily
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "").strip()

    # OpenWeatherMap
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "").strip()

    # PostgreSQL
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "assistant_db")

    # ChromaDB
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "chroma")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))

    @property
    def postgres_uri(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
