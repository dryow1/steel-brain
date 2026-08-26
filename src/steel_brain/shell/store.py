"""The Shell's SQLite store: API keys + usage metering. WAL mode, thread-safe."""
import sqlite3, secrets, threading, datetime
from pathlib import Path

class Store:
    def __init__(self, db_path):
        self.db_path = str(db_path)
        self._lock = threading.Lock()
        con = self._con()
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("""CREATE TABLE IF NOT EXISTS api_keys(
            key TEXT PRIMARY KEY, label TEXT, created_at TEXT,
            revoked INTEGER DEFAULT 0, daily_limit INTEGER DEFAULT 100)""")
        con.execute("""CREATE TABLE IF NOT EXISTS usage(
            id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, tool TEXT, ts TEXT)""")
        con.commit(); con.close()

    def _con(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def issue_key(self, label: str, daily_limit: int = 100) -> str:
        key = "sb_" + secrets.token_urlsafe(24)
        with self._lock:
            con = self._con()
            con.execute("INSERT INTO api_keys(key,label,created_at,daily_limit) VALUES(?,?,?,?)",
                        (key, label, datetime.datetime.utcnow().isoformat(), daily_limit))
            con.commit(); con.close()
        return key

    def revoke_key(self, key: str):
        with self._lock:
            con = self._con()
            con.execute("UPDATE api_keys SET revoked=1 WHERE key=?", (key,))
            con.commit(); con.close()

    def key_status(self, key: str):
        con = self._con()
        row = con.execute("SELECT revoked, daily_limit FROM api_keys WHERE key=?", (key,)).fetchone()
        con.close()
        if row is None: return None
        return {"revoked": bool(row[0]), "daily_limit": row[1]}

    def record_usage(self, key: str, tool: str):
        with self._lock:
            con = self._con()
            con.execute("INSERT INTO usage(key,tool,ts) VALUES(?,?,?)",
                        (key, tool, datetime.datetime.utcnow().isoformat()))
            con.commit(); con.close()

    def usage_today(self, key: str) -> int:
        today = datetime.datetime.utcnow().date().isoformat()
        con = self._con()
        n = con.execute("SELECT COUNT(*) FROM usage WHERE key=? AND ts LIKE ?",
                        (key, today + "%")).fetchone()[0]
        con.close()
        return n

    def usage_count(self, key: str) -> int:
        con = self._con()
        n = con.execute("SELECT COUNT(*) FROM usage WHERE key=?", (key,)).fetchone()[0]
        con.close()
        return n
