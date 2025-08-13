from datetime import datetime
import logging

logger = logging.getLogger("agentic_rag")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def now_iso():
    return datetime.utcnow().isoformat() + "Z"
