"""Remote MCP door (/mcp, streamable HTTP): lists the 3 tools, answers calls,
stays honest on unknown grades, meters usage, and enforces the daily cap."""
import os, sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
os.environ["SB_SERVE_UNVERIFIED"] = "1"
os.environ.setdefault("SB_DB", os.path.join(os.path.dirname(__file__), "test_shell.db"))

import steel_brain.http_api as api
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def c():
    # the MCP session manager can only start once per process, so share one client
    with TestClient(api.app) as client:
        yield client

HDRS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}


def _rpc(client, method, params=None, id_=1):
    body = {"jsonrpc": "2.0", "id": id_, "method": method}
    if params is not None:
        body["params"] = params
    r = client.post("/mcp", json=body, headers=HDRS)
    assert r.status_code == 200, r.text
    return r.json()


def _payload(res):
    """Tool result as a dict: structuredContent if the SDK sends it, else the JSON text block."""
    if "structuredContent" in res:
        return res["structuredContent"]
    import json
    return json.loads(res["content"][0]["text"])


def _init(client):
    return _rpc(client, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                       "clientInfo": {"name": "test", "version": "0"}})


def test_mcp_initialize_and_list_tools(c):
    assert _init(c)["result"]["serverInfo"]["name"] == "steel-brain"
    names = {t["name"] for t in _rpc(c, "tools/list", {}, 2)["result"]["tools"]}
    assert names == {"grade_lookup", "substitution_check", "cert_guide"}


def test_mcp_call_and_unknown_grade_and_cap(c, monkeypatch):
    start = api.store.usage_today(api.MCP_KEY)
    monkeypatch.setattr(api, "MCP_DAILY_CAP", start + 5)
    _init(c)
    res = _rpc(c, "tools/call", {"name": "grade_lookup", "arguments": {"grade": "4140QT"}}, 3)["result"]
    assert not res.get("isError") and _payload(res)["found"] is True
    res = _rpc(c, "tools/call", {"name": "grade_lookup", "arguments": {"grade": "unicorn999"}}, 4)["result"]
    assert _payload(res)["found"] is False          # honest, no guessing
    assert api.store.usage_today(api.MCP_KEY) == start + 2              # metered
    for i in range(3):                                          # reach cap of 5
        _rpc(c, "tools/call", {"name": "grade_lookup", "arguments": {"grade": "4140QT"}}, 10 + i)
    res = _rpc(c, "tools/call", {"name": "grade_lookup", "arguments": {"grade": "4140QT"}}, 20)["result"]
    assert res.get("isError") is True and "limit" in res["content"][0]["text"]


def test_v1_and_health_still_work(c):
    assert c.get("/health").json()["status"] == "ok"
    assert c.get("/v1/grade/4140QT").status_code == 401        # key still required on REST


def test_mcp_rejects_foreign_host(c):
    r = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
               headers={**HDRS, "Host": "evil.example"})
    assert r.status_code in (400, 421)
