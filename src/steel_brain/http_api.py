"""FastAPI app: the public HTTP door. Auth -> rate limit -> meter -> answer."""
import os
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends
from .kb import KB, KB_DIR
from .tools import Tools
from .shell.store import Store
from . import __version__

DB_PATH = os.environ.get("SB_DB", str(Path(__file__).resolve().parents[2] / "shell.db"))
SERVE_UNVERIFIED = os.environ.get("SB_SERVE_UNVERIFIED", "0") == "1"

store = Store(DB_PATH)
kb = KB(KB_DIR, serve_unverified=SERVE_UNVERIFIED)
tools = Tools(kb)
app = FastAPI(title="Steel Brain API", version=__version__,
              description="Steel domain knowledge for AI agents: grades, substitutions, cert guidance. Answers only from a verified knowledge base - never guesses.")

def auth(x_api_key: str = Header(default=None)):
    if not x_api_key:
        raise HTTPException(401, "Missing X-API-Key header")
    st = store.key_status(x_api_key)
    if st is None or st["revoked"]:
        raise HTTPException(401, "Invalid or revoked API key")
    if store.usage_today(x_api_key) >= st["daily_limit"]:
        raise HTTPException(429, "Daily rate limit reached")
    return x_api_key

@app.get("/health")
def health():
    return {"status": "ok", "version": __version__,
            "grades_loaded": len(kb.grades),
            "grades_servable": sum(1 for g in kb.grades if kb._servable(g))}

@app.get("/v1/grade/{grade}")
def grade_lookup(grade: str, key: str = Depends(auth)):
    store.record_usage(key, "grade_lookup")
    return tools.grade_lookup(grade)

@app.get("/v1/substitution")
def substitution(from_grade: str, to_grade: str, application: str, key: str = Depends(auth)):
    store.record_usage(key, "substitution_check")
    return tools.substitution_check(from_grade, to_grade, application)

@app.get("/v1/cert")
def cert(grade: str, use_case: str, key: str = Depends(auth)):
    store.record_usage(key, "cert_guide")
    return tools.cert_guide(grade, use_case)
