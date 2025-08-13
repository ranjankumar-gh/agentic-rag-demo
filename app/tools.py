# Tool wrappers: vector_search, product_catalog_api, web_search
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from .config import settings
import requests
from .utils import logger

# NOTE: Vector embedding function is left abstract — replace with your embedding
# model (OpenAI embeddings, sentence-transformers, etc.)

def fake_embed(text: str) -> List[float]:
    # Placeholder embedding - replace with real embedding call
    return [hash(text) % 1000 / 1000.0 for _ in range(1536)]

class Tools:
    def __init__(self):
        self.qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    def vector_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        emb = fake_embed(query)
        try:
            hits = self.qdrant.search(collection_name=settings.qdrant_collection, query_vector=emb, limit=limit)
            results = []
            for h in hits:
                payload = h.payload or {}
                results.append({
                    "id": h.id,
                    "score": h.score,
                    "payload": payload,
                })
            return results
        except Exception as e:
            logger.warning("Qdrant search failed: %s", e)
            return []

    def product_catalog_api(self, region: str):
        # If PRODUCT_CATALOG_URL set, call real API. Otherwise return mock.
        if settings.product_catalog_url:
            try:
                res = requests.get(settings.product_catalog_url, params={"region": region}, timeout=5)
                res.raise_for_status()
                return res.json()
            except Exception as e:
                logger.warning("Product catalog call failed: %s", e)
                return []

        # Mocked product catalog response
        mock = [
            {"name": "Super 2GB/day", "price": 199, "data_per_day": "2GB", "validity_days": 28, "last_updated": "2025-08-12T10:00:00Z"},
            {"name": "Ultra 3GB/day", "price": 299, "data_per_day": "3GB", "validity_days": 30, "last_updated": "2025-08-13T09:00:00Z"},
        ]
        return mock

    def web_search(self, query: str):
        # Placeholder web search tool - return empty or small mock
        logger.info("web_search called for query: %s", query)
        return []
