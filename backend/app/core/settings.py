from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    enable_dev_learning_portal: bool = True
    openai_api_key: str | None = None
    openai_model: str | None = None
    openai_timeout_seconds: float = 20.0
    openai_invalid_output_retries: int = 2
    openai_input_cost_per_million_tokens_usd: float | None = None
    openai_output_cost_per_million_tokens_usd: float | None = None
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "fitcoach_knowledge"
    rag_embedding_provider: str = "local-hash"
    rag_embedding_model: str = "text-embedding-3-small"
    rag_embedding_dimensions: int = 256
    rag_retrieval_limit: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
