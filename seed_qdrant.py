# Minimal seeding script to push a few sample prepaid plan documents to Qdrant.
from qdrant_client import QdrantClient
from app.config import settings
import os
import uuid

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

#client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
client = QdrantClient(host=qdrant_host, port=qdrant_port)
#print(settings.qdrant_host, settings.qdrant_port, settings.qdrant_collection)

collection = settings.qdrant_collection

# Create collection (if not exists) - using simple config
try:
    client.recreate_collection(collection_name=collection, vectors_config={"size": 1536, "distance": "Cosine"})
except Exception:
    pass

items = [
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "plan-199-2gb")),
        "vector": [0.01] * 1536,
        "payload": {
            "name": "Super 2GB/day",
            "price": 199,
            "data_per_day": "2GB",
            "validity_days": 28,
            "last_updated": "2025-08-12T10:00:00Z",
            "source": "kb",
        },
    },
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "plan-299-3gb")),
        "vector": [0.02] * 1536,
        "payload": {
            "name": "Ultra 3GB/day",
            "price": 299,
            "data_per_day": "3GB",
            "validity_days": 30,
            "last_updated": "2025-08-13T09:00:00Z",
            "source": "kb",
        },
    },
]

client.upsert(collection_name=collection, points=items)
print("Seeded Qdrant with sample plans")
