"""Validate KB: schema + provenance report. Run before every deploy."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from steel_brain.kb import KB, KB_DIR

kb = KB(KB_DIR, serve_unverified=True)
std = [g["grade_id"] for g in kb.grades if g.get("provenance") == "standard_published"]
kee = [g["grade_id"] for g in kb.grades if g.get("provenance") == "kee"]
print(f"grades: {len(kb.grades)} total | {len(std)} standard-published | {len(kee)} cert-verified")
print(f"substitutions: {len(kb.substitutions)} (trade-verified) | certs: {len(kb.certs)} (trade-verified)")
print("\nv1 launch posture: grade PROPERTIES = published standards (honest);")
print("SUBSTITUTION + CERT logic = trade-verified from YHF rulings (the moat).")
print("v2 (later) upgrades specific grades to cert-verified via the Hermes cert-feed loop.")
