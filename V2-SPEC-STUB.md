# Steel Brain v2 — Cert-Fed Living KB (SPEC STUB, not scheduled)
**Do not build until v1 shows demand. This is banked, not queued.**

## The idea
New mill certs arrive at YHF constantly. v2 turns that stream into an
auto-updating knowledge base: grade property numbers reflect what's ACTUALLY
in recent certs, not just published standards. This is the compounding moat —
a competitor can copy standards data; nobody can copy YHF's live cert stream.

## Why it's v2, not v1
- v1 must first prove any agent calls Steel Brain at all.
- v2 is v1 + a feeding loop — it cannot exist without v1 shipped.
- v1's query logs tell v2 WHICH grades to prioritise (don't cert-feed all 23 blindly).

## Architecture sketch (reuses the VOC / document-extraction pattern)
1. New cert PDF lands (HeatLookup already indexes these).
2. Hermes extracts: grade, heat no., chemistry, mechanicals.
3. Aggregator updates a per-grade "typical range across last N certs" field —
   SEPARATE from the published-standard field, exposed as its own KB attribute.
4. Outlier flagging: a cert value outside standard range gets held for review,
   never silently averaged in.
5. grade_lookup gains an optional "cert_observed_range" alongside "standard_range",
   and provenance flips that grade to "cert-verified".

## Open design questions (resolve at Gate 1 when scheduled)
- Average vs range vs latest across certs? (probably: range + count + last-seen)
- How many certs before a grade earns "cert-verified"? (min sample size)
- Update cadence: on-arrival vs nightly batch?
- Outlier policy: hold-for-review threshold, who reviews.
- Privacy: cert values are YHF-internal — expose ranges, never customer/heat identifiers.

## Reuse note
The "watch incoming documents -> extract -> update live KB" loop is the SAME
pattern as VOC, dispatch recovery, email-to-quote. Build it once here, formally,
and it generalises across the stack. That reuse is part of what would justify
scheduling v2.

## Trigger to schedule v2
v1 query logs show real, recurring grade_lookup traffic for specific grades
over ~2+ weeks. Then v2 targets those grades first.
