from typing import List, Dict, Any
from .tools import Tools
from .utils import now_iso, logger
from .config import settings
from datetime import datetime, timedelta, timezone
import time

# LLM wrapper — simple OpenAI based wrapper using langchain
try:
    from langchain.llms import OpenAI
except Exception:
    OpenAI = None

class SimpleAgent:
    def __init__(self):
        self.tools = Tools()
        openai_key = settings.openai_api_key
        if openai_key and OpenAI:
            self.llm = OpenAI(openai_api_key=openai_key, temperature=0.0)
        else:
            self.llm = None

        # state
        self.retrieved: List[Dict[str, Any]] = []
        self.plan_steps: List[str] = []
        self.confidence = 0.0

    def plan(self, query: str, region: str = "Maharashtra") -> List[Dict[str, Any]]:
        # Decide steps based on heuristics. For telecom: check KB then live API if stale
        steps = [
            {"tool": "vector_search", "args": {"query": query, "limit": 5}},
            {"tool": "product_catalog_api", "args": {"region": region}},
        ]
        self.plan_steps = steps
        logger.info("Planned steps: %s", steps)
        return steps

    def act(self, step: Dict[str, Any]):
        tool = step.get("tool")
        args = step.get("args", {})
        if tool == "vector_search":
            return self.tools.vector_search(**args)
        elif tool == "product_catalog_api":
            return self.tools.product_catalog_api(**args)
        elif tool == "web_search":
            return self.tools.web_search(args.get("query"))
        else:
            logger.warning("Unknown tool: %s", tool)
            return []

    def reason(self, results: List[Dict[str, Any]]):
        # Merge results into self.retrieved; normalize structure
        for r in results:
            # If result already has payload / schema, keep
            if isinstance(r, dict) and ("payload" in r or "name" in r):
                self.retrieved.append(r)
            else:
                # wrap
                self.retrieved.append({"payload": r})

    def reflect(self) -> bool:
        # Check freshness: if any catalog item newer than X or if retrieved empty
        # now = datetime.utcnow()
        now = datetime.now(timezone.utc)
        freshest = None
        for item in self.retrieved:
            payload = item.get("payload") or item
            last_updated = payload.get("last_updated")
            if last_updated:
                try:
                    dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                    if freshest is None or dt > freshest:
                        freshest = dt
                except Exception:
                    continue
        # freshness rule: if no freshest or older than 3 days -> low confidence (needs API)
        if freshest is None:
            self.confidence = 0.4
            return False
        if freshest.tzinfo is None:
            freshest = freshest.replace(tzinfo=timezone.utc)
        age = now - freshest
        if age > timedelta(days=3):
            self.confidence = 0.5
            return False
        self.confidence = 0.9
        return True

    def generate(self, query: str) -> Dict[str, Any]:
        # Build simple prompt using retrieved items
        plans = []
        for r in self.retrieved:
            p = r.get("payload") if isinstance(r, dict) else r
            if not p:
                continue
            plans.append({
                "name": p.get("name"),
                "price": p.get("price"),
                "data_per_day": p.get("data_per_day"),
                "validity_days": p.get("validity_days"),
                "source": p.get("source", "catalog"),
                "last_updated": p.get("last_updated"),
            })

        generated_at = now_iso()

        # Optionally call LLM to create a natural-language summary (if available)
        summary = None
        if self.llm:
            prompt = f"User query: {query}\n\nAvailable plans:\n"
            for pl in plans:
                prompt += f"- {pl['name']} | {pl['data_per_day']} | ₹{pl['price']} | {pl['validity_days']} days | updated {pl.get('last_updated')}\n"
            prompt += "\nProvide a concise summary highlighting new or recent plans and any notes about freshness."
            try:
                summary = self.llm(prompt)
            except Exception as e:
                logger.warning("LLM call failed: %s", e)
                summary = None

        return {
            "query": query,
            "plans": plans,
            "generated_at": generated_at,
            "confidence": self.confidence,
            "summary": summary,
        }

    def run(self, query: str, region: str = "Maharashtra"):
        # Orchestration loop: plan -> act -> reason -> reflect -> maybe repeat -> generate
        steps = self.plan(query, region)
        for step in steps:
            res = self.act(step)
            # small delay to emulate network calls; in real use remove
            time.sleep(0.1)
            self.reason(res if isinstance(res, list) else [res])

        ok = self.reflect()
        if not ok:
            # If not confident, run a fallback web_search or retry product API once
            logger.info("Not confident after initial retrieval — calling web_search + retrying product API")
            web = self.act({"tool": "web_search", "args": {"query": query}})
            self.reason(web if isinstance(web, list) else [web])
            # retry product API
            prod = self.act({"tool": "product_catalog_api", "args": {"region": region}})
            self.reason(prod if isinstance(prod, list) else [prod])
            # re-evaluate
            ok = self.reflect()

        return self.generate(query)
