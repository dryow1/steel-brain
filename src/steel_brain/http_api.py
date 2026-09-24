"""FastAPI app: the public HTTP door. Auth -> rate limit -> meter -> answer.
Also serves the MCP server over streamable HTTP at /mcp (no key; metered, capped per day)."""
import os
import contextlib
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends
from .kb import KB, KB_DIR
from .tools import Tools
from .shell.store import Store
from .mcp_server import build_server
from . import __version__

DB_PATH = os.environ.get("SB_DB", str(Path(__file__).resolve().parents[2] / "shell.db"))
SERVE_UNVERIFIED = os.environ.get("SB_SERVE_UNVERIFIED", "0") == "1"

store = Store(DB_PATH)
kb = KB(KB_DIR, serve_unverified=SERVE_UNVERIFIED)
tools = Tools(kb)

# --- public MCP door (/mcp) ---
MCP_KEY = "mcp-public"   # usage rows for remote MCP calls are logged under this key
MCP_DAILY_CAP = int(os.environ.get("SB_MCP_DAILY_CAP", "2000"))
MCP_HOSTS = [h.strip() for h in os.environ.get(
    "SB_MCP_HOSTS", "api.steelbrain.dev,localhost,127.0.0.1,testserver").split(",") if h.strip()]

def _mcp_meter(tool_name: str):
    if store.usage_today(MCP_KEY) >= MCP_DAILY_CAP:
        raise RuntimeError("Steel Brain public daily limit reached - try again tomorrow (UTC).")
    store.record_usage(MCP_KEY, tool_name)

def _transport_security():
    try:
        from mcp.server.transport_security import TransportSecuritySettings
    except ImportError:
        return {}
    hosts = MCP_HOSTS + [h + ":*" for h in MCP_HOSTS]
    return {"transport_security": TransportSecuritySettings(
        enable_dns_rebinding_protection=True, allowed_hosts=hosts, allowed_origins=[])}

mcp_srv = build_server(on_call=_mcp_meter, tools=tools,
                       stateless_http=True, json_response=True, **_transport_security())
mcp_app = mcp_srv.streamable_http_app()   # route: /mcp

@contextlib.asynccontextmanager
async def lifespan(_app):
    async with mcp_srv.session_manager.run():
        yield

app = FastAPI(title="Steel Brain API", version=__version__, lifespan=lifespan,
              description="Steel domain knowledge for AI agents: grades, substitutions, cert guidance. Answers only from a verified knowledge base - never guesses. MCP (streamable HTTP) at /mcp.")

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

# Mounted last so the /health and /v1 routes above match first; this sub-app serves /mcp.
app.mount("/", mcp_app)
