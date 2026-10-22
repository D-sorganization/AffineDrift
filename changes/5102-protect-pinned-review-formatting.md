---
issue: 5102
summary: "Protect the Pinned Shot-Pattern Review from Prettier"
next_step: "Preserve the review bytes and inventory pin; future content changes require separate review and attestation."
branch: "fix/ci-render-cache-5116"
paths: ".prettierignore, tests/test_prettier_drift_5102.py"
---

The owner approved exempting only
`reports/shot-pattern-publication/technical-review.md` from Prettier. Its bytes
and existing SHA-256 inventory pin remain unchanged; this formatter decision
does not re-review or re-attest the scientific content.

The separate historical fragment requests no delivery-state transition, so
collation retains the shipped entry and its earlier PR evidence.
