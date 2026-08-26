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
- [ ] F11 deploy to VPS <-- SUNDAY
- [ ] F12 registry submissions <-- MONDAY

## KB provenance
- 23 grades, all serve now (marked draft where property numbers unconfirmed)
- 39 substitution rules, Kee-verified (from dated ontology rulings)
- 4 cert guides, Kee-verified
- Tests: 15 passing (10 Gate 2 + 5 domain guards)

## F03 remaining = property-number review only
Aliases and substitutions are DONE (Kee ruled them already in the ontology).
The only open item is confirming the drafted property numbers per grade.
Run: python scripts/validate_kb.py  -> lists what's still 'draft'.
