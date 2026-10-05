---
issue: 4927
summary: "Correct simulation, local optimization and feedback guarantees"
dl_state: "in_progress"
next_step: "Complete final PDF inspection and frozen regression, accept three corpus rows, then open a regular PR against fix/platform-model-contracts-review"
owner: "codex"
branch: "fix/simulation-feedback-review"
---

Complete Volume V chapters 4–6 reviewed. RNEA is separated from integration and inverse kinematics. Simulation reuses the canonical three-link golf model and rejects unsupported/nonfinite data. The wrong iLQR value update and nonexistent line search are replaced by a derived, tested quadratic core and an explicit nonlinear acceptance protocol. Constant-target gravity PD, moving-target computed torque, regional contraction and finite-time funnel guarantees have separate assumptions and consequences.

51 actual-listing tests pass after failing/erroring against the originals. Six independent 100-case checks pass, maximum error 1.289e-10 below 1e-6. Five successful Flash reviews/proposals were lead-adjudicated; one failed oversized invocation is excluded. Decisions, rejected findings, source-reading scope and handoff details are in docs/development/technical-review/simulation-feedback-review/review-notes.md. Initial PDF has 52 pages and 28 references; final affected pages and frozen regression remain pending. No complete optimizer, whole-volume or empirical human certification.

Parent #4923 is regular PR #4930, head 55ded1e2e. Accepted corpus currently has 407 rows, 59 pending-prefix rows; this batch's three rows are not yet accepted. Source stays on fix/simulation-feedback-review; never merge into the topic parent. Retarget after verified remote-main parent delivery and use the central automerge guard. #4889 has green current-head CI but REST auto_merge null; GraphQL reset is 04:21:03 UTC. Own lease through 05:13:09 UTC and presence through 05:12:07. Bibliography stash backup retained. No edits to shared SPEC/HANDOFF/DEVELOPMENT_LOG.
