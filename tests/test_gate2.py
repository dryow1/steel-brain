"""Gate 2 scorecard - the 10 acceptance tests from GATE1-STEEL-BRAIN.md.
Tests run against format-example KB with SB_SERVE_UNVERIFIED=1 (test mode).
Before real deploy, F03 replaces examples with Kee-verified entries and
the same tests pass with SB_SERVE_UNVERIFIED unset."""
import os, sys, threading, importlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
os.environ["SB_SERVE_UNVERIFIED"] = "1"
os.environ["SB_DB"] = os.path.join(os.path.dirname(__file__), "test_shell.db")

# fresh DB per test session
if os.path.exists(os.environ["SB_DB"]):
    os.remove(os.environ["SB_DB"])

import steel_brain.http_api as api
importlib.reload(api)
from fastapi.testclient import TestClient

client = TestClient(api.app)
KEY = api.store.issue_key("gate2-tests", daily_limit=50)

def _get(path, key=KEY, **params):
    headers = {"X-API-Key": key} if key else {}
    return client.get(path, headers=headers, params=params)

# T1 - grade_lookup returns properties
def test_t1_grade_lookup_4140qt():
    r = _get("/v1/grade/4140QT")
    assert r.status_code == 200 and r.json()["found"]
    g = r.json()["grade"]
    assert g["grade_id"] == "4140QT"
    assert "chemistry" in g and "mechanical" in g
    assert g["mechanical"]["hardness_hb"][0] == 248  # QT hardness

# T2 - unknown grade -> graceful, no hallucination
def test_t2_unknown_grade_honest():
    r = _get("/v1/grade/unicorn999")
    assert r.status_code == 200
    body = r.json()
    assert body["found"] is False and "not in knowledge base" in body["message"].lower()

# T3 - substitution valid case
def test_t3_substitution_machined_valid():
    r = _get("/v1/substitution", from_grade="1020RB", to_grade="4140QT", application="machined")
    assert r.json()["found"] and r.json()["verdict"] == "valid"

# T4 - substitution invalid case with reason
def test_t4_substitution_heat_treat_invalid():
    r = _get("/v1/substitution", from_grade="4140RB", to_grade="4140QT", application="machined")
    body = r.json()
    assert body["found"] and body["verdict"] == "invalid" and body["reasoning"]

# T5 - cert guide mentions class certs
def test_t5_cert_guide_eh36():
    r = _get("/v1/cert", grade="EH36", use_case="shipbuilding")
    body = r.json()
    assert body["found"]
    joined = " ".join(body["cert_types"])
    assert "DNV" in joined and "ABS" in joined

# T6 - auth: no key -> 401; revoked key -> 401
def test_t6_auth():
    assert _get("/v1/grade/4140", key=None).status_code == 401
    k2 = api.store.issue_key("revoke-me")
    api.store.revoke_key(k2)
    assert _get("/v1/grade/4140", key=k2).status_code == 401

# T7 - metering: 10 calls -> 10 rows under correct key
def test_t7_metering():
    k3 = api.store.issue_key("meter-test", daily_limit=50)
    for _ in range(10):
        assert _get("/v1/grade/S355", key=k3).status_code == 200
    assert api.store.usage_count(k3) == 10

# T8 - rate limit triggers at threshold
def test_t8_rate_limit():
    k4 = api.store.issue_key("limit-test", daily_limit=3)
    for _ in range(3):
        assert _get("/v1/grade/4140", key=k4).status_code == 200
    assert _get("/v1/grade/4140", key=k4).status_code == 429

# T9 - MCP server builds and registers exactly the 3 tools
def test_t9_mcp_tools():
    from steel_brain.mcp_server import build_server
    import anyio
    mcp = build_server()
    tools = anyio.run(mcp.list_tools)
    names = {t.name for t in tools}
    assert names == {"grade_lookup", "substitution_check", "cert_guide"}

# T10 - concurrent calls don't corrupt the meter
def test_t10_concurrent_metering():
    k5 = api.store.issue_key("concurrent-test", daily_limit=200)
    errors = []
    def worker():
        try:
            r = _get("/v1/grade/4140", key=k5)
            assert r.status_code == 200
        except Exception as e:
            errors.append(e)
    threads = [threading.Thread(target=worker) for _ in range(20)]
    [t.start() for t in threads]; [t.join() for t in threads]
    assert not errors
    assert api.store.usage_count(k5) == 20


# --- Domain guard tests (beyond the 10 Gate 2 tests) ---
# These lock in Kee's do-not-substitute rulings so a KB rebuild can't silently break them.

def test_guard_4140_heat_treat_never_valid():
    for f,t in [("4140RB","4140QT"),("4140QT","4140RB")]:
        r = _get("/v1/substitution", from_grade=f, to_grade=t, application="machined")
        assert r.json()["verdict"] == "invalid", f"{f}->{t} must be invalid"

def test_guard_316_to_304_never_valid():
    r = _get("/v1/substitution", from_grade="SS316L", to_grade="SS304L", application="machined")
    assert r.json()["verdict"] == "invalid"

def test_guard_eh36_to_ms36_never_valid():
    r = _get("/v1/substitution", from_grade="EH36PL", to_grade="MS36PL", application="welded-structural")
    assert r.json()["verdict"] == "invalid"

def test_guard_seamless_required_for_pressure():
    r = _get("/v1/substitution", from_grade="APISML", to_grade="APIERW", application="pressure")
    assert r.json()["verdict"] == "invalid"

def test_guard_all_grades_have_provenance():
    # every grade must carry provenance; none silently unmarked
    import steel_brain.http_api as api
    for g in api.kb.grades:
        assert g.get("provenance") in ("kee","standard_published"), g["grade_id"]
