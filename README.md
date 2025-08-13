# Agentic RAG — Telecom Starter

This repository is a starter demonstrating an **Agentic RAG** orchestration for a telecom prepaid-offer use case.
It includes a FastAPI app, a simple agent loop (plan/act/reflect/generate), and tooling examples (Qdrant + Product Catalog mock).

## Quick start (dev)

1. Copy `.env.example` to `.env` and set variables (optional: OPENAI_API_KEY).
2. Start services with Docker Compose:

```bash
docker-compose up --build
```

3. (Optional) Seed Qdrant with sample plans:
```bash
pip install -r requirements.txt
python scripts/seed_qdrant.py
```

4. POST to `/query`:
```bash
curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"query":"prepaid 4G offers maharashtra 2GB/day"}'
```

## CI

A GitHub Actions workflow is included at `.github/workflows/ci.yml` to run tests with a Qdrant service.

## Notes

- Replace the `fake_embed` with a real embedding model (OpenAI embeddings or sentence-transformers).
- Replace the mock `product_catalog_api` with your real product catalog endpoints.
- The agent is synchronous and intentionally simple — for production, consider async I/O, retries/backoff, tracing, and stronger schema validation.
