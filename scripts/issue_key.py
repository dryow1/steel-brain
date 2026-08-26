"""Issue or revoke API keys. Usage: python scripts/issue_key.py issue "label" [daily_limit] | revoke KEY"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from steel_brain.shell.store import Store
from steel_brain.http_api import DB_PATH

store = Store(DB_PATH)
if sys.argv[1] == "issue":
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    print(store.issue_key(sys.argv[2], limit))
elif sys.argv[1] == "revoke":
    store.revoke_key(sys.argv[2]); print("revoked")
