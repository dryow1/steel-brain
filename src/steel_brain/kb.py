"""KB loader + validation. Unverified entries load but are NOT servable."""
import json
from pathlib import Path

KB_DIR = Path(__file__).resolve().parents[2] / "kb"

REQUIRED_GRADE_FIELDS = {"grade_id","names","standards","condition","forms",
                         "chemistry","mechanical","typical_applications",
                         "weldability","provenance"}

class KB:
    def __init__(self, kb_dir: Path = KB_DIR, serve_unverified: bool = False):
        self.serve_unverified = serve_unverified
        self.grades = self._load(Path(kb_dir) / "grades.json")
        self.substitutions = self._load(Path(kb_dir) / "substitutions.json")
        self.certs = self._load(Path(kb_dir) / "certs.json")
        self._alias = {}
        for g in self.grades:
            missing = REQUIRED_GRADE_FIELDS - set(g)
            if missing:
                raise ValueError(f"KB entry {g.get('grade_id','?')} missing fields: {missing}")
            for name in [g["grade_id"], *g.get("names", [])]:
                self._alias[self._norm(name)] = g["grade_id"]

    @staticmethod
    def _load(path: Path):
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def _norm(s: str) -> str:
        return "".join(ch for ch in s.lower() if ch.isalnum())

    def _servable(self, entry: dict) -> bool:
        if self.serve_unverified:
            return True
        # grades: servable if provenance set (draft_standards or kee-verified)
        if "provenance" in entry:
            return entry.get("provenance") is not None  # standard_published or kee
        # subs/certs: servable if kee-verified
        return entry.get("verified_by") is not None

    @staticmethod
    def is_kee_verified(entry: dict) -> bool:
        return entry.get("provenance") == "kee" or entry.get("verified_by") == "kee"

    def find_grade(self, query: str):
        gid = self._alias.get(self._norm(query))
        if gid is None:
            return None
        entry = next(g for g in self.grades if g["grade_id"] == gid)
        return entry if self._servable(entry) else None

    def _canon(self, name: str) -> str:
        """Resolve any alias/name to its canonical grade_id; fall back to normalized input."""
        return self._alias.get(self._norm(name), self._norm(name))

    def find_substitution(self, from_grade: str, to_grade: str, application: str):
        f, t = self._canon(from_grade), self._canon(to_grade)
        for r in self.substitutions:
            if (self._canon(r["from"]) == f and self._canon(r["to"]) == t
                    and r["application"] == application and self._servable(r)):
                return r
        return None

    def find_cert(self, grade: str, use_case: str):
        g = self._canon(grade)
        for c in self.certs:
            if self._canon(c["grade"]) == g and self._servable(c):
                if use_case.lower().strip() in c["use_case"].lower() or c["use_case"].lower() in use_case.lower():
                    return c
        return None
