# steel-brain — project rules
MCP tool server: steel domain knowledge for other people's agents.
Spec: GATE1-STEEL-BRAIN.md (frozen — do not expand scope).

## Hard rules
- NO BMS, NO YHF data, NO prices, NO stock. Ever.
- Unknown grade -> honest "not in KB" response. Never infer or guess properties.
- Every KB entry needs "verified_by": "kee" + date. Unverified entries are NOT served.
- One feature per commit. Update STATE.md after every commit.
- Tests first. Gate 2 scorecard = tests/test_gate2.py (10 tests).

## Layout
kb/            grades.json, substitutions.json, certs.json  (THE PRODUCT)
src/steel_brain/
  kb.py        loader + validation (rejects malformed/unverified)
  tools.py     grade_lookup, substitution_check, cert_guide
  shell/       auth.py (API keys), metering.py, ratelimit.py
  http_api.py  FastAPI app (public HTTP door, X-API-Key header)
  mcp_server.py  MCP stdio server (registry door)
scripts/       validate_kb.py, issue_key.py
deploy/        setup_vps.sh, steel-brain.service, RUNBOOK.md
registry/      metadata for the 4 registry submissions
