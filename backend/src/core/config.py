from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
while not (BASE_DIR / ".env").exists() and BASE_DIR.parent != BASE_DIR:
    BASE_DIR = BASE_DIR.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Конфигурация приложения.
    """

    app_name: str = "Review classifier"
    app_version: str = "1.0.0"

    # LLM (OpenRouter)
    openrouter_api_key: str | None = None

    openrouter_model: str | None = "qwen/qwen3.5-35b-a3b"

    openrouter_instuct_model: str = "qwen/qwen3-235b-a22b-2507"

    openrouter_base_url: str | None = "https://openrouter.ai/api/v1"

    deytona_api_key: str | None = None

    # Настройки Pydantic
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,  # игнорировать регистр
        extra="ignore",
    )

    def __init__(self, **data):
        super().__init__(**data)


@lru_cache
def get_settings() -> Settings:
    """
    Создаёт и кеширует единственный экземпляр настроек.
    Использует lru_cache, чтобы не парсить .env каждый раз.
    """
    return Settings()


settings = get_settings()
