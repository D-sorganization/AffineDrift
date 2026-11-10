---
issue: 5465
summary: "Calcs requirements.lock, SciPy manifest pin, output JSON byte hash (#5465 slice 1)"
dl_state: "in_review"
next_step: "Merge after CI; slice 2 needs pinned UpstreamDrift regen"
branch: "cursor/5465-repro-manifest-gate-3977"
---

Adds `research/alpha-war/calcs/requirements.lock`, records SciPy and `output_json_sha256`
in the regeneration manifest, and exact version guards in reproducibility tests.
