---
issue: 4927
summary: "Correct simulation, local optimization and feedback guarantees"
dl_state: "in_review"
next_step: "Deliver the regular PR after verified parent remote-main delivery, then verify accepted blobs on fetched main"
owner: "codex"
branch: "fix/simulation-feedback-review"
---

Complete Volume V chapters 4–6 reviewed. RNEA is separated from integration and inverse kinematics. Simulation reuses the canonical three-link golf model and rejects unsupported/nonfinite data. The wrong iLQR value update and nonexistent line search are replaced by a derived, tested quadratic core and an explicit nonlinear acceptance protocol. Constant-target gravity PD, moving-target computed torque, regional contraction and finite-time funnel guarantees have separate assumptions and consequences.

51 actual-listing tests pass after failing/erroring against the originals; 89 combined checks pass. Six independent 100-case checks pass, maximum error 1.289e-10 below 1e-6. Five successful Flash reviews/proposals were lead-adjudicated; one failed oversized invocation is excluded. Frozen source bece6bee500fb24f82530794e059faab94e44531 passed 7,172 tests, 29 skipped, 210 deselected, 60 warnings in 426.26 seconds, 93.25% coverage, exit 0 and unchanged tracked tree. All five pre-PR gates passed, including 51 mapped tests. PDF pass 8 has 52 pages and 28 references; scoped pages inspected with no scoped overflow or unresolved references. No complete optimizer, whole-volume or empirical human certification.

Parent #4923 is regular PR #4930, head 55ded1e2e. Accepted corpus has 407 rows and 56 pending-prefix rows after this batch's three complete chapters. These are heterogeneous scope labels, not a scientific completion percentage. Acceptance and eight exact hashes: reports/technical-review/simulation-feedback-validation.json. Decisions, primary-reading scope, failures and handoff: docs/development/technical-review/simulation-feedback-review/review-notes.md. Never merge into the topic parent. Retarget after verified remote-main parent delivery and use the central automerge guard. #4889 has green current-head CI but arming remains blocked by GraphQL quota; do not assume queued. Own lease through 05:13:09 UTC and expanded presence through 06:03:56. Bibliography stash backup retained. Next bounded work is #4931, Volume V chapters 7–9, in AffineDrift-inference-policy-analysis-review. No edits to shared SPEC/HANDOFF/DEVELOPMENT_LOG.
