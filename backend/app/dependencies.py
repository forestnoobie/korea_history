"""Dependency injection helpers."""
from functools import lru_cache

from .services.opensearch_service import OpenSearchService


@lru_cache(maxsize=1)
def get_opensearch_service() -> OpenSearchService:
    return OpenSearchService()
