# Steel Brain API
Steel grade intelligence for AI agents. Trade-verified substitution & cert logic + standard grade properties.

## What's verified vs standard
- **Substitution rules & cert guidance:** trade-verified from a working steel trader's dated rulings. This is the moat.
- **Grade property numbers:** published-standard ranges (ASTM/EN/JIS/API/ABS), honestly labelled. v2 upgrades these to cert-verified via an automated cert-feed.

## Quick start (dev)
pip install -r requirements.txt
python -m pytest tests/            # 15 tests (10 gate + 5 domain guards)
python scripts/issue_key.py issue "dev" 100
uvicorn steel_brain.http_api:app --app-dir src
# open http://localhost:8000/docs

## Status
v1 complete. 23 grades, 39 substitution rules, 4 cert guides. Ready to deploy.
