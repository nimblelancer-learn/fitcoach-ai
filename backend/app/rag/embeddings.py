from __future__ import annotations

import hashlib
import math
import re
from typing import Any

try:
    from openai import OpenAI
except ModuleNotFoundError:

    class OpenAI:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ModuleNotFoundError("openai package is required for OpenAI embeddings")


from app.core.settings import Settings

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class EmbeddingClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: OpenAI | None = None

    def vector_size(self) -> int:
        if self._settings.rag_embedding_provider == "openai":
            return self._settings.rag_embedding_dimensions
        return self._settings.rag_embedding_dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        provider = self._settings.rag_embedding_provider
        if provider == "openai":
            return self._embed_with_openai(texts)
        if provider == "local-hash":
            return [
                _hash_embed(text=text, dimensions=self._settings.rag_embedding_dimensions)
                for text in texts
            ]
        raise ValueError(f"unsupported embedding provider: {provider}")

    def _embed_with_openai(self, texts: list[str]) -> list[list[float]]:
        if not self._settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when RAG_EMBEDDING_PROVIDER=openai")

        if self._client is None:
            self._client = OpenAI(api_key=self._settings.openai_api_key)

        response = self._client.embeddings.create(
            model=self._settings.rag_embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]


def _hash_embed(*, text: str, dimensions: int) -> list[float]:
    if dimensions <= 0:
        raise ValueError("embedding dimensions must be positive")

    vector = [0.0] * dimensions
    tokens = TOKEN_PATTERN.findall(text.lower())
    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        weight = 1.0 + (digest[5] / 255.0)
        vector[index] += sign * weight

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
