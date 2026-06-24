from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

from app.core.settings import Settings


@dataclass(frozen=True)
class QdrantPoint:
    point_id: str
    vector: list[float]
    payload: dict[str, Any]


class QdrantClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def ensure_collection(self, *, vector_size: int) -> dict[str, Any]:
        path = f"/collections/{self._settings.qdrant_collection}"
        try:
            response = self._request_json("GET", path)
        except error.HTTPError as exc:
            if exc.code != 404:
                raise
            self._request_json(
                "PUT",
                path,
                {
                    "vectors": {
                        "size": vector_size,
                        "distance": "Cosine",
                    }
                },
            )
            response = self._request_json("GET", path)

        current_size = response["result"]["config"]["params"]["vectors"]["size"]
        if current_size != vector_size:
            raise ValueError(
                "existing Qdrant collection vector size does not match embedding output"
            )
        return response

    def upsert_points(self, points: list[QdrantPoint]) -> dict[str, Any]:
        return self._request_json(
            "PUT",
            f"/collections/{self._settings.qdrant_collection}/points?wait=true",
            {
                "points": [
                    {
                        "id": point.point_id,
                        "vector": point.vector,
                        "payload": point.payload,
                    }
                    for point in points
                ]
            },
        )

    def search_points(self, query_vector: list[float], *, limit: int) -> list[dict[str, Any]]:
        response = self._request_json(
            "POST",
            f"/collections/{self._settings.qdrant_collection}/points/query",
            {
                "query": query_vector,
                "limit": limit,
                "with_payload": True,
            },
        )
        result = response.get("result", [])
        if isinstance(result, dict):
            points = result.get("points", [])
            if isinstance(points, list):
                return points
            return []
        if isinstance(result, list):
            return result
        return []

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = parse.urljoin(f"{self._settings.qdrant_url.rstrip('/')}/", path.lstrip("/"))
        headers = {"Content-Type": "application/json"}
        if self._settings.qdrant_api_key:
            headers["api-key"] = self._settings.qdrant_api_key

        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = request.Request(url, data=body, headers=headers, method=method)
        with request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
        if not response_body:
            return {}
        return json.loads(response_body)
