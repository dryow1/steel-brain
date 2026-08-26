# Registry metadata pack (F12) — submit after deploy

## Name
steel-brain

## One-liner
Steel grade intelligence for AI agents: substitution rules and cert guidance verified by a working steel trader, plus standard grade properties — with an honest line on what's guessed and what's not.

## Description
Steel Brain gives your agent real steel-trade judgment as three tool calls:

- **substitution_check** — can grade A replace grade B for this application? Verdicts WITH reasoning, encoding real trade rules a spec sheet won't tell you: 4140RB (annealed) must never substitute 4140QT (pre-hardened) despite being the same alloy; 316 must never downgrade to 304 for marine; EH36 satisfies an S355 structural request but not vice-versa. These are the mistakes that scrap a job — encoded from a real trader's rulings.
- **cert_guide** — which mill cert applies (EN 10204 3.1/3.2, class certs from ABS/DNV/Lloyd's/BV/ClassNK) and exactly what to check on it. Knows that a classification society is a condition of supply, not a grade.
- **grade_lookup** — properties, chemistry, forms, applications, weldability for 23 grades spanning carbon/alloy/stainless bar, pipe, hollow bar and plate. Aliases handled (4140 = 42CrMo4 = SCM440; S355 = ST52).

**Honesty by design:** grade properties are published-standard ranges (ASTM/EN/JIS/API/ABS) and say so. The substitution and cert logic is the trade-verified part — the knowledge that isn't in any standard. Unknown grades return an honest "not in knowledge base," never a guess. Built for agents serving engineers, estimators, fabricators, and procurement.

## Categories
manufacturing, engineering, materials, procurement, domain-knowledge

## Endpoints
- MCP (stdio): python -m steel_brain.mcp_server
- REST: GET /v1/grade/{grade}, /v1/substitution, /v1/cert (X-API-Key header; free tier 100/day)
- Health: GET /health

## Auth
API key, free tier at launch.

## Submit to
1. Official MCP Registry — github.com/modelcontextprotocol/registry
2. mcp.so
3. smithery.ai
4. glama.ai
(Verify each portal's current flow on the day — registry landscape shifts monthly.)
