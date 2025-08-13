from fastapi import FastAPI, HTTPException
from .schemas import QueryRequest, QueryResponse, PlanItem
from .agent import SimpleAgent
from .utils import logger

app = FastAPI(title="Agentic RAG — Telecom Starter")
agent = SimpleAgent()

@app.post("/query", response_model=QueryResponse)
async def handle_query(req: QueryRequest):
    try:
        result = agent.run(req.query, region=req.region)
        # normalize into QueryResponse
        plans = []
        for p in result.get("plans", []):
            plans.append(PlanItem(
                name=p.get("name") or "unknown",
                price=p.get("price") or 0.0,
                data_per_day=p.get("data_per_day") or "",
                validity_days=int(p.get("validity_days") or 0),
                source=p.get("source") or "catalog",
                last_updated=p.get("last_updated"),
            ))
        resp = QueryResponse(
            query=result.get("query"),
            plans=plans,
            generated_at=result.get("generated_at"),
            confidence=float(result.get("confidence") or 0.0),
            notes=result.get("summary"),
        )
        return resp
    except Exception as e:
        logger.exception("Error handling query")
        raise HTTPException(status_code=500, detail=str(e))
