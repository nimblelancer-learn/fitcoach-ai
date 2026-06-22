from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    enable_dev_learning_portal: bool = True
    openai_api_key: str | None = None
    openai_model: str | None = None
    openai_timeout_seconds: float = 20.0
    openai_invalid_output_retries: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
