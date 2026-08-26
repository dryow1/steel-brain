"""The three tools. Honest 'not in KB' responses - never guess."""
from .kb import KB

NOT_IN_KB_MSG = "Not in knowledge base. Steel Brain only answers from verified entries - it never guesses."

class Tools:
    def __init__(self, kb: KB):
        self.kb = kb

    def grade_lookup(self, grade: str) -> dict:
        g = self.kb.find_grade(grade)
        if g is None:
            return {"found": False, "message": NOT_IN_KB_MSG, "query": grade}
        return {"found": True, "grade": g,
                "property_source": g.get("property_source", ""),
                "note": "Grade properties are published-standard ranges. Substitution and cert guidance are trade-verified."}

    def substitution_check(self, from_grade: str, to_grade: str, application: str) -> dict:
        r = self.kb.find_substitution(from_grade, to_grade, application)
        if r is None:
            return {"found": False,
                    "query": {"from": from_grade, "to": to_grade, "application": application},
                    "message": NOT_IN_KB_MSG + " No verified rule covers this combination - treat as NOT approved."}
        return {"found": True, "verdict": r["verdict"], "reasoning": r["reasoning"],
                "from": r["from"], "to": r["to"], "application": r["application"]}

    def cert_guide(self, grade: str, use_case: str) -> dict:
        c = self.kb.find_cert(grade, use_case)
        if c is None:
            return {"found": False, "message": NOT_IN_KB_MSG,
                    "query": {"grade": grade, "use_case": use_case}}
        return {"found": True, "cert_types": c["cert_types"], "check_fields": c["check_fields"],
                "notes": c.get("notes", "")}
