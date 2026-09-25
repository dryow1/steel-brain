# STATE
- [x] F01 skeleton + tests scaffolded
- [x] F02 KB schema + loader + validator
- [~] F03 KB CONTENT — 23 real grades loaded from Hermes/BMS sources.
        Aliases + substitution rules + cert rulings = KEE-VERIFIED (from ontology).
        Property numbers (chem/tensile/yield/hardness) = DRAFT from standards.
        <-- REMAINING: Kee ticks/corrects the 23 grades' property numbers.
- [x] F04 grade_lookup (alias resolution working: 4140->RB/QT, S355->RB, etc.)
- [x] F05 substitution_check (39 rules; overrides beat generic ladder; guard tests lock dangerous pairs)
- [x] F06 cert_guide (4 use-cases: EH36 ship, API pressure, 316 marine, 4140QT shafts)
- [x] F07 auth
- [x] F08 metering + rate limit
- [x] F09 MCP wrapper + health
- [x] F10 docs
- [x] F11 deploy to VPS -- droplet live since Sep 2026, now serving 0.2.0
- [x] F12 registry submissions -- v1.0.0 tagged + GitHub release cut. Dockerfile
        (stdio, KB baked in) built + verified locally (no docker runtime on
        dev machine, so verified via clean-venv sim of the exact COPY layout:
        real MCP initialize/list_tools/grade_lookup all pass). Image built by
        CI and pushed public to ghcr.io/dryow1/steel-brain:1.0.0. glama.json
        points at the Dockerfile + declares stdio transport.
        Published to the official MCP Registry as io.github.dryow1/steel-brain
        v1.0.0 (oci package, status active). Glama release built + published
        via the admin Dockerfile page -- quality score 58% (up from 33%).
        smithery.ai listed 25 Sep 2026 (see v0.2.0 below).
        mcp.so: skipped by decision ($39 pay-to-publish).

## KB provenance
- 23 grades, all serve now (marked draft where property numbers unconfirmed)
- 39 substitution rules, Kee-verified (from dated ontology rulings)
- 4 cert guides, Kee-verified
- Tests: 19 passing (10 Gate 2 + 5 domain guards + 4 MCP HTTP)

## F03 remaining = property-number review only
Aliases and substitutions are DONE (Kee ruled them already in the ontology).
The only open item is confirming the drafted property numbers per grade.
Run: python scripts/validate_kb.py  -> lists what's still 'draft'.

## v0.2.0 - remote MCP door (24 Sep 2026)
- /mcp: streamable HTTP MCP endpoint on the same FastAPI app (stateless, JSON responses).
  No API key; every call logged under key "mcp-public"; shared daily cap
  SB_MCP_DAILY_CAP (default 2000). Host allowlist SB_MCP_HOSTS (DNS-rebinding guard).
- REST /v1 unchanged (X-API-Key still required).
- Tests: 19 passing (15 existing + 4 in tests/test_mcp_http.py).
- server.json 1.1.0 adds remotes -> https://api.steelbrain.dev/mcp.
- Unlocks: smithery.ai listing (needed a streamable-HTTP /mcp endpoint).
- Count remote callers: sqlite3 shell.db "select date(ts),count(*) from usage where key='mcp-public' group by 1"
- Pinned mcp>=1.10,<2 (25 Sep 2026): mcp 2.x removed the stateless_http kwarg;
  unpinned install on the droplet pulled 2.1.1 and broke test collection.

## v0.2.0 deploy + listings (25 Sep 2026)
- Droplet snapshot "steel-brain-before-mcp" taken before deploy.
- Deployed f449567 to droplet (/root/steel-brain, runs as root): 19 passed on
  the droplet, service restarted. /health -> 0.2.0, 23 servable; /mcp
  tools/list -> 3 tools; yhfsteel.com (same droplet) still 200.
- MCP Registry: io.github.dryow1/steel-brain 1.1.0 published, active + latest,
  remote https://api.steelbrain.dev/mcp. 1.0.0 still active.
- smithery.ai: listed as dryow-jt/steel-brain (gateway
  steel-brain--dryow-jt.run.tools), release SUCCESS, 3 tools found.
