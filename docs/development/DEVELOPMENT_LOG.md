# Development Log — AffineDrift

State table for every feature in flight in this repository. Update
entries **in place**; never append dated sections. One entry per
feature, from proposal to ship. See the `development-logs` section of
`AGENTS.md` for the binding rules and
`shared_scripts/development_log.py` for the validator.

- **Portfolio:** personal
- **WIP limit:** 2
- **Last audited:** 2026-08-28 by bootstrap
- **Shipped records:** [2026 archive](DEVELOPMENT_LOG_ARCHIVE_2026.md)

## States

`proposed` → `in_progress` → `in_review` → `shipped`, with `parked`
reachable from any live state and `abandoned` from `parked`.
`shipped` never returns to `in_progress`; open a new entry instead.

## Active

### DL-#4821 · Counterfactual Intervention and Evidence Review

- **State:** in_progress
- **Owner:** codex
- **PR:** pending; predecessor #4820 remains in CI
- **Issue:** #4821; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/counterfactual-rigor-4821
- **Paths:** articles/proximal_distal_companion/chapters/ch11_counterfactual_scissors.qmd, scripts/make_proximal_distal_companion_figures.py, tests/test_counterfactual_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 baseline dc1884f2084a1caaa1b135201e751e330afe24e2; four focused passes;12gates/655titles/894filequality;238pagePDF,53math,4browsercells pass;initial27affected passes plus2scratch-hygiene failures remediated with6passes; final29affected checks pass.
- **Summary:** Eight issue findings distinguish complete-state intervention, nonlinear finite effects, geometry controls, strategy comparisons and human inference. Supplied-text Flash helpers support data arithmetic and test drafting; four helper outputs lead-adjudicated; publication validated, broad regression and acceptance/binding pending. No audit credit yet;103 source audits plus whole-book consistency remain.
- **Next step:** Run the full regression before final source acceptance and corpus binding.

### DL-#4819 · Practical Synthesis Evidence and Causal Comparisons

- **State:** in_review
- **Owner:** codex
- **PR:** #4820 (regular, combined Chapters18/28); parent #4818 verified on remote main
- **Issue:** #4819; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/synthesis-rigor-4819
- **Paths:** articles/proximal_distal_companion/chapters/ch28_practical_synthesis.qmd, scripts/make_proximal_distal_companion_review_figures.py, tests/test_synthesis_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 682b709bc31459a882421062d2632282b78ed356 baseline;6632tests pass,29skip,187deselected,79.33%coverage;12gates,893Python files,655titles;237pagePDF,48math and4browserprofiles pass.
- **Summary:** Lead accepted eight scientific decisions connecting wrench/power, hidden hand allocations, task velocity, feasible interventions, finite Pareto results, measurement limits and frontend scope. Five Flash outputs adjudicated. Source 1a7521e581bab0e6aa40df3f9bf0cb5ddafdee66 committed; eight findings bound with201 prior findings preserved,209total and103pending source audits. All44post-binding checks pass; source and binding c19ff2d993ea0a0a0f1cd8151e54b03df93d1869 are verified on remote topic with normal hooks.
- **Next step:** Push PR4820 registration, remove temporary integration hold and arm guarded squash auto-merge; verify exact checked head and remote-main owned files after merge.

### DL-#4817 · Forward Solver Guarantees and Validation

- **State:** in_review
- **Owner:** codex
- **PR:** #4820 (regular, combined Chapters18/28); parent #4818 verified on remote main
- **Issue:** #4817; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/synthesis-rigor-4819
- **Paths:** articles/proximal_distal_companion/chapters/ch18_forward_model.qmd, scripts/make_proximal_distal_companion_expanded_figures.py, tests/test_forward_model_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 baseline 33afa9d25b7f61113ff4a0928d2cef2c2b1da76e; five focused passes after one RED failure;234pagePDF/HTML/56math/4browserchecks,12gates,892filequality; broad6624pass/4metadata-hygienefail,40remediationpass,79.35%accumulatedcoverage; source e4540364c6a21b66df55eb2959beef4e5eed9a2d committed; eight findings bound;40postbinding checks pass; source and binding 66a5bed3773a8991978fd7df7c27066d5cf0b9dc verified on remote topic with normal hooks.
- **Summary:** Correct fixed-mode KKT assumptions, multiplier units, projection/work ledgers, moving-boundary compatibility, input memory, counterfactuals, evidence scope and coordinate/contact comparisons. Six successful Flash outputs adjudicated. Eight findings bound to the accepted source;193 prior companion findings preserved,201total;104 source audits and whole-book consistency remain.
- **Next step:** Push PR4820 registration, remove temporary integration hold and arm guarded squash auto-merge; verify exact checked head and remote-main owned files after merge.

### DL-#4495 — Make 404 Page and Empty States Useful

- **State:** in_review
- **Owner:** antigravity
- **PR:** #4796 (regular)
- **Issue:** #4495; epic #4496
- **Branch:** fix/web-01-10-404-useful-4495
- **Paths:** 404.qmd, tests/test_404_page.py, SPEC.md
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; pytest tests/test_404_page.py (6 passed); ruff, black, mypy clean.
- **Summary:** Added prominent links for Start Here (/resources/learning-paths.html), the Library (/books/index.html), search box trigger, top destinations, and verified unified contact email dieterolson@AffineDrift.com matching contact.qmd.
- **Next step:** Passing CI Standard, squash auto-merge armed.



### DL-#4756 · Complete-State Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** [#4758](https://github.com/D-sorganization/AffineDrift/pull/4758)
- **Issue:** #4756 (epic #4009)
- **Branch:** fix/state-snapshot-rigor-4756
- **Paths:** articles/proximal_distal_companion/chapters/ch03_state_snapshot.qmd, scripts/make_proximal_distal_companion_figures.py, tests/test_state_snapshot_review.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (six new checks;12 publication gates;654 titles;Ruff/Black836;CI-scoped mypy94;221-page PDF/parity/changed-page inspection;4 browser/axe cases;full6401 passes/29 skips/78.9% configured coverage/93.0% src;63 affected)
- **Summary:** Correct complete-state, velocity-reversal, intervention and observation arguments with five Flash support jobs and lead adjudication. Seven findings bound to source 44b29ef73bf187c4b9220a90ff9e1a08a45bed20;55 prior findings preserved;124 full-source audits plus whole-book consistency remain.
- **Next step:** Delivered through merged PR #4765 on remote main 39f7553b562b6d83e5aff36d9277bbcbfcaff401; source/evidence parity verified in reports/technical-review/geometry-remote-main-receipt.json. Predecessors #4758/#4762 and issues #4756/#4759/#4763 are closed. No remaining work for this bounded review.

### DL-#4753 · Arm–Wrist Preload Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4755 (verified main carrier)
- **Issue:** #4753 (epic #4009)
- **Branch:** fix/preload-rigor-4753
- **Paths:** articles/proximal_distal_companion/chapters/ch14_arms_wrists_preload.qmd, scripts/make_proximal_distal_companion_expanded_figures.py, tests/test_preload_review.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (Delivery audit against main `1b255c15a089ab7ad97e508216bbfc281f4fa482`: Merged to main at394a7b40b; chapter and test still match fetched main. Receipt: reports/technical-review/prior-delivery-reconciliation.json. Historical validation retained: 2026-10-01 (full default suite PASS/29 skips/78.8% configured coverage/93.0% src;63 integrated;36 bound;12 publication gates;Ruff/Black835;CI-scoped mypy94;654 titles;220-page PDF/source-public parity;4 browser/axe cases))
- **Summary:** Full chapter corrections distinguish moment/wrench, conditional dynamics, causal inference and human evidence; replace wrong command-only figure with archived transmission traces. Five Flash support jobs, lead-adjudicated.Seven findings bound to exact source8ffffbc7e;48 historical findings preserved;125 full-source audits plus whole-book consistency remain.
- **Next step:** None for this delivered scope.


### DL-#4751 · Shaft Memory Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4755 (verified main carrier)
- **Issue:** #4751 (epic #4009)
- **Branch:** fix/shaft-memory-rigor-4751
- **Paths:** articles/proximal_distal_companion/chapters/ch15_shaft_memory.qmd, scripts/shaft_energy_illustration.py, tests/test_shaft_memory_review.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (Delivery audit against main `1b255c15a089ab7ad97e508216bbfc281f4fa482`: Delivered through4755 at394a7b40b;4752 closed unmerged. Five dedicated predecessor blobs match the carrier and fetched main. Receipt: reports/technical-review/prior-delivery-reconciliation.json. Historical validation retained: 2026-10-01 (63 integrated;12 gates;Ruff/Black834;final browser4/4 and axe;218-page PDF/parity;full6385 pass/4 concurrent-artifact failures, all affected reruns pass))
- **Summary:** Correct power, state, model-domain and endpoint interpretations with five Flash support jobs and lead adjudication. Seven findings bound to final source899f35bb0 after exact Git-blob parity checks;41 historical findings preserved;126 full-source audits remain.
- **Next step:** None for this delivered scope.

### DL-#4749 · Falsification Atlas Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4750 (regular; main target)
- **Issue:** #4749 (epic #4009)
- **Branch:** fix/atlas-rigor-4749
- **Paths:** articles/proximal-distal-falsification-atlas.qmd, articles/_generated/proximal-distal-falsification-atlas.qmd, data/trust/proximal_distal_falsification_atlas.json, src/affine_control/falsification_atlas/rendering.py, tests/test_falsification_atlas_identities.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (PR4750 open;seven findings bound;32 final binding checks pass;full6381 pass/one stale-registry failure/29 skips;unsupported release withdrawn;73 integrated checks pass;12 gates;653 titles;Ruff/Black832;four final browser/axe cases)
- **Summary:** Distinguish source adjudication from editorial comparisons; correct force/wrench, coordinate-metric and support/compliance comparisons with five Flash support jobs and lead adjudication.
- **Next step:** None for atlas source: PR4750 merged remote main 5b58cb68b619815214014ef4d7c9cd353d23ed87; exact source/generator/ledger/test parity verified.4741 and4748 also merged.

### DL-#4746 · Critics Corner Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4748 (regular; main target)
- **Issue:** #4746 (epic #4009)
- **Branch:** fix/critics-rigor-4746
- **Paths:** articles/tangent-hyperplane-articles/CRITICS_CORNER.qmd, tests/test_critics_corner_identities.py, reports/technical-review/critics-corner-review.md
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (73 focused pass;12 gates;653 titles;Ruff/Black831;96 MathJax expressions;full6372 pass/two root-hygiene failures;packaging artifacts preserved;18 follow-up and53 integrated checks pass;strict button9/10 plus two reruns pass with one navigation timeout retained)
- **Summary:** Correct the excluded critique's error transport, pendulum units, algorithmic and empirical claims, contraction and hybrid-event arguments with lead-reviewed Flash support.
- **Next step:** None for this source: PR4748 merged to remote main 4c1ddafa5a51c2be28361bc574618a9a146f99fa; exact source/tests/reports verified.

### DL-#4743 · Muscle Models and Coupled Power

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4745 (regular; main target)
- **Issue:** #4743 (epic #4009)
- **Branch:** fix/muscle-model-rigor-4743
- **Paths:** articles/The_Geometry_of_Motion/Volume_III/chapters/ch03_muscle_models.tex, articles/The_Geometry_of_Motion/geometry_of_motion.bib, tests/test_muscle_models_review.py, tests/test_muscle_model_identities.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (main a473831 verified; source d7be93d34; full6318 pass/five book-audit digest failures/29 skipped/93.04%; digest repair88 then bound89 passes;184 content/four skips;12 gates;653-title audit;PDF68pages/17 pages and browser4/4 verified)
- **Summary:** Correct force curves and attribution; connect excitation, fiber state, series equilibrium, tendon storage, joint power and stiffness under explicit model/empirical boundaries.
- **Next step:** None for this chapter; PR4745 merged to remote main a473831731989fce80f110bcc34745affe9ad837 on 2026-10-01. Exact source/PDF/tests verified; continue remaining corpus reviews.

### DL-#4742 · Force Direction and Reference Points

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4741 (verified main carrier)
- **Issue:** #4742 (epic #4009)
- **Branch:** `fix/force-direction-rigor-4742`
- **Paths:** `articles/proximal_distal_companion/chapters/ch09_force_direction.qmd`, `articles/figures/proximal_distal_companion/fig_companion_force_direction.svg`, `scripts/make_proximal_distal_companion_figures.py`, `tests/test_force_direction_review.py`, `reports/technical-review/force-direction-review.md`
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (Delivery audit against main `1b255c15a089ab7ad97e508216bbfc281f4fa482`: Delivered through4741 atcf0d11368;4744 merged only into its topic branch. Four dedicated predecessor blobs match the main carrier and fetched main. Receipt: reports/technical-review/prior-delivery-reconciliation.json. Historical validation retained: 2026-10-01 (source52408; full6281 pass/one stale source-contract failure,93.04%; repaired;59 focused then79 bound-audit and88 integration checks pass;184 content/4 skips;216-page PDF and browser4/4 verified))
- **Summary:** Correct force reference points and axis conventions; explain coupled response, two-hand geometric controls, observer-dependent power and measurement limits.
- **Next step:** None for this delivered scope.

### DL-#4739 · Force, Work, and Energy Boundaries

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4741 (verified main carrier)
- **Issue:** #4739 (epic #4009)
- **Branch:** `fix/force-work-rigor-4739`
- **Paths:** `articles/proximal_distal_companion/chapters/ch10_force_work_motion.qmd`, `articles/proximal-distal-a-journey-through-the-swing.pdf`, `tests/test_force_work_review.py`, `reports/technical-review/force-work-review.md`
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (Delivery audit against main `1b255c15a089ab7ad97e508216bbfc281f4fa482`: Merged to main atcf0d11368; chapter and test still match fetched main. Nine head-to-merge differences concern the peer critics-corner integration and metadata. Receipt: reports/technical-review/prior-delivery-reconciliation.json. Historical validation retained: 2026-10-01 (source803b58ecb; PDF/chapter browser verified; full6272 pass/one pin failure,93.04%; pin repaired;53 affected checks and184 content checks pass/4 skips;12 publication checks and freshness browser4/4 pass; final protected CI pending))
- **Summary:** Correct three-dimensional work, net impulse, internal mechanical-energy conversion, coordinate-force versus physical work and archive scope; preserve human-model limits and prior book findings.
- **Next step:** None for this delivered scope.



### DL-#4733 · Shallow-Wide Latency and Synergy Arguments

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4734 (verified main carrier)
- **Issue:** #4733 (epic #4009)
- **Branch:** `fix/shallow-wide-rigor-4733`
- **Paths:** `articles/The_Geometry_of_Motion/Volume_IV/chapters/ch04_shallow_wide.tex`, `articles/The_Geometry_of_Motion/Volume_IV/main.pdf`, `articles/The_Geometry_of_Motion/geometry_of_motion.bib`, `books/human-motor-control.qmd`, `tests/test_shallow_wide_review.py`, `reports/technical-review/shallow-wide-review.md`
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (Delivery audit against main `1b255c15a089ab7ad97e508216bbfc281f4fa482`: Merged to main at7eb87e3c9; VolumeIV Chapter4, PDF, human-motor-control source and test match reviewed head and fetched main. Receipt: reports/technical-review/prior-delivery-reconciliation.json. Historical validation retained: 2026-10-01 (SELF: CI failure reproduced and repaired;66 focused/184 content passes, four skips; audit/book/catalog freshness and Ruff/Black pass. CI36826515629 six failures retained in receipt. Historical full6265/93.04% at180cddda0 remains scoped to that checkpoint.))
- **Summary:** Replace universal neural-depth claims with conditional latency reasoning; correct parameter counts, state-compression inference and synergy interpretation; validate the printed NMF example.
- **Next step:** None for this delivered scope.

### DL-#4688 · Dataset Explorer Route Audit and Main Feed Ordering

- **State:** in_review
- **Owner:** codex-luna-affine4688-handoff-20260930-2335
- **PR:** #4713 merged 2026-10-01T06:04:26Z at `03ea44ea70639f7314a773b668bef0eaa02c0cd1`; standalone feed-order PR not created.
- **Issue:** #4688 (main deployment coverage and feed ordering; remains open pending successful deployment of the feed-order repair)
- **Branch:** `fix/issue-4688-main-feed-order-20261001` (feed-order repair; prior route-audit branch `fix/luna-deploy-route-4688` is historical).
- **Paths:** `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`, `reports/scientific-claim-audit.md`, `tests/test_claim_audit_inventory.py`, `tests/test_evidence_presentation.py`, `.github/workflows/deploy-website.yml`, `tests/test_generate_feed.py`, `SPEC.md`, `docs/development/HANDOFF.md`, `docs/development/DEVELOPMENT_LOG.md`.
- **Started:** 2026-09-30
- **Last verified:** 2026-10-01 (feed-order behavior remains source-bound to `50f8279cd566733982249da97b53160a1224a933`; after pinned #4748 integration, 3 workflow tests, 17 deployment-integrity tests/1 existing skip, and all 6 Critics Corner identity tests pass. Claim-audit check, SPEC, 653-title, CSS budget/architecture, Ruff/Black hooks pass. Frontend mirror `--check` exits 1 because render-generated `docs/js/` mirrors are absent; no full render was run. HISTORICAL route-audit results remain revision-specific: earlier 46 focused and 183 content-lint tests, 6,162-pass suite at `3c9572b64cf1e4dd4d3a8dbe7766de0354abb40d`, and render at `4b886599d65f9bbcec7cb9f9d41f9dfcbf674633`.)
- **Summary:** PR #4713 added the reviewed record for the already-public dataset-explorer route and source-derived regression; it merged at `03ea44e`. Separately, repair main deploy ordering while preserving render → sitemap → feed, then run the unchanged blocking source link check. HISTORICAL route-audit evidence is limited to its reviewed source/revisions; population inputs were manufactured synthetic and ZTCF/proximal-distal evidence remained model-level/educational. Finding #4695 was closed via merged PR #4728. #4694 workflow-gate work is separate.
- **Current integration:** Feed-order repair is based on `a473831731989fce80f110bcc34745affe9ad837`; the branch also integrates pinned main commit `4c1ddafa5a51c2be28361bc574618a9a146f99fa` (#4748). Accepted workflow/test diff remains commit `50f8279cd566733982249da97b53160a1224a933` (tree `efe4c26a3c16d1a3ade3f52dad3c22527fdd2a86`), byte-identical after integration. All 14 incoming paths are retained and incoming non-history blobs match the pinned commit; the three authorized history files preserve both records. HISTORICAL route-audit checkpoints and their associated tests/render do not evidence feed-order behavior.
- **Next step:** Root reviews the local integration report before deciding whether to publish the standalone feed-order PR; issue #4688 remains open pending successful main deployment. PR #4713 is already merged and is not awaiting monitoring.


### DL-#4730 · Ground-Reaction Boundaries and Matching Evidence

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4734 (verified main carrier)
- **Issue:** #4730 (epic #4009)
- **Branch:** `fix/ground-conversation-rigor-4730`
- **Paths:** `articles/proximal_distal_companion/chapters/ch16_ground_conversation.qmd`, `scripts/make_proximal_distal_companion_expanded_figures.py`, `tests/test_ground_conversation_review.py`, `reports/technical-review/ground-conversation-review.md`
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (Delivery audit against main `1b255c15a089ab7ad97e508216bbfc281f4fa482`: Ground review delivered through4734 at7eb87e3c9;4732/4735 closed unmerged. Four dedicated ground blobs match the main carrier; later main changes only 'qualified model' to 'calibrated model' in this chapter. Receipt: reports/technical-review/prior-delivery-reconciliation.json. Historical validation retained: 2026-10-01 (ground86ce488e4 source/PDF/test blobs and complete28-finding route record match consolidation0da91db1 exactly. Prior full6232/93.04% at feae3b872; latest ground55 focused/184 content passes. Protected consolidation merge pending.))
- **Summary:** Correct material contact power, internal/external wrench boundaries, ZVCF control convention and symmetric dissipation normalization; distinguish primary matching from total model contrasts and resolve post-hoc horizon counts.
- **Next step:** None for this delivered scope.

### DL-#4602 · Content Inventory and Ownership Map

- **State:** in_review
- **Owner:** claude
- **PR:** #4626
- **Issue:** #4602 (epic #4604)
- **Branch:** `claude/issue-4602`
- **Paths:** `scripts/generate_content_inventory.py`, `tests/test_content_page_inventory.py`, `data/content/inventory.json`, `data/content/inventory.csv`, `pages/content-inventory.qmd`, `pages/development-roadmap.qmd`, `.github/workflows/ci-standard.yml`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (9 new tests pass; site link gate, title-case, terminology, root-hygiene, DRY-adoption, module-size-budget, internal link, mypy/ruff/black, and claim-audit evidence checks pass; `python3 -m scripts.generate_content_inventory --check` passes at a stable 197-page fixed point)
- **Summary:** Generates a deterministic inventory of every rendered page (word count, status from the `status-banner` component, last-reviewed date from front-matter `date:`, canonical pointer, inbound link count, outbound broken links) as JSON/CSV artifacts plus a dashboard page; flags pages under 300 words without a Planned status as consolidation/retirement candidates; verified via a new CI step.
- **Next step:** Open the draft PR for frontier review; no further implementation planned unless review requests changes.

### DL-#4538 · Reader Run Environment (Binder, Devcontainer, Downloads)

- **State:** in_review
- **Owner:** claude
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4682 (draft)
- **Issue:** #4538 (WEB-06.8; epic #4543)
- **Branch:** `claude/issue-4538`
- **Paths:** `environment.yml`, `articles/_metadata.yml`, `_includes/notebook-binder-launch.qmd`, `books/tangent-space-methods.qmd`, `books/control-is-motion.qmd`, `books/biomechanics-biology-to-systems.qmd`, `books/human-motor-control.qmd`, `notebooks/geometry_of_motion/README.md`, `scripts/check_root_hygiene.py`, `tests/test_reader_run_environment.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: 7/7 `tests/test_reader_run_environment.py` pass; `check_root_hygiene.py`, `check_quarto_render_coverage.py`, `check_quarto_xrefs.py`, `check_single_title.py`, `check_title_case.py`, `check_terminology.py`, `check_dry_adoption.py`, `check_contract_coverage.py` all pass; ruff/black clean on changed Python files)
- **Summary:** Adds a root `environment.yml` so mybinder.org can build a JupyterLab environment that opens the notebook scaffolds, installing from `requirements.txt` (not `requirements-docker.lock`, which pins a Windows-only `pywinpty` wheel that fails on Binder's Linux image and is stale relative to `requirements.txt`), a shared `_includes/notebook-binder-launch.qmd` Binder-launch link included from each of the four book pages' "Notebook Workflow" section and from the notebooks README, and `code-tools: true` scoped to `articles/_metadata.yml` (the one content directory that shows Python reference implementations) so those pages get Quarto's source-download menu without flipping the site-wide default. The devcontainer half of the issue (`.devcontainer/devcontainer.json` and the CI job to build it) is blocked — see HANDOFF.md. The Binder build itself is unverified (repo2docker was never run).
- **Next step:** A session with permission to write under a path named `.devcontainer` must add the file (content given in the PR's Blocked section) and a CI build step; then this entry's state can move to `shipped`.

### DL-#4503 · URL Stability and Redirect Policy

- **State:** in_review
- **Owner:** claude
- **PR:** #4503 (draft)
- **Issue:** #4503 (WEB-02.9; epic #4505 / E2)
- **Branch:** `claude/issue-4503`
- **Paths:** `src/tools/check_redirects.py`, `tests/test_check_redirects.py`, `tests/test_deployment_integrity.py`, `config/redirects.yml`, `.github/workflows/deploy-website.yml`, `CONTRIBUTING.md`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (13/13 new pytest cases in `test_check_redirects.py` pass; `test_deployment_integrity.py` 16 passed/1 skipped; ruff, black --line-length 100, and mypy clean on the new module.)
- **Summary:** Compares the previously deployed site's public-site manifest against the new build's manifest and the `config/redirects.yml` ledger, failing the deploy workflow if a previously published route disappeared without a documented and actually-rendered redirect; ledger usage documented in CONTRIBUTING.md alongside Quarto `aliases:`.
- **Next step:** Owner/frontier review of the draft PR; no further implementation planned pending review feedback.

## Shipped (Last 90 Days)

Entries stay here for 90 days after merge, then move to the archive.

### DL-#4725 · Annotated Reference Library

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4729 (regular)
- **Issue:** #4725 (epic #4009)
- **Branch:** `fix/reference-library-rigor-4725`
- **Paths:** `articles/Launch_Monitor_Technology_Review/sections/appendix-a-references.tex`, `articles/Launch_Monitor_Technology_Review/sections/03-impact-physics.tex`, `articles/Launch_Monitor_Technology_Review/references.bib`, `articles/Launch_Monitor_Technology_Review/main.pdf`, `reports/technical-review/reference-library-review.md`, `tests/test_reference_library_review.py`
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (21 focused passes; 6178 full-suite passes/29 skips; 78.37% combined coverage and 92.95% src-only from same data; 183 post-full content passes/four skips; 78-page PDF and 20 final pages verified; Ruff/Black/titles/content gates pass; broad mypy has nine errors in unchanged production sources)
- **Summary:** Distinguish median-centered agreement, absolute error, data return, historical vendor specifications and patent disclosures; correct study attribution and inverse sensitivity without certifying the full chapter.
- **Next step:** Merged protected remote main fd508f04cd48b80f8f248432cea4a033b9188a13 at 2026-10-01 03:37:56 UTC; fetched and verified. Final integrated local suite 6191 passed/29 skipped, 92.95% src coverage; subsequent content 183 passed/four skipped. Receipt carried in #4730 after merge; lease/presence released 03:44 UTC. Broader goal active.

### DL-#4724 · Plane-to-Space Mechanical and Evidence Boundaries

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4726 (regular)
- **Issue:** #4724 (epic #4009)
- **Branch:** `fix/plane-space-rigor-4724`
- **Paths:** `articles/proximal_distal_companion/chapters/ch20_plane_to_space.qmd`, `tests/test_plane_space_review.py`, `reports/technical-review/plane-space-review.md`
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (39 focused/legacy/hygiene checks; four final browser cases, zero serious/critical axe findings; three equations and final PDF pages inspected)
- **Summary:** Correct observer/reference power, contact constraints, rank/feasibility, archived populations and engine independence; derive and expose the shared vector-damper angular-momentum limitation. Preserve prior review scopes and immutable provider source; follow-up UpstreamDrift #11195.
- **Next step:** Merged remote main 644bfd5bebb197ee03deb16877f189a0d772c403 at 2026-10-01 03:23:14 UTC, all protected checks green (36807137602). Fetched/ancestor verified; lease/presence released 03:24 UTC. Broader goal remains active.

### DL-#4720 · Heavy-Hit Coupling and Acoustic Evidence

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4723 (regular)
- **Issue:** #4720 (epic #4009)
- **Branch:** `fix/heavy-hit-consistency-4720`
- **Paths:** `articles/technology-heavy-hit-impact-coupling.qmd`, `articles/_includes/impact-acoustics.qmd`, `articles/_includes/impact-research-program.qmd`, `tests/test_heavy_hit_boundary_review.py`, `reports/technical-review/heavy-hit-review.md`
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (6086 full-suite passes, 29 skips, 92.95% coverage; 38 focused audit/numerical/hygiene passes; 138 rendered expressions/23 displays visually checked at 390/1440 px; four browser cases and one axe scan, zero serious/critical findings; twelve content gates and Ruff/Black/mypy pass)
- **Summary:** Reconcile force transmission, fixed/moving grip ports and energy accounting; retain source-specific acoustic and research limits. Preserve previous reviews and parked provider synthesis.
- **Next step:** Science/evidence bound at 3f9c6882b/c1fc3a09f; merged radar main bd1255f15 integrated. Post-full content: 180 passes/four skips. Regular PR #4723 merged at 2a7c094070c5ebd7d16c95c332d5526931cc5ba0 with all protected checks green (CI 36801091325). Remote-main ancestry verified; lease/presence released. Deployment separately blocked by #4688 / #4713.

### DL-#4717 · Radar Screw-Kinematics Appendix Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4721 (regular)
- **Issue:** #4717 (epic #4009)
- **Branch:** `fix/radar-screw-rigor-4717`
- **Paths:** `articles/Launch_Monitor_Technology_Review/sections/appendix-e-screw-kinematics.tex`, `articles/Launch_Monitor_Technology_Review/references.bib`, `articles/Launch_Monitor_Technology_Review/main.pdf`, `tests/test_radar_screw_appendix_review.py`, `reports/technical-review/radar-screw-review.md`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (40 focused and 46 post-cleanup cases pass; 6,057 full-suite passes/29 skips; separate coverage run passed at 92.95%; 180 content passes/four skips; 76-page book with fifteen final pages visually checked; Ruff/Black/mypy and content gates pass)
- **Summary:** Distinguish a rigid-motion representation from observable information and model-based inference; correct frame, covariance, waveform, impact and output-definition claims. Preserve the rest of the book's review scope and the historical outline's provenance.
- **Next step:** Merged remote main `bd1255f153926c7e653148b8c4db972a08ba7be9` at 2026-10-01 01:11:24 UTC, all protected checks green (36799282870). Full combined-main suite 6078 passes, 92.95% coverage; subsequent content 180 passes/four skips. Lease/presence released 01:12 UTC.

### DL-#4714 · Impact Optimality and Model Limits

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4718 (regular)
- **Issue:** #4714 (epic #4009; historical corpus #4021)
- **Branch:** `fix/impact-optimality-rigor-4714`
- **Paths:** `articles/impact-optimality-and-model-limits.qmd`, `articles/proximal-distal-model-workbench.qmd`, `resources/articles.qmd`, `tests/test_impact_optimality_review.py`, `reports/technical-review/impact-optimality-review.md`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (21 impact checks; 46 post-binding audit/numerical/hygiene checks; 179 content passes; full Windows 6036 passes and three audit/snapshot failures subsequently resolved; 92.88% coverage; Ruff/Black/mypy and 12 content gates; final 12 browser cases and 74 math expressions)
- **Summary:** Bound the instantaneous theorem, inertia reduction and historical solver evidence; correct primary-study and human-objective inference; reconcile two linked public summaries without renewing their other review scope.
- **Next step:** Complete. Regular PR #4718 merged to remote main 24cdba4d49abec347bbe56fd51cc7d5ed00ab6a5 at 2026-10-01 00:23:35 UTC; every protected check passed (CI 36792360532). Lease/presence released. Provider follow-up Tools #5393 and separately owned deployment gap #4688 remain open.


### DL-#4712 · Two-Hand Wrench Chapter Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4712 (regular)
- **Issue:** #4710 (corpus #4021; epic #4009)
- **Branch:** `fix/two-hand-wrench-rigor-4710`
- **Paths:** `articles/proximal_distal_companion/chapters/ch12_two_hands_one_wrench.qmd`, `references/proximal-distal-energy.bib`, `models/bilateral-hand-wrench-validation.qmd`, `tests/test_two_hand_wrench_review.py`, `reports/technical-review/two-hand-wrench-review.md`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (combined-main suite: 6,034 passed, 29 skipped, 92.88% coverage; final content: 180 passed/four skipped; 39 protocol/history/audit checks; 209-page PDF and 20 browser cases verified)
- **Summary:** Reconcile force/moment origins, map degeneracies, rigid/flexible power and archived sensor/contact evidence; distinguish synthetic model support from human inference. Citation-only updates in three neighboring chapters and the protocol do not renew their scientific reviews.
- **Next step:** Merged to remote main be263f9cd946a6aa8b4a97b086af9eab399c3ac6 at 23:32:17 UTC; all protected CI checks passed (36786787125). Lease and presence released. Provider citation follow-up #4711 remains open.

### DL-#4715 · Quarto Script-Action Link Classification

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4716 (regular PR)
- **Issue:** #4715 (related deployment health #4688)
- **Branch:** `fix/quarto-script-links-4715`
- **Paths:** `src/tools/check_site_health.py`, `tests/test_site_health_script_actions.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (ten RED regressions; 98 focused checks GREEN; full Windows suite 6,028 passed, 29 skipped, 92.95% coverage; 179 content checks passed, four skipped; Ruff/Black/mypy/SPEC/evidence checks pass)
- **Summary:** Ignore JavaScript action URLs during filesystem target resolution so Quarto code-menu controls no longer block deployment; retain failures for missing article links.
- **Next step:** Merged #4716 to remote main 5e1a11059 at 22:27:52 UTC; lease released. Preserve #4688's separate audit work and verify a later main deployment.

### DL-#4706 · Induced Acceleration Biomechanics Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4709 (regular PR)
- **Issue:** #4706 (corpus #4021; epic #4009)
- **Branch:** `fix/induced-acceleration-rigor-20260930`
- **Paths:** `articles/The_Geometry_of_Motion/Volume_I/chapters/ch03b_induced_acceleration_biomechanics.tex`, `articles/The_Geometry_of_Motion/quarto/ch03b_induced_acceleration_biomechanics.qmd`, `articles/The_Geometry_of_Motion/Volume_I/main.pdf`, `tests/test_iaa_biomechanics_review.py`, `reports/technical-review/iaa-biomechanics-review.md`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (final source d7cf1af8; final render evidence 2f32c8d4; integrated main 59c0cc2d: 28 numerical/source checks, fourteen attribution contracts, full Ruff/Black and configured mypy; 149-page book and four browser combinations; Linux CI 41e075ef: 5962 passed, 92.83% coverage; 179 content checks; eight book builds; Windows 6005 passed, two snapshot-location failures resolved and six hygiene checks pass; quotation gate passes; CI requires named gravity constant in one test, corrected without changing assertions)
- **Summary:** Reconcile complete print/web Chapter 3b mechanics and primary-study interpretation, with explicit constrained and state-space accounting; preserve other chapter review scopes.
- **Next step:** Complete. PR #4709 merged at 984552e17 with CI Standard 36773428069 green; issue lease and presence released. Corpus continues in regular PR #4712.

## Archive

Older entries live in `DEVELOPMENT_LOG_ARCHIVE_<year>.md`.

### DL-#4606 · "What's New" Feed RSS Validation

- **State:** in_review
- **Owner:** claude
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4675 (draft)
- **Issue:** #4606 (WEB-14.4; epic #4610 / E14)
- **Branch:** `claude/issue-4606`
- **Paths:** `scripts/generate_feed.py`, `tests/test_generate_feed.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: `pytest tests/test_generate_feed.py` 26/26 pass; ruff and black --line-length 100 clean; mypy clean; live generator run against real repo content produces 30 items with zero validation errors)
- **Summary:** Adds `validate_feed_xml()`, an RSS 2.0 structural validator (well-formed XML, required channel/item elements, absolute item links, RFC-822 pubDates, unique guids) wired into `generate_feed.py`'s `main()` so an invalid feed fails the build instead of publishing, satisfying acceptance criterion 1 ("The RSS feed validates"). Criterion 2 ("Items link to revision history") is blocked on the still-open prerequisite #4545 (WEB-07.3), which introduces the `changes:` front-matter field and per-page "Revision history" section this criterion depends on; see HANDOFF.md Blocked section.
- **Next step:** Land #4545 (WEB-07.3), then point feed item links at its revision-history anchor and re-check criterion 2.
### DL-#4592 · Consolidate the Manifesto

- **State:** in_review
- **Owner:** claude
- **PR:** not created yet at this commit; opening a draft PR immediately after
- **Issue:** #4592 (WEB-12.6; epic #4594; `tier:cli`, `complexity:routine`)
- **Branch:** `claude/issue-4592`
- **Paths:** `pages/drifter-manifesto.qmd`, `articles/drifter-manifesto.qmd`, `config/categories.yml`, `tests/test_editorial_and_consistency.py`, `data/trust/site_trust_surface_audit.json`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`, `reports/site-trust-surface-audit.md`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (focused suites pass: editorial/consistency, trust-surface/claim-audit, page-style, manifesto rigor, formatting lints, site link gate; full suite passes with no failures; ruff/black clean; `regenerate_claim_audit_evidence --check` passes.)
- **Summary:** Adds `opinion` to the controlled category vocabulary and recategorises both Manifesto pages from `critique`; declares `pages/drifter-manifesto.qmd` the canonical entry point and `articles/drifter-manifesto.qmd` an explicitly non-canonical, Opinion-labelled companion, without deleting either page's content (full retirement is WEB-02.4's own `tier:strong` ADR work).
- **Next step:** Open the draft PR and await frontier review; no further development expected unless the reviewer requests scope changes.
### DL-#4541 · Fixture and Dataset Explorer

- **State:** in_review
- **Owner:** claude
- **PR:** not created yet (draft PR to be opened this session)
- **Issue:** #4541 (epic #4543, E6 — Interactive Models and Reproducibility)
- **Branch:** `claude/issue-4541`
- **Paths:** `models/dataset-explorer.qmd`, `js/dataset-explorer.js`, `js/dataset-explorer-ui.js`, `css/dataset-explorer.css`, `scripts/generate_dataset_explorer_manifest.py`, `data/dataset_explorer_manifest.json`, `tests/dataset-explorer.test.js`, `tests/dataset-explorer-ui.test.js`, `tests/test_generate_dataset_explorer_manifest.py`, `scripts/sync_frontend_assets.py`, `_quarto.yml`, `data/trust/claim_audit_inventory.json`, `SPEC.md`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: `npx jest` 28 suites/455 passed/19 skipped; targeted `pytest` across `test_generate_dataset_explorer_manifest.py`, `test_claim_audit_inventory.py`, `test_claim_audit_output_boundary.py`, `test_sync_frontend_assets.py`, `test_check_single_title.py`, `test_site_trust_surface_audit.py` — 84/84 passed; `ruff check .` and `black --check --line-length 100 .` clean repo-wide; `stylelint css/dataset-explorer.css` clean; site link gate passes; `check_spec_changelog.py` passes)
- **Summary:** New browser page listing every `data/ztcf/`, `data/population_generalization/`, and `data/proximal_distal_energy_transfer/` fixture from a generated manifest. A hand-written JSON Schema validator checks each fixture against its published schema client-side. Each fixture gets an accessible data table and a download button whose SHA-256 is computed in-browser. Linked from `_quarto.yml`'s navbar (Build → Datasets).
- **Next step:** Push the branch, open the draft PR, and let CI's `quarto render`/Playwright lane confirm the page renders and passes axe-core.

### DL-#4550 · Print and PDF Editions for Books and Core Series

- **State:** in_review
- **Owner:** claude
- **PR:** draft (see HANDOFF.md for link)
- **Issue:** #4550 (WEB-07.9; epic #4552)
- **Branch:** `claude/issue-4550`
- **Paths:** `css/print.css`, `styles.css`, `js/pdf.js`, `js/main.js`, `tests/test_print_stylesheet_consolidation.py`, `tests/pdf.test.js`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: `pytest tests/test_print_stylesheet_consolidation.py` 4/4 pass; `npx jest` 27 suites, 437 passed/19 skipped; `ruff check .` and `black --check --line-length 100 .` clean)
- **Summary:** Consolidates the two competing `@media print` blocks into `css/print.css` as the single print stylesheet, drops the A4-only forced `@page` size (now `auto`) so both Letter and A4 print via the printer/OS choice, and adds a `beforeprint` handler forcing MathJax to typeset lazy-loaded off-screen math before any print (native Ctrl+P or the export-to-PDF button). The "PDFs built in CI and linked from the header card" criterion is deliberately not implemented this session — see HANDOFF.md Blocked section.
- **Next step:** Owner/frontier decision on the deferred PDF-header-card-link scope (see HANDOFF.md Blocked), then implement or split into a follow-up issue.
### DL-#4495 · Make the 404 Page and Empty States Useful

- **State:** in_review
- **Owner:** claude
- **PR:** to be opened as a draft by this session
- **Issue:** #4495 (WEB-01.10; epic #4496 / E1)
- **Branch:** `claude/issue-4495`
- **Paths:** `404.qmd`, `tests/test_404_page.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: `pytest tests/test_404_page.py` 3 passed; `ruff check .` and `black --check --line-length 100 .` clean repo-wide)
- **Summary:** Unifies the 404 page's contact address with About/Contact (`dieterolson@AffineDrift.com`, not the personal Gmail address it previously pointed to). The page's search-box mention and its five suggested-destination links were already present. The other half of the acceptance criteria — explicit "Start Here" and "Library" links — is blocked: neither target exists yet (`pages/start-here.qmd` is #4486, tier:strong, still open; the "Library" navbar grouping is part of the unmerged WEB-02.1 navbar restructure, also tier:strong). See the PR's Blocked section.
- **Next step:** Once #4486 (Start Here page) and WEB-02.1 (Library navbar grouping) land, add the two links to `404.qmd` and close out the remainder of this issue's acceptance criteria.
### DL-#4565 · Math Accessibility Verification

- **State:** in_review
- **Owner:** claude
- **PR:** see PR opened from `claude/issue-4565` against `main` (draft)
- **Issue:** #4565 (WEB-09.5; epic #4569 / E9)
- **Branch:** `claude/issue-4565`
- **Paths:** `tests/mathjax-loader.test.js`, `tests/e2e/accessibility.spec.js`, `docs/development/math-accessibility-verification-4565.md`, `.github/workflows/ci-standard.yml`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: `npx jest` 26 suites passed, 432 passed/19 skipped, 0 failed; `npx playwright test tests/e2e/accessibility.spec.js --list` registers the new test across all 5 browser projects; YAML-validated `ci-standard.yml`; full Playwright run deferred to CI's `e2e-tests` job since Quarto is not installed in this worktree)
- **Summary:** Verifies the `connect-src 'self'` CSP does not block MathJax speech-rule locale fetches — finding is that `_includes/mathjax-loader.html` never loads the `[a11y]/explorer`/SRE component, so no such fetch happens today — and adds regression tests plus a Playwright check across three math-heavy pages confirming assistive MathML attaches with no CSP violations or failed requests. CI review of the first PR revision found a real, unrelated CSP violation (Pandoc's legacy cdnjs polyfill tag surviving into the pre-prune E2E render); fixed by reordering `ci-standard.yml` so pruning runs before Playwright, without widening the CSP. The issue's first acceptance criterion (an actual NVDA/VoiceOver run with recorded results) is a human-in-the-loop step this agent cannot perform; see `docs/development/math-accessibility-verification-4565.md` for the manual protocol.
- **Next step:** A human tester runs the manual NVDA/VoiceOver protocol in the findings doc and records results on #4565.
### DL-#4599 · Consolidate Inline "Recent" History Scripts

- **State:** in_review
- **Owner:** claude
- **PR:** #4625
- **Issue:** #4599 (`WEB-13.5`; epic #4604)
- **Branch:** `claude/issue-4599`
- **Paths:** `js/history.js`, `models/models-drake.qmd`, `models/models-mujoco.qmd`, `models/models-myosim.qmd`, `models/models-opensim.qmd`, `models/models-pendulum.qmd`, `models/models-pinocchio.qmd`, `models/models-simulink.qmd`, `resources/resources-books.qmd`, `resources/resources-datasets.qmd`, `resources/resources-notebooklm.qmd`, `resources/resources-papers.qmd`, `resources/resources-researchers.qmd`, `resources/resources-software.qmd`, `resources/resources-videos.qmd`, `resources/resources-websites.qmd`, `tests/history.test.js`, `tests/home.test.js`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (`npx jest`: 27 suites, 445 passed, 19 pre-existing skips; `ruff check .` clean; `black --check --line-length 100 .` clean.)
- **Summary:** Replaces the 15 duplicated inline localStorage "Recent X" widgets with a shared `initCategoryHistory()` in `js/history.js` for the 7 `models-*` pages (which genuinely track visits across a shared page set) and removes the widget entirely on the 8 `resources-*` pages (each only ever recorded its own page, so the feature showed nothing useful); adds first-ever Jest coverage for `history.js` and `home.js`.
- **Next step:** Awaiting reviewer merge of #4625.
### DL-#4542 · Programming-Companion Metadata and Repository Links

- **State:** in_review
- **Owner:** claude
- **PR:** not yet created
- **Issue:** #4542 (epic #4543)
- **Branch:** `claude/issue-4542`
- **Paths:** `src/affine_control/programming_companion/catalog_generator.py`, `models/programming/programs.qmd`, `models/programming/engines.qmd`, `repositories/*.qmd`, `tests/test_programming_companion_catalog_generator.py`, `tests/test_repository_links_pinned.py`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (targeted pytest subsets and full `pytest` run pass; `ruff check` and `black --check` clean on touched files; `scripts.regenerate_claim_audit_evidence` re-run clean).
- **Summary:** The catalog generator read a nonexistent `title` key for programs and engines (the manifest field is `name`), so every program and engine row rendered its ID as its title; fixed to read `name` (and `engine_id` for the programs' Engine column), dropped the Engines page's fabricated Maturity column (no such field exists in the manifest schema), and regenerated the committed pages. Labelled the 16 unpinned `repositories/*.qmd` UpstreamDrift root links as "navigation only" per the acceptance criteria, since they point at the live repository rather than a reviewed commit.
- **Next step:** Open the draft PR and record its number here; awaiting frontier-agent review.

### DL-#4551 · Parameters Page and Notation Quick-Reference Card

- **State:** in_review
- **Owner:** claude
- **PR:** #4627 (draft)
- **Issue:** #4551 (epic #4552)
- **Branch:** `claude/issue-4551`
- **Paths:** `pages/parameters.qmd`, `pages/notation-quick-reference.qmd`, `pages/notation.qmd`, `NOTATION.md`, `PARAMETERS.md`, `sitemap.xml`, `tests/test_notation_and_parameters_pages.py`, `data/trust/claim_audit_inventory.json`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-30 (merged origin/main; added reviewed claim-audit records for `/pages/parameters.html` and `/pages/notation-quick-reference.html`.)
- **Summary:** Renders `PARAMETERS.md` via a new `pages/parameters.qmd`, adds a condensed one-page printable `pages/notation-quick-reference.qmd`, and removes the duplicate heading/manual table of contents that `pages/notation.qmd` inherited from `NOTATION.md`. The acceptance criterion "every core page links notation from its header card" is not implemented: the header-card component (#4507 / WEB-03.2) does not exist yet, so there is nothing to link from; see the PR's Blocked section.
- **Next step:** Owner/reviewer decides whether to accept the interim scope (3 of 4 criteria) or hold for #4507, then mark shipped once the PR merges.

### DL-#4607 · Contributor and Reviewer Guide on the Site

- **State:** in_review
- **Owner:** claude
- **PR:** #4636 (draft)
- **Issue:** #4607 (part of #4610)
- **Branch:** `claude/issue-4607`
- **Paths:** `pages/contributor-guide.qmd`, `pages/collaborate.qmd`, `tests/test_contributor_reviewer_guide.py`, `tests/test_page_style_discipline.py`, `data/trust/claim_audit_inventory.json`, `scripts/claim_audit_ids.py`, `tests/test_claim_audit_inventory.py`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-30 (merged origin/main; added reviewed claim-audit record for `/pages/contributor-guide.html`; `pytest tests/test_contributor_reviewer_guide.py tests/test_page_style_discipline.py tests/test_claim_audit_inventory.py tests/test_check_quarto_render_coverage.py` pass; `ruff check` and `black --check` clean on changed files.)
- **Summary:** Adds a reader-facing guide routing corrections, claim critiques, dataset contributions, and chapter reviews to their GitHub issue templates, linked from Collaborate. The "linked from every WEB-03.4 block" acceptance criterion is deferred because WEB-03.4 does not exist yet.
- **Next step:** Owner/frontier review of the draft PR.

### DL-#4492 · Short On-Ramp Learning Paths (5 Minutes, 30 Minutes, 3 Hours)

- **State:** in_review
- **Owner:** claude
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4677 (draft)
- **Issue:** #4492 (WEB-01.7; epic #4496)
- **Branch:** `claude/issue-4492`
- **Paths:** `resources/on-ramp-paths.qmd`, `resources/learning-paths.qmd`, `tests/test_on_ramp_paths.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-29 (fix round for PR #4677 review: `pytest tests/test_on_ramp_paths.py` 10 passed; `pytest tests/test_site_link_gate.py tests/test_how_to_read.py tests/test_persona_start_paths.py tests/test_check_links.py tests/test_check_site_health.py` 98 passed; site gate passed; `ruff check tests/test_on_ramp_paths.py` and `black --check --line-length 100 tests/test_on_ramp_paths.py` clean)
- **Summary:** Adds `resources/on-ramp-paths.qmd`, a new page with 5-minute, 30-minute, and 3-hour reading sequences for each of the 8 personas from `config/personas.yml`, built entirely from existing pages (no new prose content elsewhere), each ending in a self-check question with its answer grounded in the linked page's own body text; linked from `resources/learning-paths.qmd` so it isn't orphaned. Fix round corrected a notation error (lowercase `g(x)u`), a ZVCF/trajectory wording error, a fabricated "double-pendulum benchmark" claim about Theory Part 4, a mischaracterization of the research-review stub pages as finished reviews, an inconsistent Theory Part 1 time estimate, a subtitle hour-range mismatch, and rewrote all 24 self-checks from recall trivia to reflective questions.
- **Next step:** Push the branch with this fix round and await re-review.
### DL-#4547 · Deduplicate and Reconcile Bibliography Databases

- **State:** in_review
- **Owner:** claude
- **PR:** #4676 (draft)
- **Issue:** #4547 (WEB-07.5)
- **Branch:** `claude/issue-4547`
- **Paths:** `scripts/check_bibliography_cross_file.py`, `tests/test_check_bibliography_cross_file.py`, `articles/The_Physics_of_Golf/golf_physics.bib` (metadata fix only).
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (SELF: reworked after review blocked the original mechanical-merge draft. `python3 scripts/check_bibliography_cross_file.py` reports 163 keys shared across files, 0 disagreeing, 0 CI-flagged duplicate DOIs (82 raw shared-DOI groups exist pre-exemption, mostly legitimate per-book copies — see PR #4676 for the list); `pytest tests/test_check_bibliography_cross_file.py` 18/18; `python3 -m scripts.check_citation_resolution`, `python3 -m scripts.check_qmd_citation_keys`, and `scripts/check_latex_structure.py` (pre-existing, already CI-wired citation-resolution checks) all pass clean against the reverted tree; `ruff check .` and `black --check --line-length 100 .` clean.)
- **Summary:** Reworked after review blocked the original mechanical dedupe: that merge broke the locked `proximal_distal_energy_transfer` article, touched an owner-sign-off-gated book audit ledger, deleted citation keys still in use, and silently renamed a key. All of that is reverted to `origin/main` byte-for-byte. What ships instead: `proximal_distal_energy_transfer/references.bib` added to `STANDALONE_LINKED` (it is `index.qmd`'s sole `bibliography:` override) and `clark2013whatever` fixed to the `@article`/*Behavioral and Brain Sciences*/Cambridge University Press record it actually is everywhere it appears. No new citation-resolution test was added: `scripts/check_citation_resolution.py`, `scripts/check_qmd_citation_keys.py`, and `scripts/check_latex_structure.py` already do exactly that (CI-gated, all currently passing), so writing a parallel implementation would have duplicated working infrastructure. The 82 raw duplicate-DOI groups the mechanical merge would have addressed are left in place; most are legitimate copies across `STANDALONE_LINKED` files, and the CI check does not flag any of them as violations.
- **Next step:** Owner/frontier review of the reworked draft PR #4676; mark ready and merge once approved.
### DL-#4564 · Cross-Browser Coverage (Nightly Firefox/WebKit)

- **State:** in_review
- **Owner:** claude
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4685 (draft)
- **Issue:** #4564 (WEB-09.4; epic #4569 / E9)
- **Branch:** `claude/issue-4564`
- **Paths:** `.github/workflows/cross-browser-nightly.yml`, `scripts/report_e2e_browser_failures.py`, `tests/test_report_e2e_browser_failures.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF, review feedback round 1: 29/29 tests in test_report_e2e_browser_failures.py pass via `python -m pytest -q -o addopts=`; ruff and black --line-length 100 clean on the changed files; no-new-labels, missing-report-handling, and issue-cap behaviors each landed test-first)
- **Summary:** Adds a nightly workflow that runs `tests/e2e/smoke.spec.js` (the existing representative public-route + behavioral-invariant suite) against Firefox and WebKit — the two `playwright.config.js` projects `ci-standard.yml`'s PR-gated `e2e-tests` job never exercises — and files deduplicated-by-title GitHub issues via `scripts/report_e2e_browser_failures.py`: one per distinct (browser, test title) failure, using only the repo's existing `ci`/`automation` labels, rolling more than 5 new failures into a single dated summary issue, and treating a missing/empty/unparseable report as a failure of its own instead of crashing or vanishing.
- **Next step:** Owner/frontier review of the draft PR; the schedule cannot be exercised end-to-end until it first fires on `main`, so verify the first nightly run once merged.
### DL-#4576 · Privacy Policy Page

- **State:** in_review
- **Owner:** claude
- **PR:** not created yet
- **Issue:** #4576 (epic #4579)
- **Branch:** `claude/issue-4576`
- **Paths:** `pages/privacy-policy.qmd`, `_quarto.yml`, `tests/test_privacy_policy_page.py`, `tests/test_navbar_ia.py`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (`pytest tests/test_privacy_policy_page.py tests/test_navbar_ia.py -v -m content_lint`: 6 passed; `pytest tests/test_page_style_discipline.py tests/test_site_trust_surface_audit.py tests/test_editorial_and_consistency.py -v`: 144 passed; `ruff check` and `black --check --line-length 100` on changed files: clean.)
- **Summary:** Adds a Privacy Policy page covering local storage (`metrics.js`), the service worker, third-party embeds (YouTube, Google Fonts, jsDelivr), and analytics per Board decision D6; linked from the site footer.
- **Next step:** Open the draft PR and update this entry's PR field with the resulting number.

### DL-#4582 · Enforce G(x) Notation and Add a Notation Lint

- **State:** in_review
- **Owner:** claude
- **PR:** not created yet (draft opened in the same turn this entry lands)
- **Issue:** #4582 (native child of epic #4586, E11 — Mathematical Typesetting and Notation)
- **Branch:** `claude/issue-4582`
- **Paths:** `index.qmd`, `models/models-drake.qmd`, `articles/motion-control/chapter8.tex`, `articles/motion-control/Control_Is_Motion_Complete.tex`, `articles/The_Geometry_of_Motion/quarto/ch03_superposition.qmd`, `articles/The_Geometry_of_Motion/Volume_I/chapters/ch03_superposition.tex`, `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`, `articles/The_Geometry_of_Motion/Volume_II/chapters/ch08_phase_variable_control.tex`, `critiques/*.md` (12 files), `scripts/check_notation.py`, `tests/test_check_notation.py`, `config/notation-baseline.json`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (`black --check`, `ruff check` on the new script/test pass; `pytest tests/test_check_notation.py -m content_lint` 17 passed, including a real-corpus scan of `.tex`/`.qmd`/`.md` sources; `python3 scripts/check_notation.py --baseline config/notation-baseline.json` exits 0.)
- **Summary:** Replaces lowercase `g(x)` with uppercase `G(x)` for the control-affine input map everywhere it carries that meaning (home page, four textbook chapters and their LaTeX mirrors, 12 critique files), per `NOTATION.md:342-346`. Adds a baseline-gated pytest lint (`scripts/check_notation.py` + `tests/test_check_notation.py`) so a reintroduced lowercase `g(x)` fails CI; the two `ch05_optimal_control` files keep their unrelated inequality-constraint `g(x)` via an explicit baseline allowlist rather than a misleading rewrite.
- **Next step:** Open the draft PR for #4582 and flip this entry to `shipped` once it merges.

### DL-#4546 · ScholarlyArticle and Book JSON-LD

- **State:** in_review
- **Owner:** claude
- **Issue:** #4546 (epic #4552)
- **PR:** [#4618](https://github.com/D-sorganization/AffineDrift/pull/4618) (draft)
- **Branch:** `claude/issue-4546`
- **Paths:** `scripts/filters/schema-jsonld.lua`, `tests/test_schema_jsonld.py`, `_quarto.yml`, `_includes/article-schema.html` (deleted), `articles/affine-nature-golf-swing.qmd`, `articles/appendix-applications.qmd`, `books/control-is-motion.qmd`, `resources/resources-datasets.qmd`, `resources/resources-software.qmd`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (`python3 -m pytest tests/test_schema_jsonld.py tests/test_companion_hierarchy.py -v` — 10 passed; `python3 -m ruff check .` and `python3 -m black --check --line-length 100 .` clean; manual `quarto render` of all five tagged sample pages confirmed valid per-type JSON-LD)
- **Summary:** Replaced the dead, broken `_includes/article-schema.html` (unreferenced; `{{< meta >}}` does not expand inside raw HTML) with a Lua filter registered project-wide in `_quarto.yml` that emits Schema.org JSON-LD for any page declaring `schema-type: ScholarlyArticle|Book|Chapter|Dataset|SoftwareSourceCode`; pages without that field are untouched. Tagged one real sample page per type.
- **Next step:** None outstanding for this scope; a frontier agent reviews the draft PR before merge.

### DL-#4608 · Website & UX Issue Template

- **State:** in_review
- **Owner:** claude
- **PR:** not created (pending)
- **Issue:** #4608 (epic #4610)
- **Branch:** `claude/issue-4608`
- **Paths:** `.github/ISSUE_TEMPLATE/website-ux-problem.md`, `tests/test_website_ux_issue_template.py`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (`python3 -m pytest tests/test_website_ux_issue_template.py -v`: 3 passed; `ruff check` and `black --check --line-length 100` clean on changed files)
- **Summary:** Adds a GitHub issue template for website/UX problems capturing page URL, viewport, theme, browser, and expected versus actual behaviour, matching the style of the existing content/critique/textbook templates.
- **Next step:** Open the draft PR and hand off for frontier review.

### DL-#4583 · Standardise the DCR Name

- **State:** in_review
- **Owner:** claude
- **Issue:** `#4583`
- **PR:** not created yet
- **Branch:** `claude/issue-4583`
- **Paths:** `articles/drift-control-ratio.qmd` (renamed from `controllability-drift-ratio.qmd`), `scripts/check_terminology.py`, `tests/test_check_terminology.py`, `data/trust/claim_audit_inventory.json`, `data/trust/claim_critique_ledger.json`, `data/trust/claim_registry.json`, `data/trust/site_trust_surface_audit.json`, `NOTATION.md`, plus ~28 other files referencing the old slug or expansion (critiques, articles, config, tests, generated trust panels/reports).
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (targeted suite: `test_dcr_article_rigor.py`, `test_dcr_reachability_contract.py`, `test_dcr_event_sensitivity_protocol.py`, `test_editorial_and_consistency.py`, `test_publication_markup_contract.py`, `test_scientific_trust_metadata.py`, `test_research_protocol_readiness.py`, `test_check_single_title.py`, `test_formatting_lints.py`, `test_check_terminology.py`, `test_claim_audit_inventory.py` — 149 passed. `ruff check .` and `black --check --line-length 100 .` clean. `regenerate_claim_audit_evidence --check`, `generate_claim_critique_ledger --check`, `generate_trust_panels --check` all current. `check_spec_changelog` passes.)
- **Summary:** Standardises the three competing DCR expansions ("drift-to-control ratio", "controllability-drift ratio") to the canonical "Drift-Control Ratio" across ~34 files; renames the article slug from `controllability-drift-ratio` to `drift-control-ratio` with a `controllability-drift-ratio.html` redirect alias; bans both wrong expansions in `scripts/check_terminology.py`; updates the source-of-truth trust/audit JSON registries and regenerates all derived artifacts (critique annotations, trust panels, audit report, research-readiness library).
- **Next step:** Open the draft PR for #4583.

### DL-#4568 · Accessibility Statement Page

- **State:** in_review
- **Owner:** claude
- **PR:** see this session's draft PR
- **Issue:** #4568 (epic #4569 — E9 Accessibility Conformance)
- **Branch:** `claude/issue-4568`
- **Paths:** `pages/accessibility.qmd`, `_quarto.yml`, `tests/test_accessibility_statement_page.py`, `tests/test_page_style_discipline.py`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (6/6 new-test-file checks pass; 248 passed across the focused content/link-gate/style-discipline suite; ruff and black clean; `check_title_case.py` clean.)
- **Summary:** Publishes an accessibility statement stating the WCAG 2.1 Level AA conformance target, summarizing the known-issues inventory tracked in #4139, and giving a contact route (GitHub Issues, email) for reporting barriers; linked from the site footer.
- **Next step:** Awaiting frontier-agent review of the draft PR.

### DL-#4548 · Render or Retire Orphaned Per-Article Bibliography Files

- **State:** in_review
- **Owner:** claude
- **PR:** not created
- **Issue:** #4548 (epic #4552)
- **Branch:** `claude/issue-4548`
- **Paths:** `_quarto.yml`, `articles/*-bibliography.md` (21 files), `articles/proximal-distal-energy-transfer.qmd`, `articles/wrist-universal-joint.qmd`, `scripts/check_quarto_render_coverage.py`, `tests/test_check_quarto_render_coverage.py`, `docs/development/content-architecture.md`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (`python3 -m pytest -q` full suite passed after `python3 -m scripts.regenerate_claim_audit_evidence` refreshed the `force-mobility-matrices-bibliography.md` review-evidence digest the added frontmatter changed; `python3 -m ruff check .` and `python3 -m black --check --line-length 100 .` both clean; `python3 -m scripts.check_quarto_render_coverage` and `python3 -m scripts.link-checker --site-gate --root .` both pass against the real repo.)
- **Summary:** Added the `articles/*-bibliography.md` Quarto render rule (mirroring the pre-existing `critiques/*.md` rule) and minimal title/description front matter to the 22 companion bibliography files, so they render instead of 404ing; fixed the two links that pointed at raw `.md`/GitHub-blob sources; kept and front-mattered the one orphan companion file (`Pinocchio_Project_Outline-bibliography.md`) because its annotated content is substantive; documented the pattern.
- **Next step:** Open the draft PR for review.

### DL-#4504 · Configure Search, and Include Maturity in Results

- **State:** in_review
- **Owner:** claude
- **PR:** not created yet (draft PR to be opened this session)
- **Issue:** #4541 (epic #4543, E6 — Interactive Models and Reproducibility)
- **Branch:** `claude/issue-4541`
- **Paths:** `models/dataset-explorer.qmd`, `js/dataset-explorer.js`, `js/dataset-explorer-ui.js`, `css/dataset-explorer.css`, `scripts/generate_dataset_explorer_manifest.py`, `data/dataset_explorer_manifest.json`, `tests/dataset-explorer.test.js`, `tests/dataset-explorer-ui.test.js`, `tests/test_generate_dataset_explorer_manifest.py`, `scripts/sync_frontend_assets.py` (registered the two new JS modules), `_quarto.yml` (navbar entry under Build → Datasets), `data/trust/claim_audit_inventory.json` (digests regenerated via `scripts/regenerate_claim_audit_evidence.py` after the `_quarto.yml` edit), `SPEC.md`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: `npx jest` 28 suites/455 passed/19 skipped; targeted `pytest` across `test_generate_dataset_explorer_manifest.py`, `test_claim_audit_inventory.py`, `test_claim_audit_output_boundary.py`, `test_sync_frontend_assets.py`, `test_check_single_title.py`, `test_site_trust_surface_audit.py` — 84/84 passed; `ruff check .` and `black --check --line-length 100 .` clean repo-wide; `stylelint css/dataset-explorer.css` clean; site link gate passes ("Site gate passed!"); `check_spec_changelog.py` passes)
- **Summary:** New browser page listing every `data/ztcf/`, `data/population_generalization/`, and `data/proximal_distal_energy_transfer/` fixture from a generated manifest. A hand-written JSON Schema validator (draft 2020-12 keyword subset used by AffineDrift's fixture schemas) checks each fixture against its published schema client-side; only `data/ztcf/` has a published `*.schema.json` today, so the other two families are reported as "schema unavailable" rather than a fabricated pass. Each fixture gets an accessible data table (generic JSON flatten, capped at 500 rows) and a download button whose SHA-256 is computed in-browser from the exact fetched bytes. The page is linked only from `_quarto.yml`'s navbar (Build → Datasets), not from existing narrative articles: those articles' digests are pinned as claim-audit review evidence, so cross-linking them was reverted; `_quarto.yml` is pinned too, so its edit required running `scripts/regenerate_claim_audit_evidence.py` (the sanctioned in-place digest refresh) to keep `data/trust/claim_audit_inventory.json` current.
- **Next step:** Push the branch, open the draft PR, and let CI's `quarto render`/Playwright lane confirm the page renders and passes axe-core (not run locally; see HANDOFF.md).
- **Issue:** #4504 (WEB-02.10; epic #4514)
- **Branch:** `claude/issue-4504`
- **Paths:** `_quarto.yml`, `_includes/site-head.html`, `js/search-maturity-badge.js`, `scripts/generate_search_maturity_index.py`, `css/search-metrics.css`, `articles/zero-torque-counterfactual.qmd`, `.github/workflows/deploy-website.yml`, `tests/e2e/search.spec.js`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (SELF: `npx jest` 441 passed/19 skipped; `pytest --timeout=120 -q` all passed; ruff/black clean; `check_spec_changelog` and `regenerate_claim_audit_evidence --check` pass. Full-site Playwright E2E not run locally — `quarto render` is blocked in this sandbox; CI's `e2e-tests` job validates the new ZTCF search spec.)
- **Summary:** Configures an explicit Quarto `search:` block (overlay, limit 10, `/`/`s` shortcut), removes the unverified `SearchAction` JSON-LD (its target was never implemented), and injects the page-header-card maturity badge into matching search results via a generated `search-maturity.json` index and a client-side DOM-annotation module.
- **Next step:** Push the branch, open the draft PR, and let CI's `e2e-tests` job confirm the new "ZTCF" search spec passes against the real full-site render.
### DL-#4535 · DCR Visualiser Widget

- **State:** in_review
- **Owner:** claude
- **PR:** not created yet (opened by the orchestrator, not this session)
- **Issue:** #4535 (WEB-06.5; epic #4543)
- **Branch:** `claude/issue-4535`
- **Paths:** `articles/controllability-drift-ratio.qmd`, `js/dcr-visualizer.js`, `js/dcr-visualizer-ui.js`, `css/dcr-visualizer.css`, `tests/dcr-visualizer.test.js`, `tests/dcr-visualizer-ui.test.js`, `tests/test_dcr_visualizer_parity.py`, `tests/fixtures/dcr_visualizer_parity.json`, `scripts/sync_frontend_assets.py`, `data/research_protocols/library.json`, `data/research_protocols/public_summary.json`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (review response: `npx jest tests/dcr-visualizer.test.js tests/dcr-visualizer-ui.test.js tests/rotation-converter-ui.test.js` 36 passed; targeted `pytest` incl. `test_dcr_visualizer_parity.py`, `test_sync_frontend_assets.py`, `test_deployment_integrity.py`, `test_check_css_architecture.py`, `test_research_protocol_readiness.py`, `test_claim_audit_inventory.py` all passed; `ruff check .` and `black --check --line-length 100 .` clean)
- **Summary:** Adds an interactive DCR-through-swing-phase widget to the DCR article, built on a pure-JS mirror of `src/affine_control/reachability.py`'s `LinearScalarSystem`/`instantaneous_scalar_dcr`/`scalar_linear_reachable_interval`. It compares an additive-drift and a state-dependent-drift system that share one instantaneous DCR at the phase start but different reachable-interval widths (the same fixture governed by `tests/test_dcr_event_sensitivity_protocol.py`), explicitly demonstrating claim `ad-dcr-001`, and links that claim from the widget. Review response: relabeled the phase slider and heading to remove the golf-specific "swing phase" framing, added a `<thead>`/`scope="col"` header row to the results table, added a `<noscript>` fallback with the default example's values, moved all inline styles and hex literals into `css/dcr-visualizer.css` (theme-variable-driven, with a dark-mode override for the two series accent colors, and registered in `scripts/sync_frontend_assets.py`'s deploy mirror map alongside the two JS modules, which had been missing from it), and centralized the shared parity numbers into `tests/fixtures/dcr_visualizer_parity.json` read by both the pytest and Jest suites. Regenerated the claim-audit and research-readiness digests that pin the article's SHA-256 after editing it.
- **Next step:** Let CI's Jest/E2E/quality-gate confirm the widget renders, mirrors correctly into `docs/`, and passes axe-core on the DCR page.

### DL-#4577 · Performance of MathJax-Heavy Pages

- **State:** in_review
- **Owner:** claude
- **PR:** not created yet (draft PR to be opened this session)
- **Issue:** #4577 (WEB-10.9; epic #4579 / E10)
- **Branch:** `claude/issue-4577`
- **Paths:** `_includes/mathjax-loader.html`, `tests/mathjax-loader.test.js`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: `npx jest tests/mathjax-loader.test.js` 10/10 passed after RED→GREEN; full `npx jest` 432 passed/19 skipped/0 failed; `ruff check .` and `black --check --line-length 100 .` clean repo-wide)
- **Summary:** Evaluated the issue's "smaller MathJax component build" option: swapped the gated loader's CDN bundle from `tex-mml-chtml.js` to `tex-chtml.js` (TeX input + CHTML output only), dropping the unused MathML *input* jax that Quarto's TeX-only `.math` spans never exercise, with a re-pinned SRI hash. Measured before/after via the pinned CDN URLs: 1,173,007 → 1,160,989 bytes raw (264,567 → 261,828 bytes gzip transfer) — applies to every math-bearing page, including the three heaviest chapters by display-equation density (`Tangent_Hyperplanes_Unified_Thesis.qmd` 329, `volume2_content.qmd` 284, `superposition.qmd` 190 delimiter occurrences). `enableAssistiveMml` (screen-reader MathML) ships identically in both bundles, so accessibility is unchanged. The larger "build-time pre-rendering to SVG/MathML" option in the issue was evaluated and not implemented — see HANDOFF.md for why.
- **Next step:** Owner/frontier review of the draft PR; no further implementation planned pending review feedback.

### DL-#4578 · Social Cards per Page

- **State:** in_review
- **Owner:** claude
- **PR:** draft (see HANDOFF.md for link)
- **Issue:** #4578 (WEB-10.10; epic #4579 / E10)
- **Branch:** `claude/issue-4578`
- **Paths:** `scripts/generate_social_cards.py`, `tests/test_social_cards.py`, `logo/social-cards/*.png`, `articles/The_Physics_of_Golf/quarto/index.qmd`, `articles/The_Geometry_of_Motion/quarto/index.qmd`, `articles/proximal_distal_energy_transfer/index.qmd`, `.github/workflows/deploy-website.yml`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: 13/13 tests pass across test_social_cards.py and test_image_budget.py; ruff and black --line-length 100 clean)
- **Summary:** Generates one 1200x630 Open Graph card per book/series (title, badge, signature graphic) at build time instead of one site-wide card, checked in like the existing site-wide `logo/og-card.png`, and wires three representative landing pages to use theirs via per-page `open-graph`/`twitter-card` overrides.
- **Next step:** After merge and deploy, run a social-card debugger against the three live page URLs to close out the issue's second acceptance criterion (see HANDOFF.md Blockers).
### DL-#4567 · Wire Alt-Text and Long-Description Validation Into CI

- **State:** in_progress
- **Owner:** claude
- **PR:** not created
- **Issue:** #4567 (epic #4569)
- **Branch:** `claude/issue-4567`
- **Paths:** `scripts/validate_accessibility.py`, `config/accessibility-long-description-baseline.json`, `tests/test_validate_accessibility.py`, `.github/workflows/ci-standard.yml`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: 20/20 `test_validate_accessibility.py` tests pass; ruff and black clean; `--qmd-only` exits 0 across the full repo; `check_spec_changelog`, `check_module_size_budget`, `check_root_hygiene`, `check_workflow_action_pins` all pass)
- **Summary:** Wires `validate_accessibility.py`'s alt-text/heading/long-description checks into `quality-gate` via a new `--qmd-only` CI step; adds a long-description check for complex E8 SVG diagrams, grandfathering 39 pre-existing matplotlib-generated SVG figures via a new baseline file; the script's unrelated CSS colorblind-color and JS ARIA-label checks remain unwired (pre-existing failures, out of scope).
- **Next step:** Open the draft PR referencing Closes #4567 and release the lease.

### DL-#4549 · Datasets Page Rebuild (Licences, Schemas, Checksums)

- **State:** in_review
- **Owner:** claude
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4632 (draft)
- **Issue:** #4549 (WEB-07.7; epic #4552)
- **Branch:** `claude/issue-4549`
- **Paths:** `data/datasets.yml`, `src/tools/datasets_catalog.py`, `scripts/generate_datasets_catalog.py`, `resources/resources-datasets.qmd`, `css/resources.css`, `docs/css/resources.css`, `tests/test_generate_datasets_catalog.py`, `.github/workflows/ci-standard.yml`, `tests/conftest.py`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (`pytest tests/test_generate_datasets_catalog.py` 14 passed; `generate_datasets_catalog --check` up to date; ruff/black clean repo-wide; mypy clean on new modules; Quarto render-coverage/syntax/xref/single-title/title-case checks pass; full pre-push hook chain including `pytest-unit` passed; PR #4632 opened as draft)
- **Summary:** Rebuilds the Datasets resource page as a generated catalogue from `data/datasets.yml`, replacing four truncated-looking third-party cards and the `mini.s-shot.ru` thumbnail host with verified licence/size/modality/access/citation fields, and adds an "AffineDrift Data Artefacts" section listing `data/ztcf`, `data/research_protocols`, and `schemas` with a real SHA-256 checksum per file.
- **Next step:** Awaiting frontier-agent PR review.
### DL-#4595 · Cache Quarto Renders in CI

- **State:** in_review
- **Owner:** claude
- **PR:** not created
- **Issue:** #4595 (WEB-13.1; epic #4604 / E13)
- **Branch:** `claude/issue-4595`
- **Paths:** `.github/workflows/ci-standard.yml`, `tests/test_deployment_integrity.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: 16/16 test_deployment_integrity.py pass + 1 skipped, 2/2 test_workflow_action_pins.py pass, ruff/black clean repo-wide)
- **Summary:** Caches the PR `e2e-tests` Quarto render output (`docs/` + `.quarto/`) keyed on a hash of every render-relevant source file, skipping the ~14-minute render only on an exact hash match; deploy's clean full render is untouched. A true per-file incremental render was scoped out because it would conflict with the existing #4126 invariant guaranteeing the E2E lane always renders every route; see HANDOFF.md for the full reasoning.
- **Next step:** Owner/frontier review of the draft PR, including the `tier:strong` follow-up proposed for reconciling incremental rendering with the #4126 full-coverage guarantee if the ≥30% median-time criterion is not met by the cache alone.

### DL-#4600 · Service-Worker Cache Busting by Content Hash

- **State:** in_review
- **Owner:** claude
- **PR:** not created yet (draft PR to be opened this session)
- **Issue:** #4600 (epic #4604)
- **Branch:** `claude/issue-4600`
- **Paths:** `service-worker.js`, `tests/e2e/offline.spec.js`, `.github/workflows/ci-standard.yml`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (Jest full suite 420 passed/19 skipped; `pytest tests/test_update_sw_cache_version.py` 12 passed; `ruff check .` and `black --check --line-length 100 .` clean. Full-site Playwright E2E not run locally — `quarto render` is out of scope for this session; CI's `e2e-tests` job validates the re-enabled offline spec.)
- **Summary:** Removes the stale TODO in `service-worker.js` referencing closed issue #1459 (content-hash cache busting is already implemented by `scripts/update_sw_cache_version.py`, which hashes precached CSS/JS assets into `CACHE_NAME`), replaces the offline E2E test's flaky fixed 3s wait with a deterministic `navigator.serviceWorker.ready` wait, and drops that one title from the `ci-standard.yml` full-site E2E exclusion list.
- **Next step:** Push the branch, open the draft PR, and let CI's `e2e-tests` job confirm the re-enabled offline spec passes against the real full-site render.
### DL-#4596 · Report Broken External Links as Issues

- **State:** in_review
- **Owner:** claude
- **PR:** not created
- **Issue:** #4548 (epic #4552)
- **Branch:** `claude/issue-4548`
- **Paths:** `_quarto.yml`, `articles/*-bibliography.md` (21 files), `articles/proximal-distal-energy-transfer.qmd`, `articles/wrist-universal-joint.qmd`, `scripts/check_quarto_render_coverage.py`, `tests/test_check_quarto_render_coverage.py`, `docs/development/content-architecture.md`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (`python3 -m pytest -q` full suite passed after `python3 -m scripts.regenerate_claim_audit_evidence` refreshed the `force-mobility-matrices-bibliography.md` review-evidence digest the added frontmatter changed; `python3 -m ruff check .` and `python3 -m black --check --line-length 100 .` both clean; `python3 -m scripts.check_quarto_render_coverage` and `python3 -m scripts.link-checker --site-gate --root .` both pass against the real repo.)
- **Summary:** Added the `articles/*-bibliography.md` Quarto render rule (mirroring the pre-existing `critiques/*.md` rule) and minimal title/description front matter to the 22 companion bibliography files, so they render instead of 404ing; fixed the two links that pointed at raw `.md`/GitHub-blob sources; kept and front-mattered the one orphan companion file (`Pinocchio_Project_Outline-bibliography.md`) because its annotated content is substantive; documented the pattern.
- **Next step:** Open the draft PR for review.
- **Issue:** #4595 (WEB-13.1; epic #4604 / E13)
- **Branch:** `claude/issue-4595`
- **Paths:** `.github/workflows/ci-standard.yml`, `tests/test_deployment_integrity.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: 16/16 test_deployment_integrity.py pass + 1 skipped, 2/2 test_workflow_action_pins.py pass, ruff/black clean repo-wide)
- **Summary:** Caches the PR `e2e-tests` Quarto render output (`docs/` + `.quarto/`) keyed on a hash of every render-relevant source file, skipping the ~14-minute render only on an exact hash match; deploy's clean full render is untouched. A true per-file incremental render was scoped out because it would conflict with the existing #4126 invariant guaranteeing the E2E lane always renders every route; see HANDOFF.md for the full reasoning.
- **Next step:** Owner/frontier review of the draft PR, including the `tier:strong` follow-up proposed for reconciling incremental rendering with the #4126 full-coverage guarantee if the ≥30% median-time criterion is not met by the cache alone.
- **Issue:** #4596 (epic #4604)
- **Branch:** `claude/issue-4596`
- **Paths:** `scripts/link-checker.py`, `.github/workflows/link-checker.yml`, `docs/LINK-CHECKER.md`, `tests/test_link_checker_script.py`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: 79/79 relevant link-checker tests pass, ruff/black clean, SPEC changelog check passes)
- **Summary:** Scheduled external-link check now upserts a single tracking issue (find-or-update, close on all-clear) instead of only logging, checks DOI links through their doi.org redirect, and attaches an archive.org fallback suggestion to each dead link.
- **Next step:** Push branch, open draft PR referencing Closes #4596, and release the fleet lease.

### DL-#4588 · Keep Internal Governance Vocabulary Out of Reader Prose

- **State:** in_progress
- **Owner:** claude
- **PR:** not created
- **Issue:** #4567 (epic #4569)
- **Branch:** `claude/issue-4567`
- **Paths:** `scripts/validate_accessibility.py`, `config/accessibility-long-description-baseline.json`, `tests/test_validate_accessibility.py`, `.github/workflows/ci-standard.yml`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (SELF: 20/20 `test_validate_accessibility.py` tests pass; ruff and black clean; `--qmd-only` exits 0 across the full repo; `check_spec_changelog`, `check_module_size_budget`, `check_root_hygiene`, `check_workflow_action_pins` all pass)
- **Summary:** Wires `validate_accessibility.py`'s alt-text/heading/long-description checks into `quality-gate` via a new `--qmd-only` CI step; adds a long-description check for complex E8 SVG diagrams, grandfathering 39 pre-existing matplotlib-generated SVG figures via a new baseline file; the script's unrelated CSS colorblind-color and JS ARIA-label checks remain unwired (pre-existing failures, out of scope).
- **Next step:** Open the draft PR referencing Closes #4567 and release the lease.

- **Issue:** #4588 (epic #4594)
- **Branch:** `claude/issue-4588`
- **Paths:** `scripts/check_governance_vocabulary.py`, `tests/test_check_governance_vocabulary.py`, `config/governance-vocabulary-baseline.json`, `pages/glossary.qmd`, `.github/workflows/ci-standard.yml`, plus prose edits across `pages/`, `resources/`, `books/`, and `models/`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (SELF: 52/52 tests pass across test_check_governance_vocabulary.py and test_check_terminology.py; lint clean against baseline)
- **Summary:** Adds a warn-mode CI lint for internal governance vocabulary ("governed", "qualified", "provenance", "protected", "fail-closed") in reader prose, a plain-language glossary page, and removes the vocabulary from the hub/entry reader pages. Full 75% corpus-wide reduction is blocked on the still-open prerequisite #4587 (editorial style guide) for the remaining `articles/` chapter corpus; see the HANDOFF.md Blocked section.
- **Next step:** Land #4587, then use its standard to rewrite the `articles/` chapter corpus and shrink the baseline.

### DL-#4563 · Restore the Ten Excluded Browser Tests

- **State:** in_review
- **Owner:** claude
- **PR:** to be opened as a draft by this session
- **Issue:** #4563 (WEB-09.3; epic #4569 / E9 — Accessibility Conformance)
- **Branch:** `claude/issue-4563`
- **Paths:** `.github/workflows/ci-standard.yml`, `tests/e2e/touch-targets.spec.js`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (statically, not by running Playwright — see Blocked note on the PR; `npx jest` 429/429 passing, unaffected)
- **Summary:** Nine of the ten titles `--grep-invert`-excluded from the Chromium E2E job (#4140) were already fixed in source by PR #4200 (stale homepage/navigation/user-journey selectors, dark-theme contrast, back-to-top touch target, bibliography detail panel) but the exclusion list itself was never removed, so CI never actually validated those fixes; this issue removes the nine now-obsolete exclusions and fixes a tenth defect found by re-reading the suite (`touch-targets.spec.js`'s shared helper counted a CSS-hidden element, such as the collapsed `.navbar-toggler` at desktop width, as a non-compliant 0×0 touch target instead of skipping it). The tenth excluded title, `matches visual snapshot` (60 pixel-comparison cases in `visual.spec.js`), stays excluded: no baseline PNGs are committed anywhere in the repo, so it cannot pass regardless of site correctness; generating them needs a `playwright test --update-snapshots` run on the actual fleet CI runner (font metrics differ from this sandbox), which is out of reach here.
- **Next step:** Frontier review of the draft PR's Blocked note (pixel-snapshot baselines) and CI's e2e-tests run, which is the only environment in this fleet that can actually execute the restored tests against a real Quarto render.

### DL-#4591 · Readability Measurement Tool

- **State:** in_review
- **Owner:** claude
- **PR:** #4591 (draft)
- **Issue:** #4591 (WEB-12.5; epic #4594 / E12)
- **Branch:** `claude/issue-4591`
- **Paths:** `scripts/check_readability.py`, `tests/tools/test_check_readability.py`, `.github/workflows/ci-standard.yml`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (33/33 new pytest cases pass; ruff, black --line-length 100, and mypy clean on the new module.)
- **Summary:** Advisory Flesch-Kincaid grade-level checker for lay blocks, `summary-plain`, and hub pages, wired into CI as a non-blocking step with a JSON report artifact; threshold (grade 10) taken from WEB-12.1's stated targets since the style guide itself (WEB-12.1) is still open.
- **Next step:** Owner/frontier review of the draft PR; no further implementation planned pending review feedback.
### DL-#4524 · Extend Critique Annotations to ZTCF and Proximal–Distal Pages

- **State:** in_progress
- **Owner:** local
- **PR:** not created
- **Issue:** #4524
- **Branch:** `fix/web-05-3-critique-annotations-4524`
- **Paths:** `scripts/generate_claim_critique_ledger.py`, `data/trust/claim_critique_ledger.json`, `articles/zero-torque-counterfactual.qmd`, `articles/theory-part2.qmd`, `articles/proximal-distal-energy-transfer.qmd`, `data/trust/claim_audit_inventory.json`, `data/trust/proximal_distal_falsification_atlas.json`, `tests/test_claim_critique_ledger.py`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-29 (d53290cd / SELF: 19/19 test_claim_critique_ledger.py tests pass, 18/18 test_claim_audit_inventory.py pass, 17/17 test_proximal_distal_falsification_atlas.py pass, all ledgers and reports verified)
- **Summary:** Enforces that every critique maps to every page whose claim it targets and extends critique annotations to the ZTCF, Theory Part 2, and Proximal-Distal pages.
- **Next step:** Commit changes, push branch, open PR referencing Closes #4524, and release lease.

### DL-#4523 · Readable Claim Ledger Page

- **State:** in_review
- **Owner:** claude
- **PR:** #4637 (draft) — https://github.com/D-sorganization/AffineDrift/pull/4637
- **Issue:** #4523 (epic #4530)
- **Branch:** `claude/issue-4523`
- **Paths:** `evidence/claims.qmd`, `scripts/generate_claims_ledger.py`, `tests/test_claims_ledger.py`, `_includes/generated/claims-ledger.qmd`, `_includes/generated/claims-ledger/drift-control-ratio.qmd`, `articles/drift-control-ratio.qmd`, `_quarto.yml`, `src/tools/site_page_scan.py`, `tests/test_site_link_gate.py`, `scripts/check_root_hygiene.py`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`, `reports/scientific-claim-audit.md`
- **Started:** 2026-09-29
- **Last verified:** 2026-09-30 (SELF: merged origin/main forward, fixed the stale `articles/controllability-drift-ratio.qmd` path left over from PR #4629's DCR rename, and reviewed/added claim-audit inventory records for the new `/evidence/claims.html` route.)
- **Summary:** Generates a dedicated `evidence/claims.qmd` page from `data/trust/claim_registry.json` — one accessible card per claim with plain/formal statements, evidence rung, falsifiers, related critiques, and the pages making the claim — and links every claim-making page back to its ledger entry via a generated per-page include.
- **Next step:** Open the draft PR for frontier review; `scripts/generate_sitemap.py`'s `SITEMAP_CONTENT_DIRS` does not yet include `evidence/` (noted as a follow-up, not blocking).

### DL-#4477 · Companion Opening and Whole-Swing Ledger

- **State:** shipped
- **Owner:** codex
- **PR:** #4478
- **Issue:** #4477 (corpus #4021; epic #4009)
- **Branch:** `fix/4477-ledger-rigor`
- **Paths:** `articles/proximal_distal_companion/chapters/ch01_follow_the_energy.qmd`, `articles/proximal_distal_companion/chapters/ch29_whole_swing_ledger.qmd`, `articles/proximal-distal-a-journey-through-the-swing.qmd`
- **Started:** 2026-09-28
- **Last verified:** 2026-09-28 (17 focused checks; full suite 5,626 passed/29 skipped/132 deselected, 92.88% coverage. Content 131 passed/four skipped; static checks pass. Four browser cases and 207-page PDF verified; archived NPZ consistency and seven provider hashes verified.)
- **Summary:** Reconciles ground impulse/work, rigid/flexible wrench power, shaft storage, physical mass, state and intervention semantics across the opening and synthesis; preserves the remaining chapter sources and historical review scope.
- **Next step:** Merged with required CI passing; deployment pending at the user-requested remote-main stop checkpoint. No further development.

### DL-#4475 · Green Simulation Mechanics and Implementation Evidence

- **State:** shipped
- **Owner:** codex
- **PR:** #4476
- **Issue:** #4475 (corpus #4021; epic #4009)
- **Branch:** `fix/4475-green-rigor`
- **Paths:** `articles/green-simulation.qmd`, `tests/test_green_simulation_rigor.py`, `reports/technical-review/green-provider-source-index.json`
- **Started:** 2026-09-28
- **Last verified:** 2026-09-28 (All 16 focused checks pass; full suite 5,609 passed/29 skipped/132 deselected, 92.88% coverage. Content 131 passed/four skipped; static checks pass. Four browser cases pass, zero severe axe findings; eight display equations visually inspected.)
- **Summary:** Corrects rolling/sliding dynamics and probability claims, qualifies numerical/surface/capture choices, and documents actual provider discrepancies without changing provider code.
- **Next step:** Merged and publication verified at 1a8dd00b (deployment 36397339440). No current development; broader goal paused.

### DL-#4473 · Club-Fitting Mechanics and Evidence

- **State:** shipped
- **Owner:** codex
- **PR:** #4474
- **Issue:** #4473 (corpus #4021; epic #4009)
- **Branch:** `fix/4473-fitting-rigor`
- **Paths:** `articles/technology-club-fitting.qmd`, `references/club-fitting.bib`, `tests/test_club_fitting_rigor.py`
- **Started:** 2026-09-28
- **Last verified:** 2026-09-28 (Complete article corrected; seven source/example failures reproduced; all 16 checks pass. Full suite 5,593 passed/29 skipped/132 deselected, 92.88% coverage; content 131 passed/four skipped; static checks pass. Four browser cases pass, zero severe axe findings; all ten display equations visually reviewed.)
- **Summary:** Separates model interventions and causal inference, corrects spatial/beam/mass mechanics and replaces nonexistent wire guarantees with explicit synthetic proposals.
- **Next step:** Merged and publication verified at 1a8dd00b (deployment 36397339440). No current development; broader goal paused.

### DL-#4471 · Markerless Camera Measurement Rigor

- **State:** shipped
- **Owner:** codex
- **PR:** #4472
- **Issue:** #4471 (corpus #4021; epic #4009)
- **Branch:** `fix/4471-camera-rigor`
- **Paths:** `articles/markerless-mocap-camera-selection.qmd`, `data/markerless_mocap/camera_evidence_registry_v1.json`, `tests/test_camera_selection_rigor.py`
- **Started:** 2026-09-27
- **Last verified:** 2026-09-27 (Full article and 57 registry claims inspected. RED: ten numerical passes, six source failures; GREEN: all 16 plus 14 registry contracts pass. Manufacturer modes and study transfer corrected.)
- **Summary:** Connects exposure, timing, payload, geometry and differentiation to the limits of golf-swing inference; preserves unavailable prices/licenses and unmeasured physical qualification.
- **Next step:** Merged and publication verified at 1a8dd00b (deployment 36397339440). No current development; broader goal paused.

### DL-#4469 · Volume I Mathematical Reference

- **State:** shipped
- **Owner:** codex
- **PR:** #4470
- **Issue:** #4469 (corpus #4021; epic #4009)
- **Branch:** `fix/4469-volume-one-reference`
- **Paths:** `articles/The_Geometry_of_Motion/Volume_I/main.tex`, `books/tangent-space-methods.qmd`, `tests/test_volume_one_reference_rigor.py`
- **Started:** 2026-09-27
- **Last verified:** 2026-09-27 (21 focused; 52 reference/audit contracts; full suite 5,561 passed, 29 skipped, 132 deselected, 92.88% coverage; 131 content checks passed/four skipped. Static checks pass. Full 149-page PDF compiles; affected pages visually inspected. Public map 4/4 browser cases, zero severe axe findings. Source/PDF 14b8f183; six-path evidence 782dc161. Four parallel supplied-text Flash reviews adjudicated.)
- **Summary:** Reconciles notation and mathematical reference material with corrected chapter assumptions; separates geometry, flow sensitivity and control certification.
- **Next step:** Published at 24c77a55. Deployment 36389665569, CI 36389665580 and Compile 36389665540 pass. Live gate 960/960; four reviewed-route cases, zero severe axe findings; both pinned source/PDF downloads and six hashes verified. Receipt: volume-one-reference-publication.json.

### DL-#4467 · Secondary-Axis Mechanics and Putter Design

- **State:** shipped
- **Owner:** codex
- **PR:** #4468
- **Issue:** #4467 (corpus #4021; epic #4009)
- **Branch:** `fix/4467-secondary-axis`
- **Paths:** `articles/secondary-axis-stability.qmd`, `critiques/intermediate_axis_fallacy.md`, `critiques/misattribution_of_stability_gravity.md`, `tests/test_secondary_axis_rigor.py`
- **Started:** 2026-09-27
- **Last verified:** 2026-09-27 (19 focused mechanics/source checks; full Python suite 5,540 passed, 29 skipped, 132 deselected, 92.88% src coverage; 80 final mechanics/audit contracts pass. Three final Quarto routes, 12/12 light/dark mobile/desktop cases, zero serious/critical axe violations. All 117 math expressions loaded; 17 display equations visually checked at both widths. Ruff, Black 728 files, title audit 638 sources and mypy 91 sources pass. Eight exact evidence paths bound to 919f6d18; terminology scope correction and repeated 12-case browser gate pass. Final static CI passes after naming the unchanged gravity test constant.)
- **Summary:** Separates free spin, supported motion, gravity and collision; supplies checked inertia-rate and moment comparisons; removes unsupported equipment and neural claims from article and critiques.
- **Next step:** Published at 54d73e39; deployment 36386984016 and post-merge CI pass. Revision-bound live gate passes all 960 site cases and 12 reviewed-route cases with zero severe axe findings. Eight evidence hashes match. Receipt: reports/technical-review/secondary-axis-publication.json.

### DL-#4465 · Contraction Development Workspace

- **State:** shipped
- **Owner:** codex
- **PR:** #4466
- **Issue:** #4465 (corpus #4021; epic #4009)
- **Branch:** `fix/4465-contraction-workspace`
- **Paths:** `articles/tangent-hyperplane-contraction/`, `tests/test_contraction_workspace_rigor.py`, `reports/technical-review/contraction-workspace-*`
- **Started:** 2026-09-27
- **Last verified:** 2026-09-27 (14 focused checks pass after six source RED failures; 5,519 full-suite passes with two temporary Playwright root-hygiene failures, resolved and all six hygiene tests pass; 92.88% src coverage. Content lint 131 passed/four skipped. Ruff, Black, title audit and mypy pass. Native 15-page PDF visually checked; ten standalone renders and twenty browser cases pass.)
- **Summary:** Corrects the full development manuscript, consolidated QMD, eight chapters and hub; separates optimal cost from contraction, supplies counterexamples and explicit domain/coordinate/contact assumptions. Existing production exclusions and redirects remain intact.
- **Next step:** Preserve the excluded-route review receipt after protected PR #4466 merged at e48c9e00.

### DL-#4463 · Biological Model Selection

- **State:** shipped
- **Owner:** codex
- **PR:** #4464
- **Issue:** #4463 (corpus #4021; epic #4009)
- **Branch:** `fix/4463-biology-model-selection`
- **Paths:** `articles/The_Geometry_of_Motion/Volume_III/`, `books/biomechanics-biology-to-systems.qmd`, `tests/test_biology_model_selection_rigor.py`
- **Started:** 2026-09-27
- **Last verified:** 2026-09-27 (PR #4464 merged at 855b6fa6; deployment 36378430500 succeeded. Downloaded artifact 10952174815 verified by SHA-256: 960/960 site cases pass, all four biology cases and three pinned source/PDF downloads verified; zero serious/critical axe violations. Seven scientific evidence paths match their checkpoint and deployed merge. Prior numerical/render validation retained in review receipts.)
- **Summary:** Connects model assumptions to golf delivery and biological inference; corrects modal dynamics, force/power pairing, redundancy, inertial accounting and excitation affinity without asserting empirical human parameters.
- **Next step:** Preserve the source and publication receipts for this completed chapter correction.


### DL-#4429 · Site-Surface Audit Provenance Reconciliation

- **State:** shipped
- **Owner:** local
- **PR:** #4453
- **Issue:** #4429 (site-surface audit #4063; corpus #4021; epic #4009)
- **Branch:** `feat/4429-reconcile-audit-provenance`
- **Paths:** `data/trust/site_trust_surface_audit.json`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`, `reports/site-trust-surface-audit.md`, `reports/technical-review/site-surface-provenance-review.md`, `reports/technical-review/site-surface-provenance-reconciliation.json`, `SPEC.md`, `docs/development/DEVELOPMENT_LOG.md`, `docs/development/HANDOFF.md`
- **Started:** 2026-09-24
- **Last verified:** 2026-09-24 (PR #4453 merged cdd0044c; issue #4429 closed; 10/10 site trust surface audit tests and 18/18 claim audit inventory tests passed in CI.)
- **Summary:** Reconciles historical provenance of site-surface audit evidence across 12 canonical routes, binds exact source bytes to committed checkpoint 63d98d19, resolves test symbol provenance for ad-finding-notation-render-integrity, and preserves render history.
- **Next step:** None. PR #4453 merged 2026-09-24; issue #4429 closed.

### DL-#4450 · Why Physics Matters

- **State:** shipped
- **Owner:** codex
- **PR:** #4451
- **Issue:** #4450 (corpus #4021; epic #4009)
- **Branch:** `fix/why-physics-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch01_why_physics.tex`, `articles/The_Physics_of_Golf/quarto/ch01_why_physics.qmd`, `articles/The_Physics_of_Golf/main.pdf`, `articles/The_Physics_of_Golf/figures/why_physics_release.svg`, `articles/The_Physics_of_Golf/figures/why_physics_release.pdf`, `scripts/build_why_physics_figure.py`, `tests/test_why_physics_rigor.py`
- **Started:** 2026-09-23
- **Last verified:** 2026-09-27 (checked head 82b1a904 and merge 530778ef have identical trees; all twelve evidence paths unchanged on deployed bf78cb2a. CI 35938311583 and post-merge CI 35940168938 succeeded. Deployment 36298955953 succeeded; SHA-256-verified live artifact 10925830179 passed 960/960, including four Chapter 1 cases, with zero serious/critical axe violations. Separate publication receipt retained.)
- **Summary:** Replaces unsupported force/energy and expertise claims with a defined input baseline, explicit constraints, checked manufactured work/release examples and six worked answers; connects mechanics to finite-time club delivery and impact.
- **Next step:** None for this correction. Merged to main.

### DL-#4444 · Language of Motion

- **State:** shipped
- **Owner:** codex
- **PR:** #4448
- **Issue:** #4444 (corpus #4021; epic #4009)
- **Branch:** `fix/language-motion-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch02_language_of_motion.tex`, `articles/The_Physics_of_Golf/quarto/ch02_language_of_motion.qmd`, `articles/The_Physics_of_Golf/main.pdf`, `tests/test_language_motion_rigor.py`, `tests/test_audit_quarto_figure_parity.py`, `reports/technical-review/language-motion-review.md`, `reports/technical-review/language-motion-render-verification.json`
- **Started:** 2026-09-23
- **Last verified:** 2026-09-23 (Local 5516 passed/29 skipped/132 deselected, 92.88% src coverage; CI 5468 passed/32 skipped/132 deselected, 92.85% coverage. PR #4448 merged at `9d72e2c2124730a8642be45e837c9069b2484368` with every required check green; its tree matches checked head `8ccf6f664f63ff5c5fc6e2810e00209237e36809`. Deployment 35925227535 succeeded: live 960/960, all four cases for each reviewed route, and zero serious/critical axe violations. Artifact 10779298519.)
- **Summary:** Reconciles coordinate signs, state closure, constraints, directional kinematics and worked examples with Chapter 3; replaces unsupported human interpretations with a checked synthetic trajectory and shared geometry.
- **Next step:** None for this correction. Merge the documentation-only turnover checkpoint; the broader corpus/whole-book review remains active under the latest explicit resume.

### DL-#4445 - Deferred Catalog Enforcement

- **State:** shipped
- **Owner:** codex
- **Issue:** #4445; central Repository_Management#1687
- **Branch:** `chore/4445-deferred-catalog-guard`
- **PR:** #4446
- **Paths:** `shared_scripts/`, `.pre-commit-config.yaml`, `pyproject.toml`, `tests/test_deferred_catalog_hook.py`, `docs/development/deferred-catalog-bundle.json`, `AGENTS.md`, `CLAUDE.md`, `AGENT_HANDOFF.md`, `SPEC.md`
- **Started:** 2026-09-23
- **Last verified:** 2026-09-23 (PR #4446 merged to main; pre-commit hook and validator deployed; canonical hashes and integration controls pass.)
- **Summary:** Deploys the canonical validator and fail-closed catalog hook, preserving v1 plans and separating pending resources from approval or measurement.
- **Next step:** None. Merged to main.

### DL-#4441 · Contraction Lay Article

- **State:** shipped
- **Owner:** codex
- **PR:** #4443
- **Issue:** #4441 (corpus #4021; epic #4009)
- **Branch:** `fix/contraction-lay-rigor`
- **Paths:** `articles/tangent-hyperplane-articles/Advanced/Contraction_Tangent_LAYMAN.qmd`, `tests/test_contraction_lay_rigor.py`, `reports/technical-review/contraction-lay-review.md`, `reports/technical-review/contraction-lay-render-verification.json`
- **Started:** 2026-09-23
- **Last verified:** 2026-09-23 (Corrective PR4443 merged at6036629e; its ten frozen paths are unchanged. PR #4448 merged at `9d72e2c2124730a8642be45e837c9069b2484368` with every required check green; its tree matches checked head `8ccf6f664f63ff5c5fc6e2810e00209237e36809`. Deployment 35925227535 succeeded: live 960/960, all four cases for each reviewed route, and zero serious/critical axe violations. Artifact 10779298519.)
- **Summary:** Corrects stability/metric/Riccati interpretation, removes unsupported results, and connects feasible feedback and mechanical impedance to finite-time strike and event sensitivity. No comparative solver or human-performance claim.
- **Next step:** None for this correction. Merge the documentation-only turnover checkpoint; the broader corpus/whole-book review remains active under the latest explicit resume.

### DL-#4438 · Deferred Impact Project Projection

- **State:** shipped
- **Owner:** codex
- **Issue:** #4438; fleet RM#1687 / RD#1248
- **Branch:** `docs/4438-deferred-project-projection`
- **PR:** #4439
- **Paths:** `docs/project/CHARTER.md`, `docs/project/STATUS.md`
- **Started:** 2026-09-23
- **Last verified:** 2026-09-23 (implementation 1c129d52; merge sync preserves main 7664a390; source catalog/plan/README/SPEC inspected; #4253 verified open; catalog and both charter parsers pass; original planning bytes unchanged; title-case/SPEC pass; commit/pre-push hooks pass)
- **Summary:** Initial charter separates active theory/numerical synthesis from parked DV-4253 and exposes pending resource/evidence decisions. Original scientific obligations remain authoritative in the plan.
- **Next step:** #4439 merged as c169bbd9; live parked DV-4253 is verified. Enforcement continues in DL-#4445.


### DL-#4436 · Force and Mobility Ellipsoids

- **State:** shipped
- **Owner:** codex
- **PR:** #4437
- **Issue:** #4436 (corpus #4021; epic #4009)
- **Branch:** `fix/force-mobility-rigor`
- **Paths:** `articles/force-mobility-matrices.qmd`, `articles/force-mobility-matrices-bibliography.md`, `css/force-mobility.css`, `tests/test_force_mobility_rigor.py`, `reports/technical-review/force-mobility-review.md`
- **Started:** 2026-09-23
- **Last verified:** 2026-09-23 (PR #4437 passed every required check and merged at 7664a390, whose tree exactly matches checked head cacba18b. CI: 5,422 passed, 32 skipped, 132 deselected, 92.85% coverage; content 131 passed/four skips. All 56 selected local checks pass. Source/render d032cb0f binds six findings and eight paths; original science 981e8d34. Local production and expanded keyboard/axe pass 4/4 with 133 expressions and 16 displays. Deployment 35900025138 at c169bbd9 succeeded with live 960/960, including four article cases and zero serious/critical axe violations; artifact 10769877887. Independent planning PR #4439 superseded run 35898481011 without changing scientific/evidence bytes. Publication receipt: reports/technical-review/force-mobility-publication.json.)
- **Summary:** Reconciles rate/load metrics and power pairing, rank loss, dynamic authority, constrained impact, compliance and preload, grasp/constraint maps, and unsupported human interpretations. Corrects the rectangular SVD example and bibliography provenance. No empirical or physiological validation is claimed.
- **Next step:** None for this scientific release. Merge the documentation-only checkpoint, release this session and pause the broader goal at the user's request. No new tasks or rewrites.

### DL-#4431 · Nonlinear Control Insights and Physical Coupling

- **State:** shipped
- **Owner:** codex
- **PR:** #4433
- **Issue:** #4431 (core #4058; corpus #4021; epic #4009)
- **Branch:** `fix/nonlinear-control-insights-rigor`
- **Paths:** `articles/nonlinear-control-insights.qmd`, `css/nonlinear-control.css`, `tests/test_nonlinear_control_insights_rigor.py`, `reports/technical-review/nonlinear-control-insights-review.md`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (main `66f63f87` exactly matches checked head `af8347f3`; all required checks passed; deployment `35807652744` succeeded; live artifact `10729736031` passes 960/960, including four article cases, with zero serious/critical axe violations. Final source/render `a424ead9` binds eight findings and nine evidence paths; initial scientific checkpoint `3053bb71` is retained. All 55 selected checks and 131 content-lint tests pass, with four existing skips. Local production and expanded keyboard/axe checks each pass 4/4; all 106 expressions, 22 displays and six wide mobile endpoints were inspected.)
- **Summary:** Replaces indefinite inertia and degree/radian errors, energy amplification, unique physiological baseline and unsupported control/identification claims with a physical two-rod example, complete energy balance and finite-time counterexamples. The governed critique stays open; primary-source access limits are recorded. Final CI corrections fixed 17 published-link suffixes and issue/test scope metadata. Publication receipt: `reports/technical-review/nonlinear-control-insights-publication.json`.
- **Next step:** None for this release. Finish the documentation-only closeout and pause the broader goal at the user's request. No new tasks or rewrites.

### DL-#4428 · Manifesto State-Rate Units and Verification Scope

- **State:** shipped
- **Owner:** codex
- **PR:** #4432
- **Issue:** #4428 (site surfaces #4063; corpus #4021; epic #4009)
- **Branch:** `fix/manifesto-notation-units`
- **Paths:** `pages/drifter-manifesto.qmd`, `css/manifesto.css`, `reports/technical-review/manifesto-notation-review.md`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (main `2ef5c908` exactly matches checked head `c7cec8ea`; all protected checks passed; deployment `35805142089` succeeded; live artifact `10727234915` passes 960/960 checks, including all four manifesto cases, with zero serious/critical axe violations. Source/render `2250d07f` and aggregate `31664586` remain frozen; five findings, local browser 4/4, all 11 expressions and 28 audit tests verified.)
- **Summary:** Distinguishes generalized input load, acceleration contribution and full-state rate; includes retained flexible coordinates and memory/constraint boundaries; corrects Part 5 capability and Part 4 orientation. Scientific model runs remain unchanged. Publication receipt: `reports/technical-review/manifesto-notation-publication.json`.
- **Next step:** None for this release. Preserve its evidence at the requested stopping checkpoint.

### DL-#4427 · Zero-Torque Counterfactual Mechanics and Interpretation

- **State:** shipped
- **Owner:** codex
- **PR:** #4430
- **Issue:** #4427 (Physics #4054; core #4058; corpus #4021; epic #4009)
- **Branch:** `fix/zero-torque-counterfactual-rigor`
- **Paths:** `articles/zero-torque-counterfactual.qmd`, `articles/The_Physics_of_Golf/chapters/ch06_zero_torque_counterfactual.tex`, `articles/The_Physics_of_Golf/quarto/ch06_zero_torque_counterfactual.qmd`, `tests/test_zero_torque_chapter_rigor.py`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (SELF; PR4430 merged as4fe70151 after all required checks; deployment35802860809 succeeded; live artifact10727276644 passes960/960 and eight route cases; c5ed3344 figure correction passes; three obsolete glossary phrase assertions updated and full content_lint selection passes with four documented skips; exact figure census corrected and23 parity tests pass; all eight full-book builds pass; 14 findings/11 evidence paths bound to e7d8c688; 13 dependency carry-forwards at457dbba2; historical discrepancies tracked #4429; 51 targeted tests pass; complete three-source rewrite; 23 scientific/contract checks pass; 128 paired math expressions; nine print pages and 42 web displays inspected; local production 8/8 and expanded overview 4/4 pass)
- **Summary:** Corrects inertia, velocity/gravity bias, coupled inverse recovery, DCR projection, branch/state-reset distinctions, inverse-dynamics double counting and unsupported numerical/physiological claims. Exact rigid fixture unchanged; preparation records scope and access limits.
- **Next step:** Preserve frozen scientific checkpoint e7d8c688 and publication receipt at main4fe70151.

### DL-#4425 · Paired Induced-Acceleration Mechanics and Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4425 (Physics #4054; corpus #4021; epic #4009)
- **PR:** #4426
- **Branch:** `fix/induced-acceleration-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch30b_induced_acceleration.tex`, `articles/The_Physics_of_Golf/quarto/ch30b_induced_acceleration.qmd`, `tests/test_induced_acceleration_chapter_rigor.py`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (SELF; PR4426 merged as99aa5835; deployment35796355561 succeeded with live artifact10725510305,960/960 and four chapter cases pass; CI gravity constant naming corrected without numerical change; all eight full textbook builds and Python3.12 CI pass; complete paired rewrite; 20 numerical checks and 14 attribution contracts pass; 128 matching body expressions; all ten print pages and 18 desktop displays inspected; four production browser cases pass, 139 rendered expressions per case and 11 complete mobile scroll endpoints)
- **Summary:** Print retains claims removed from the web edition. Both need constrained affine baseline and task projection, precise coupling/index normalization, a distinction between integrated terms and interventions, and corrected novelty/literature/anatomy claims. Preparation notes preserve access limits and reproducible examples.
- **Next step:** Preserve the frozen scientific evidence and publication receipt at main 99aa5835.

### DL-#4422 · Putting Launch, Rolling, Slope and Capture

- **State:** shipped
- **Owner:** codex
- **Issue:** #4422 (measurement #4059; corpus #4021; epic #4009)
- **PR:** #4424
- **Branch:** `fix/putting-roll-rigor`
- **Paths:** `articles/putting-roll-models.qmd`, `tests/test_putting_roll_rigor.py`, `data/trust/claim_audit_inventory.json`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (SELF; live publication verified; entire article rewritten; 15 independent mechanics/calibration/capture cases and 18 inventory checks pass; four production browser cases pass with zero serious/critical axe violations; all168 math expressions render in each case; all 28 desktop equations and four tables visually inspected; four expanded cases and every wide scroll endpoint pass)
- **Summary:** Finds missing rotational inertia in slope acceleration, omitted first-order lateral resistance, spinless-only skid assumptions, incorrect V-groove geometry and a false universal capture limit. Primary Penner paper and official USGA sources inform corrections; preparation notes preserve access limits and derivations.
- **Next step:** Publication verified at ded63640 via deployment35792227837 and live artifact10722988337;960/960 and all four putting cases pass. Preserve frozen evidence a17f5ded.

### DL-#4253 - Deferred Impact Evidence Planning

- **State:** shipped
- **Owner:** codex (planning migration)
- **Issue:** #4253
- **Branch:** `docs/deferred-validation-planning`
- **PR:** #4423
- **Paths:** `docs/development/planning/`, `README.md`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (PR #4423 merged 2026-09-22T21:53:38Z as `docs(planning): separate empirical impact evidence from synthesis`; catalog, three heavy-hit controls and 637-file title audit passed in CI.)
- **Summary:** Separates unavailable empirical/perceptual obligations from active qualified theory synthesis. Existing source issues and scientific acceptance criteria are preserved.
- **Next step:** None. PR #4423 merged 2026-09-22; planning docs deployed. Epic #4253 remains open as a deferred impact research item.

### DL-#4420 · Force-Measurement Geometry, Instruments and Inference

- **State:** shipped
- **Owner:** codex
- **Issue:** #4420 (measurement #4059; corpus #4021; epic #4009)
- **PR:** #4421
- **Branch:** `fix/force-measurement-rigor`
- **Paths:** `articles/technology-force-measurement.qmd`, `tests/test_force_measurement_rigor.py`, `data/trust/claim_audit_inventory.json`, `tests/test_claim_audit_inventory.py`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (protected merge9ef76c6e; replacement deployment35789304756 at d9a8d08e succeeded; artifact10721968227 passes all960 live cases, including four force cases with zero overflow/axe failures)
- **Summary:** Corrects both COP height signs, central-axis/free-couple geometry, covariance reasoning, transducer and sampling claims, ASTM standard omission, pressure and bilateral identifiability, study-statistic attribution and causal overclaims. Prior source-only route acceptance is reopened.
- **Next step:** None for this delivery; publication receipt saved separately from frozen scientific evidence. Continue corpus review.


### DL-#4418 · Superposition Feasibility and Constrained Task Authority

- **State:** shipped
- **Owner:** codex
- **Issue:** #4418 (foundations #4058; corpus #4021; epic #4009)
- **PR:** #4419
- **Branch:** `fix/superposition-feasible-inputs`
- **Paths:** `articles/superposition.qmd`, `tests/test_superposition_article_rigor.py`, `data/trust/claim_audit_inventory.json`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (SELF; protected main a6774e33 integrated after exact-tree verification against 7ee71416; final diff excludes prerequisite GRF science; complete article reread;11 independent/existing checks pass; Black100/Ruff/title638 and changed-file quality pass; final four browser cases and416 settled math expressions pass; all21 wide mobile math scrollers reach their endpoint; selected section/equation views inspected)
- **Summary:** Retains earlier mechanics corrections and adds feasible-reference input sets, constrained inverse-mass and task maps, a circular-guide example and correct reaction/virtual-work language. Repairs three wide or spuriously numbered equation groups.
- **Next step:** None for this delivery; deployment 35782578807 succeeded at 31cdc615, live artifact 10720600549 passes 960/960 cases and all four superposition records. Publication evidence: reports/technical-review/superposition-publication.json.

### DL-#4415 · Ground-Reaction Chapter Mechanics and Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4415 (Physics #4054; corpus #4021; epic #4009)
- **PR:** #4417
- **Branch:** `fix/ground-reaction-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch15_ground_reaction_forces.tex`, `articles/The_Physics_of_Golf/quarto/ch15_ground_reaction_forces.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `references/proximal-distal-energy.bib`, `tests/test_ground_reaction_derivations.py`, `data/trust/claim_audit_inventory.json`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (SELF; PR #4417 passed all protected checks and merged as a6774e33; deployment 35779150741 succeeded; downloaded live artifact 10718336671 passes 960/960 cases across 240 routes, and all four GRF route cases pass with zero overflow or serious/critical axe findings; CI quality gate requested GRAVITY_M_S2 naming; test checkpoint8feeaa11 preserves values/equations; SELF fixes the Windows CRLF/committed-LF digest discrepancy and verifies all seven evidence paths against the frozen checkpoint; all29 mechanics/inventory checks and tracked-Python quality gate pass; six findings previously bound to complete checkpoint dfe90fed; final 19 audit/boundary tests pass; source e0ce6133 pushed; 70 mechanics/contract/LaTeX checks and 34 mechanics/inventory checks pass, Black100/Ruff/title638/citations pass; all13 final PDF pages inspected, four public browser cases pass with clean axe, all118 paired math expressions match and render without clipping/errors; metadata-only Chapter16/22 carry-forward verified)
- **Summary:** Reconciles paired system boundaries, momentum signs, COP/free moment, work, input-induced reactions, admissible counterfactuals, muscle inference and human evidence; adds eight worked solutions and corrects three bibliographic author lists from primary records.
- **Next step:** None for this delivery; publication evidence is reports/technical-review/ground-reaction-publication.json.

### DL-#4413 · Physics of Golf Preface Scientific Framing

- **State:** shipped
- **Owner:** codex
- **Issue:** #4413 (Physics #4054; corpus #4021; epic #4009)
- **PR:** #4416
- **Branch:** `fix/physics-preface-rigor`
- **Paths:** `articles/The_Physics_of_Golf/main.tex`, `articles/The_Physics_of_Golf/quarto/index.qmd`, `reports/technical-review/physics-preface-review.md`, `reports/technical-review/physics-preface-render-verification.json`, `data/trust/claim_audit_inventory.json`, `tests/test_claim_audit_inventory.py`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (SELF; protected PR merged, successful successor deployment35774559003 at main581857cb; downloaded live artifact10716514261 passes960/960 cases; all eight anatomy/preface records independently inspected, HTTP200, no page overflow, no serious/critical axe violations; prior scientific/render validation retained in review reports)
- **Summary:** Replaces drift-as-flaccidity, momentum-as-force and unsupported skill/control inference with a shared model-conditioned preface connecting geometry, energy, inputs, task authority and evidence.
- **Next step:** None for this delivery; broader corpus review continues.


### DL-#4412 · Anatomy and Joint Modeling Scientific Review

- **State:** shipped
- **Owner:** codex
- **Issue:** #4412 (Physics #4054; corpus #4021; epic #4009)
- **PR:** #4414
- **Branch:** `fix/technical-review-resume`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch22_anatomy_joint_modeling.tex`, `articles/The_Physics_of_Golf/quarto/ch22_anatomy_joint_modeling.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `tests/test_anatomy_joint_rigor.py`, `tests/test_claim_audit_inventory.py`, `reports/technical-review/anatomy-joint-review.md`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`, `reports/scientific-claim-audit.md`, `docs/development/technical-review/corpus-review-index.csv`
- **Started:** 2026-09-22
- **Last verified:** 2026-09-22 (SELF; protected PR merged, successful successor deployment35774559003 at main581857cb; downloaded live artifact10716514261 passes960/960 cases; all eight anatomy/preface records independently inspected, HTTP200, no page overflow, no serious/critical axe violations; prior scientific/render validation retained in review reports)
- **Summary:** Corrects all identified Chapter 22 geometry, anatomical, work, contact and injury-inference errors, with seven worked exercises and explicit primary-source boundaries. Reopens unsupported prior acceptance; review evidence is bound to 14f1c148. CI exposed two stale figure-census assertions after removing the documented unpaired sketch; the expected counts are corrected without weakening parity checks. Protected successor publication is verified.
- **Next step:** None for this delivery; broader corpus review continues.


### DL-#4406 · Deploy Website Public-Site Verification Gate

- **State:** shipped
- **Owner:** local
- **Issue:** #4406 (fleet-main-health Deploy Website)
- **PR:** #4407
- **Branch:** `fix/issue-4406-deploy-website-local-storage-pageerrors-local`
- **Paths:** `scripts/verify-public-site.js`, `scripts/public-site-browser-noise.js`, `tests/public-site-verifier.test.js`
- **Started:** 2026-09-21
- **Last verified:** 2026-09-21 (PR #4407 merged 2026-09-21T21:47:01Z as `fix(deploy): ignore third-party embed localStorage pageerrors (#4406)`; issue #4406 closed.)
- **Summary:** Ignore non-actionable cross-origin embed pageerrors in the every-page verifier so Deploy Website stays green without weakening first-party regression detection.
- **Next step:** None. PR #4407 merged 2026-09-21; issue #4406 closed.

### DL-#4375 · Curious Golfer Mechanics and Evidence Reasoning

- **State:** shipped
- **Owner:** codex
- **Issue:** #4375 (epic #4009; corpus #4021; foundations #4058)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4377 (regular)
- **Branch:** `fix/4375-curiosity-rigor`
- **Paths:** `articles/proximal_distal_companion/chapters/ch30_curiosity_and_review.qmd`, `reports/technical-review/curiosity-mechanics-review.md`, `reports/technical-review/curiosity-checked-examples.json`, `docs/development/technical-review/curiosity-review.md`, `tests/test_proximal_distal_companion_contract.py`, `data/companion/pins.json`, `models/programming/freshness.qmd`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`
- **Started:** 2026-09-12
- **Last verified:** 2026-09-22 (merge32010d08d9980896c51f0c93ac875f23eb818556; successful exact deployment34730740904; downloaded live artifact10309497076:960/960 cases pass; independently inspected four companion-route records, all HTTP200 with zero overflow and no serious/critical axe violations; prior detailed numerical/render validation retained in technical review reports)
- **Summary:** Corrects acceleration, wrench power and storage, forward versus instantaneous intervention, force-couple limits, numerical convergence and identifiability. Keeps the dialogue and extended examples. New issue4376 records direct-render/web chapter hierarchy drift; the corrected205-page PDF now carries the scientific update in both tracked destinations. No complete-book review or human performance qualification is asserted.
- **Next step:** None for this delivery; broader corpus work continues under #4009/#4021.

### DL-#4376 · Companion Chapter Hierarchy and PDF Synchronization

- **State:** shipped
- **Owner:** codex
- **Issue:** #4376 (epic #4009; companion to #4375)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4377 (regular)
- **Branch:** `fix/4375-curiosity-rigor`
- **Paths:** `scripts/filters/companion-hierarchy.lua`, `tests/test_companion_hierarchy.py`, `articles/proximal-distal-a-journey-through-the-swing.qmd`, `articles/proximal-distal-a-journey-through-the-swing.pdf`, `docs/articles/proximal-distal-a-journey-through-the-swing.pdf`, `articles/proximal-distal-companion.css`, `reports/technical-review/companion-hierarchy-review.md`, `reports/technical-review/companion-hierarchy-verification.json`
- **Started:** 2026-09-13
- **Last verified:** 2026-09-22 (merge32010d08d9980896c51f0c93ac875f23eb818556; successful exact deployment34730740904; downloaded live artifact10309497076:960/960 cases pass; independently inspected four companion-route records, all HTTP200 with zero overflow and no serious/critical axe violations; prior detailed numerical/render validation retained in technical review reports)
- **Summary:** Restores subordinate heading levels without changing chapter prose or incoming anchors. Rebuilds and synchronizes both PDFs with the corrected Chapter30 science. Preserves mobile equation type size. Integrates protected nullspace main squash7f0fed76; retains current turnover records through three documentation conflicts.
- **Next step:** None for this delivery; broader corpus work continues under #4009/#4021.

### DL-#4371 · Constraint Null Spaces, Dynamics and Golf Inference

- **State:** shipped
- **Owner:** codex
- **Issue:** #4371 (epic #4009; corpus #4021; core articles #4058)
- **PR:** #4373 MERGED, regular (https://github.com/D-sorganization/AffineDrift/pull/4373)
- **Branch:** `fix/4371-nullspace-rigor`
- **Paths:** `articles/null-space-constraint-jacobian.qmd`, `articles/null-space-constraint-jacobian-bibliography.qmd`, `references/nullspace-rigor.bib`, `scripts/build_nullspace_examples.py`, `tests/test_nullspace_article_rigor.py`, `reports/technical-review/nullspace-examples.json`, `docs/development/technical-review/nullspace-review.md`, `reports/technical-review/nullspace-complete-review.md`, `reports/technical-review/nullspace-render-verification.json`, `tests/test_check_quarto_render_coverage.py`, `sitemap.xml`, `data/trust/claim_audit_inventory.json`, `tests/test_claim_audit_inventory.py`, `data/trust/generated/claim_audit_report.json`, `reports/scientific-claim-audit.md`
- **Started:** 2026-09-12
- **Last verified:** 2026-09-13 (base a8bd721056f29b236872f025e3d45a6c7d882e94; this checkpoint adds readable math, expanded explanations and the independent gravity constant resolving static CI; root5334 passed/29 skipped/132 deselected/59 warnings in193.45s, coverage79.29%; focused16/Ruff/Black pass;735 tracked Python files have zero static findings; rendered209 expressions/46 displays,14 width/theme cases,184 regions and46 keyboard scroll checks pass; supplemental callouts/tables/bibliography checks pass; all29 final article images and six bibliography images per theme read; actual production gate28/28 pass with two route-level axe scans; durable reports added after seven source/example files matched committed1cfa47d45ebd14c719c0ec981e83eb53a231fb4d; durable reports committed783254f3815b82d147c77d48ff449b48613497fa; live bibliography404 exposed absent default render target; byte-identical companion renamed to QMD under existing render rules; actual-selection regression passes after RED; shared config and its bound audits preserved; reviews bound to75cf41fcba74cbf686863a2f8c701788d4db561c with nine independently checked files; all other route records unchanged; focused43 checks pass; QMD rerender preserves full main text, links and IDs; full-root publication run5335/79.29% in192.62s passed before binding; final bound-root5335 passed/29 skipped/132 deselected/59 warnings in191.85s, coverage79.29%;735 tracked Python files and637 titles pass; exact-head47b637ae reference CI failed missing Related Articles on new companion; three contextual links added; actual site gate/43 focused tests pass; render24560 and settled mobile light/dark inspection pass; all nine evidence paths independently verified against fdd6effabcb6f955d2d18bc2587e1208c4cddcd2 and both reviews rebound; latest repaired root5335 passed/29 skipped/132 deselected/59 warnings in188.68s, coverage79.29%; second hosted failure was missing sitemap entry, now added with all239 earlier entries unchanged; bidirectional coverage240 and complete site gate pass; all15 exact-head checks passed; protected squash7f0fed760f3e1d45610f5612c900ed4c67c49302 merged2026-09-13T00:16:11Z; exact deployment34727537466 succeeded; artifact10309086348 individually verifies all960 unique cases across240 routes, including8 nullspace article/bibliography cases; all HTTP200/pass with no failures/overflow/retries;240 actual route-level axe scans have zero serious/critical findings)
- **Summary:** Rewrites the full article and bibliography around regular constraints, reduced speeds, force/velocity duality, curvature-complete drift, task acceleration, reaction power and finite-time control. Replaces inconsistent golf coordinates with a declared planar mechanism and removes unsupported synergy/coaching claims and citation-graph edges. Independent examples are constructed, not fitted golfer data.
- **Next step:** Continue corpus review; separate shared TOC and keyboard defects remain #4370/#4374.

### DL-#1595 · Mermaid C4 Architecture Map Contract

- **State:** shipped
- **Owner:** local
- **Issue:** D-sorganization/Repository_Management#1595 (epic #1594)
- **PR:** #4363
- **Branch:** `feat/1595-c4-architecture-map`
- **Paths:** `docs/architecture/C4.md`, `scripts/architecture_map_contract.py`, `tests/test_architecture_map_contract.py`, `.github/workflows/architecture-map-contract.yml`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (PR #4363 merged as `docs(architecture): adopt maintainable Mermaid C4 architecture-map contract (#1595)`; SPEC.md change log row added 2026-09-10 #4363.)
- **Summary:** Adopts the maintainable Mermaid C4 architecture-map contract for AffineDrift, providing C4Context, C4Container, Feature Map, and Architecture Change Log.
- **Next step:** None. PR #4363 merged; RM#1595 addressed.

### DL-#4369 · Muscle Geometry, Torque Feasibility and Inference

- **State:** shipped
- **Owner:** codex
- **Issue:** #4369 (epic #4009; corpus #4021)
- **PR:** #4372 MERGED (https://github.com/D-sorganization/AffineDrift/pull/4372), regular; squash `3f87332512858febf2c131fbda44b62acad8d222`
- **Branch:** `fix/4369-muscle-torque-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch16_muscle_to_joint_torques.tex`, `articles/The_Physics_of_Golf/quarto/ch16_muscle_to_joint_torques.qmd`, `docs/development/technical-review/muscle-torque-review.md`, `tests/test_muscle_torque_rigor.py`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/figures/muscle_torque_feasibility.svg`, `articles/The_Physics_of_Golf/figures/muscle_torque_feasibility.pdf`, `scripts/build_muscle_torque_figures.py`, `tests/test_audit_quarto_figure_parity.py`, `reports/technical-review/muscle-torque-complete-review.md`, `reports/technical-review/muscle-torque-render-verification.json`, `data/trust/claim_audit_inventory.json`, `tests/test_claim_audit_inventory.py`, `data/trust/generated/claim_audit_report.json`, `reports/scientific-claim-audit.md`
- **Started:** 2026-09-12
- **Last verified:** 2026-09-12 (`a2d482bff6252be13cbced65cddb3b3f353027ac` relocated implementation and all nine evidence paths independently verified from git; inventory bound with four corrected scientific findings and one open TOC finding;50 combined tests pass after partition RED-to-GREEN; all29 web captures,15 chapter pages and4 bibliography pages read; all14 production-route records individually pass; Ruff/Black706/mypy91/title636 pass; previous delivery root5318/79.35%; bound-root failed deployment-output evidence survival only (5317 passed); moved figure builder into scripts and51 focused checks pass; exact SVG drawing and identical PDF pixels verified; direct builder mypy passes; final repaired root5318 passed/29 skipped/132 deselected in187.39s; coverage79.21% verified against the saved log; protected squash3f87332512858febf2c131fbda44b62acad8d222 completed, exact deployment34722147597 succeeded; all956 live records across239 routes individually verified HTTP200/pass with no failures/overflow/retries; all four Chapter16 configurations pass; artifact10306629143;239 route-level axe scans have zero serious/critical violations; TOC defect tracked separately in #4370; regular PR4372 opened and SPEC row recorded)
- **Summary:** Rewrites both editions and all11 exercise answers around signed virtual work, feasible force sharing, coupled coordinates, stiffness and power. Adds a checked feasibility/power figure and four primary-source bibliography entries. Removes unsupported anatomical/grip prescriptions and separates inverse estimates, calibration, recruitment and control hypotheses. Preserves original destinations.
- **Next step:** Address the separate TOC highlighting defect in #4370.

### DL-#4358 · Strokes-Gained Accounting and Individual Inference

- **State:** shipped
- **Owner:** codex
- **Issue:** #4358 (epic #4009; corpus #4021; applied routes #4059)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4368 (regular follow-up; #4360 previously merged)
- **Branch:** `fix/4358-strokes-delivery`
- **Paths:** `articles/strokes-gained-limitations.qmd`, `articles/strokes-gained-limitations-bibliography.md`, `critiques/strokes_gained_non_ergodic.md`, `references/strokes-gained-rigor.bib`, `css/strokes-gained.css`, `tests/test_strokes_gained_article_rigor.py`, `docs/development/technical-review/strokes-gained-review.md`, `scripts/build_strokes_gained_examples.py`, `reports/technical-review/strokes-gained-numerics.json`, `reports/technical-review/strokes-render-verification.json`, `reports/technical-review/strokes-complete-review.md`, `scripts/claim_audit_evidence.py`, `tests/test_claim_audit_markdown_sources.py`, `tests/test_claim_audit_inventory.py`, `data/trust/claim_audit_inventory.json`, `.prettierignore`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-12 (`93bbfd29d3e69147dedef153749a47a1b650dfe9`; protected PR4368 merge and exact deployment34717587828 succeeded; live artifact10305443224 independently checked: all956 unique records/239 routes HTTP200/pass, no record/inspection failures, overflow, retries or axe violations; numerical repair713a4ca5 and bound evidence retained)
- **Summary:** Corrects accounting and individual inference, including joint shot-cost/distribution/continuation effects and attribution-order dependence. Resumed after PR4360 merged without its pending rendered audit; repairs reference/panel dark contrast and invisible expanded text. All future PRs regular. Governed critique remains open; both route reviews now bind complete review evidence outside generated docs output, with Markdown-source support matching publication precedence.
- **Next step:** Preserve the published sources and bound review while continuing the corpus audit.

### DL-#4355 · Complete Forces, Torques and Physical Attribution

- **State:** shipped
- **Owner:** codex
- **Issue:** #4355 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4357 (merged; published)
- **Branch:** `fix/4355-forces-torques-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch04_forces_and_torques.tex`, `articles/The_Physics_of_Golf/quarto/ch04_forces_and_torques.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/main.pdf`, `articles/The_Physics_of_Golf/figures/forces_torques_verified.*`, `tests/test_forces_torques_chapter_rigor.py`, `tests/test_audit_quarto_figure_parity.py`, `docs/development/technical-review/forces-torques-review.md`, `docs/development/technical-review/build_forces_torques_figures.py`, `docs/development/technical-review/forces-torques-numerics.json`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`0c753400190cf330533bffc12e9b035162f37749`; exact deployment34477888759 succeeded; independently inspected all956 records/239 routes in artifact10153444359, all HTTP200/pass, no record/inspection failures, retries or axe violations)
- **Summary:** Rebuilds physical and generalized load attribution, moving-frame signs, gravity work, muscle-state and contact feasibility, whole-club grip wrench and segment power. Independent Newton–Euler and energy checks support a declared two-link example and seven worked answers. Full audit records derivations, source limits and validation failure history.
- **Next step:** None for this chapter; preserve the complete audit.

### DL-#4353 · Complete Double-Pendulum Derivation and Task Mechanics

- **State:** shipped
- **Owner:** codex
- **Issue:** #4353 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4354 (merged; published through verified descendant)
- **Branch:** `fix/4353-double-pendulum-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch03_double_pendulum.tex`, `articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/main.pdf`, `articles/The_Physics_of_Golf/figures/double_pendulum_verified.*`, `tests/test_double_pendulum_chapter_rigor.py`, `tests/test_audit_quarto_figure_parity.py`, `docs/development/technical-review/double-pendulum-review.md`, `docs/development/technical-review/build_double_pendulum_figures.py`, `docs/development/technical-review/double-pendulum-numerics.json`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`0c753400190cf330533bffc12e9b035162f37749`; published descendant of e9ad402e with both Chapter3 sources unchanged; deployment34477888759/artifact10153444359 all956/239 individually verified; original exact run34473831404 was cancelled when superseded)
- **Summary:** Corrects COM versus hinge inertia, gravity signs, Coriolis rate factors, coupled input response, physical interface power and endpoint curvature. Six worked answers and primary-source boundaries distinguish anatomical interpretation, task sensitivity and chaos. Audit records independent derivations, numerical checks and rendering defects found by complete reading.
- **Next step:** None for this chapter; preserve its derivation audit and cancellation history.

### DL-#4351 · Complete Constraint Forces, Compatible Dynamics and Power

- **State:** shipped
- **Owner:** codex
- **Issue:** #4351 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4352 (merged; published)
- **Branch:** `fix/4351-constraint-forces-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch07_constraint_forces.tex`, `articles/The_Physics_of_Golf/quarto/ch07_constraint_forces.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/main.pdf`, `articles/The_Physics_of_Golf/figures/constraint_forces_verified.*`, `tests/test_constraint_forces_rigor.py`, `tests/test_physics_of_golf_glossary.py`, `tests/test_audit_quarto_figure_parity.py`, `docs/development/technical-review/constraint-forces-review.md`, `docs/development/technical-review/build_constraint_forces_figures.py`, `docs/development/technical-review/constraint-forces-numerics.json`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`b5362af0005c8ae1ad00e81390e9151991157155`; exact deployment 34470677053 succeeded; all 956 records/239 routes in artifact 10150223079 independently inspected, HTTP 200/pass and no failures/retries or axe violations)
- **Summary:** Rebuilds acceleration compatibility, rank/scaling, mass-metric projection, moving-contact power, physical segment energy, actuation/reaction coupling and plastic capture/release. Six worked answers and independently checked examples distinguish mechanical coupling from muscle and coaching inference. Full audit preserves derivation and evidence limits.
- **Next step:** None for this chapter; preserve its audit and continue corpus review.

### DL-#4349 · Complete Affine Structure, Drift and Optimality

- **State:** shipped
- **Owner:** codex
- **Issue:** #4349 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4350 (merged; published)
- **Branch:** `fix/4349-affine-structure-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch05_affine_structure.tex`, `articles/The_Physics_of_Golf/quarto/ch05_affine_structure.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/main.pdf`, `articles/The_Physics_of_Golf/figures/affine_structure_verified.*`, `tests/test_affine_structure_rigor.py`, `tests/test_audit_quarto_figure_parity.py`, `docs/development/technical-review/affine-structure-review.md`, `docs/development/technical-review/build_affine_structure_figures.py`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`60d0298826880ca24580908127e8032565407216`; exact deployment 34466267456 succeeded; all 956 records/239 routes in artifact 10148726944 independently inspected, HTTP 200 and pass with no failures/retries or axe violations)
- **Summary:** Re-derives complete coupled drift, inverse inertia and constrained vector fields; separates capacity, realized input, energy and finite-time task authority. Seven worked answers and a reproduced figure replace unsupported phase/optimality claims. Full print/web reading corrected conversion defects missed by layout checks; all 30 historical web destinations now verified. The audit records source limits, numerical derivations and failure history.
- **Next step:** None for this chapter; preserve audit and continue corpus review.

### DL-#4347 · Complete Brain Control and Neuroscience Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4347 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4348 (merged; published)
- **Branch:** `fix/4347-brain-control-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch24_motor_control_brain.tex`, `articles/The_Physics_of_Golf/quarto/ch24_motor_control_brain.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/main.pdf`, `articles/The_Physics_of_Golf/figures/brain_control_verified.*`, `tests/test_brain_control_rigor.py`, `tests/test_audit_quarto_figure_parity.py`, `docs/development/technical-review/brain-control-review.md`, `docs/development/technical-review/build_brain_control_figures.py`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`688dda81c3f0c38759d9994cbc0d5c0cd0478bd2`; exact deployment 34460868604 succeeded; independently inspected all 956 records/239 routes in artifact 10146654751, no failures/retries or axe violations)
- **Summary:** Corrects prediction/inverse dimensions, torque versus neural inputs, delayed observations, activation and finite-horizon/event response. Replaces unsupported neural algorithms, timing/noise constants and coaching conclusions with bounded primary evidence. Ten worked answers and shared functional/activation figure connect mechanics, observation, actuation, learning and task uncertainty. Audit records derivations, failures and exact reading limits.
- **Next step:** Retain the verified brain-control source and evidence during subsequent chapter reviews.

### DL-#4345 · Complete Triple-Pendulum Dynamics and Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4345 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4346 (merged and published)
- **Branch:** `fix/4345-triple-pendulum-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch08_triple_pendulum.tex`, `articles/The_Physics_of_Golf/quarto/ch08_triple_pendulum.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/figures/triple_pendulum_verified.*`, `articles/The_Physics_of_Golf/main.pdf`, `tests/test_triple_pendulum_rigor.py`, `tests/test_ch08_triple_pendulum_mass_matrix.py`, `docs/development/technical-review/triple-pendulum-review.md`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`8808f68ab8b7e39c5110ce260473d02dbff63c45`, successful deploy 34456863592; all 956 live records / 239 routes in artifact 10144974541 independently inspected with no failures or retries)
- **Summary:** Defines one consistent planar model, derives complete inertia and Christoffel bias, computes a converged zero-torque counterexample and ideal lock release, separates segment power from local actuation, and bounds wrist-control claims with primary evidence. Six worked answers and historical destinations are preserved. Derivation and failure history are recorded in the audit.
- **Next step:** Retain the published derivation while reviewing the remaining constraint and affine chapters.


### DL-#4342 · Durable Claim-Review Evidence Through Deployment

- **State:** shipped
- **Owner:** codex
- **Issue:** #4342 (epic #4009; corpus #4021)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4344 (merged; verified in published successor 8808f68a)
- **Branch:** `fix/4341-fascia-mechanics-rigor`
- **Paths:** `reports/technical-review/dcr-complete-review.md`, `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`, `tests/test_claim_audit_output_boundary.py`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`8808f68ab8b7e39c5110ce260473d02dbff63c45`, successful deploy 34456863592; all 956 live records / 239 routes in artifact 10144974541 independently inspected with no failures or retries) Retained fascia sources/figure, DCR article/bound review/inventory and pruning test are byte-identical between 0e30c134 and this successor.
- **Summary:** Quarto output pruning removed the DCR review because it was stored under docs/. Move durable bound evidence to reports/technical-review, update references/digests and enforce survival of actual pruning for every reviewed route. Scientific authority and publication gates remain intact.
- **Next step:** Continue the remaining corpus review, including companion DCR critiques #4340.

### DL-#4341 · Fascia Mechanics and Biological Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4341 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4344 (merged; verified in published successor 8808f68a)
- **Branch:** `fix/4341-fascia-mechanics-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch12_fascia.tex`, `articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/figures/fascia_viscoelastic_memory.*`, `articles/The_Physics_of_Golf/main.pdf`, `tests/test_fascia_mechanics_rigor.py`, `tests/test_physics_of_golf_pdf_contract.py`, `tests/test_audit_quarto_figure_parity.py`, `docs/development/technical-review/fascia-mechanics-review.md`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`8808f68ab8b7e39c5110ce260473d02dbff63c45`, successful deploy 34456863592; all 956 live records / 239 routes in artifact 10144974541 independently inspected with no failures or retries) Retained fascia sources/figure, DCR article/bound review/inventory and pruning test are byte-identical between 0e30c134 and this successor.
- **Summary:** Replaces the complete paired chapter with explicit force/power/energy distinctions, correct SI examples, nonlinear and viscoelastic derivations, directional coupling, augmented control/sensing states and bounded primary evidence. Eight worked answers and a shared reproducible figure preserve historical links. Corrects the legacy regression that preserved the erroneous 1.25 J calculation. Source boundaries, failures and validation are documented. Companion DCR critiques remain separately queued as #4340.
- **Next step:** Continue the remaining corpus review, including companion DCR critiques #4340.

### DL-#4338 · DCR Scaling, Coordinates and Correction Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4338 (epic #4009; corpus #4021)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4339 (merged; verified in published successor 8808f68a)
- **Branch:** `fix/4338-dcr-complete-rigor`
- **Paths:** `articles/drift-control-ratio.qmd`, `tests/test_dcr_article_rigor.py`, `tests/test_scientific_trust_metadata.py`, `src/affine_control/research_readiness/fixtures.py`, `data/research_protocols`, `data/trust/claim_audit_inventory.json`, `reports/technical-review/dcr-complete-review.md`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`8808f68ab8b7e39c5110ce260473d02dbff63c45`, successful deploy 34456863592; all 956 live records / 239 routes in artifact 10144974541 independently inspected with no failures or retries) Retained fascia sources/figure, DCR article/bound review/inventory and pruning test are byte-identical between 0e30c134 and this successor.
- **Summary:** Complete replacement withdraws unsupported downswing growth and derives scaling, coordinate Hessians, transported metrics, regularization, finite-time reachability and event sensitivity. Thirteen independent tests support the argument. Readiness now names the actual route reviewer with coherent manufactured chronology; scientific protocol states and immutable authority pins remain unchanged. Full reading, mobile/table/disclosure QA, content, static, titles, links, style and types pass. Initial digest/date failures and visually detected dark-panel defect were corrected and documented. Companion critiques and remaining corpus stay open.
- **Next step:** Continue the remaining corpus review, including companion DCR critiques #4340.

### DL-#4336 · Passive Impedance, Distributed Feedback and Stability

- **State:** shipped
- **Owner:** codex
- **Issue:** #4336 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4337 (merged)
- **Branch:** `fix/4336-passive-impedance-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch27_passive_distributed_control.tex`, `articles/The_Physics_of_Golf/quarto/ch27_passive_distributed_control.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/figures/passive_damping_regimes.svg`, `articles/The_Physics_of_Golf/figures/passive_damping_regimes.pdf`, `tests/test_passive_distributed_control_rigor.py`, `docs/development/technical-review/passive-distributed-control-review.md`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`a1ef3f22ce38d148064b0c0b5c29c6db30f46168`, protected squash; exact deploy 34441497877 succeeded; all 956 live records / 239 routes in artifact 10138837491 independently verified)
- **Summary:** Complete paired correction connects intrinsic mechanics, maintained activation, distributed feedback, input counterfactuals, energy and finite-time outcomes. Proper storage/tracking proofs, independently checked damping/delay examples, one reproducible figure and all 12 worked answers. Final tests-directory run 5,111 passes, 92.68% coverage; focused 36, content 131, 34 static contracts, title/style/type/link and complete affected PDF/web QA pass. Protected merge and exact publication verified without retries or serious/critical accessibility findings. Peer impact work and immutable publication excluded.
- **Next step:** Retain this published derivation as a cross-reference during the remaining corpus review.

### DL-#4333 · Flexible Shaft Dynamics and Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4333 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4335 (merged and published)
- **Branch:** `fix/4333-flexible-shaft-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch11_flexible_shaft.tex`, `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd`, `docs/development/technical-review/flexible-shaft-review.md`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`de57acae49ea206d0232ecf4de8a7f9cd0b5da03`, exact live artifact 10137269737; all 956 records / 239 routes passed)
- **Summary:** Both editions corrected with beam assumptions, modal normalization, coupled input mechanics, energy accounting and bounded fitting evidence; two reproducible figures and six worked answers. Root 5,143 passes / 29 skips; content, 34 static contracts, 636 title checks, style/type/link checks and complete affected print/web QA pass. Protected deploy 34437073824 passed; all live records and 239 axe routes passed without failures/retries. Peer impact/acoustic work and immutable publication excluded.
- **Next step:** Complete; continue the corpus review.

### DL-#4331 · Muscle Force Models, Tendon Energy and Control Inference

- **State:** shipped
- **Owner:** codex
- **Issue:** #4331 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4332 (merged and published)
- **Branch:** `fix/4331-muscle-force-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch17_muscle_force_generation.tex`, `articles/The_Physics_of_Golf/quarto/ch17_muscle_force_generation.qmd`, `articles/The_Physics_of_Golf/golf_physics.bib`, `docs/development/technical-review/muscle-force-review.md`
- **Started:** 2026-09-10
- **Last verified:** 2026-09-10 (`a81f99c06c34d3a98ad215a26218537861e49d1a`, exact live artifact 10135966540; all 956 records / 239 routes passed)
- **Summary:** Both editions now connect muscle architecture, force curves, activation, tendon energy and joint/control mechanics through bounded evidence, independent examples, two figures and seven worked answers. Root 5,131 passes, 79.2% coverage; final affected, content, static, style/type/link and complete print/web QA pass. Initial conversion/manifest failures and evidence limits are documented.
- **Next step:** Complete; continue corpus review. Original deployment was cancelled; descendant deploy 34433303512 succeeded with exact live verification.

### DL-#4326 · Motor Learning, Sensory Prediction and Practice Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4326 (epic #4009; corpus #4021; Physics #4054)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4330 (merged)
- **Branch:** `fix/4326-motor-learning-rigor`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch25_motor_learning.tex`, `articles/The_Physics_of_Golf/quarto/ch25_motor_learning.qmd`, `docs/development/technical-review/motor-learning-review.md`
- **Started:** 2026-09-09
- **Last verified:** 2026-09-10 (`8c383f9cfb46cc19be832ce81e8fe356279c29c7`, protected merge and exact production artifact 10133005315)
- **Summary:** Complete paired correction connects mechanics, feel, prediction and practice through bounded primary evidence, independent examples, two shared figures and twelve worked answers. Root 5,118 passes at 79.19% coverage; final focused 44, content 130, static 34, style/type/link checks and complete affected PDF/web QA pass. Protected main/deployment checks pass; all 956 exact live records across 239 routes pass with no serious/critical axe findings or navigation retries.
- **Next step:** Continue the adjacent computational-brain chapter audit under the corpus epic.

### DL-#4327 · Nonlinear Control Explanation Publication Repair

- **State:** shipped
- **Owner:** codex
- **Issue:** #4327 (epic #4009; corpus #4021)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4329 (merged)
- **Branch:** `fix/4327-nonlinear-callouts`
- **Paths:** `articles/nonlinear-control-insights.qmd`, `css/technical-explanations.css`, `docs/development/technical-review/nonlinear-callouts-review.md`
- **Started:** 2026-09-09
- **Last verified:** 2026-09-10 (`1fe7997eba9d7059dc9b68582643653cee0ec2d0`, protected merge and all 956 records of exact live artifact 10131240380)
- **Summary:** Exact rotation deployment artifact identifies malformed nonlinear-control explanation HTML as a publication blocker. Native disclosures replace escaped markup and unsupported muscle-work, torso-stop and validation claims. Root 5,097 tests pass at79.19%coverage; final content130/static34 and12expanded keyboard/theme cases pass. The article is only partially reviewed.
- **Next step:** Continue the remaining corpus review under epic #4009.

### DL-#4324 · Motion Capture, Uncertainty and Scientific Interpretation

- **State:** shipped
- **Owner:** codex
- **Issue:** #4324 (epic #4009; corpus #4021)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4325 (merged)
- **Branch:** `fix/4324-motion-capture-rigor`
- **Paths:** `articles/technology-motion-capture.qmd`, `tests/test_motion_capture_rigor.py`, `docs/development/technical-review/motion-capture-review.md`
- **Started:** 2026-09-09
- **Last verified:** 2026-09-10 (`4cf3514dc82a6c267f43df39a89b57247cc0ba27`, published descendant; all 956 records of exact live artifact 10130399466)
- **Summary:** Complete article review connects camera geometry, anatomy, timing, conventions and correlated uncertainty to defensible golf-mechanics inference. Bounded primary claims replace categorical accuracy and energy assertions. Root 5,097 passes, 79.19% coverage; final focused 19, content 130, static 34, style/type/link checks and complete bounded web QA pass. Native Quarto explanation expands visibly.
- **Next step:** Continue the remaining corpus review under epic #4009.

### DL-#4322 · Rotation Conventions, Stable Conversion and Golf Interpretation

- **State:** shipped
- **Owner:** codex
- **Issue:** #4322 (epic #4009; corpus #4021)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4323 (merged)
- **Branch:** `fix/4322-rotation-converter-reference`
- **Paths:** `articles/rotation-converter.qmd`, `articles/rotation-representations-reference.qmd`, `js/rotation-converter.js`, `js/rotation-converter-ui.js`, `js/rotation-converter-viz.js`, `css/rotation-converter.css`, `scripts/sync_frontend_assets.py`, `src/tools/rotation_reference_examples.py`, `tests/test_rotation_representations_reference.py`, `tests/test_rotation_reference_kinematics.py`, `tests/rotation-converter-rigor.test.js`, `tests/rotation-converter-ui.test.js`, `docs/development/technical-review/rotation-converter-review.md`
- **Started:** 2026-09-09
- **Last verified:** 2026-09-10 (`4cf3514dc82a6c267f43df39a89b57247cc0ba27`, published descendant; all 956 records of exact live artifact 10130399466)
- **Summary:** Both complete articles derive stable boundary conversions and connect calibrated orientation, angular velocity, face sensitivity, uncertainty and physical work. Converter rejects malformed inputs, preserves labeled prior results and supports optional-3D failure. Root 5,078 passes, 79.19% coverage; final numerical/UI/content/static/style/type/link checks and complete bounded web QA pass.
- **Next step:** Continue the remaining corpus review under epic #4009.

### DL-#4320 · Textbook Energy Transfer and Work Ledgers

- **State:** shipped
- **Owner:** codex
- **Issue:** #4320 (epic #4009)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4321 (merged)
- **Branch:** `fix/4320-textbook-energy-transfer`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch10_energy_transfer.tex`, `articles/The_Physics_of_Golf/quarto/ch10_energy_transfer.qmd`, `src/tools/energy_ledger_examples.py`, `tests/test_textbook_energy_ledger_rigor.py`, `docs/development/technical-review/energy-chapter-review.md`
- **Started:** 2026-09-09
- **Last verified:** 2026-09-09 (`4aea9755711b462498d8cddae531dab3131f5989`)
- **Summary:** Both complete editions now derive consistent whole-system, physical segment and interface ledgers, full two-link dynamics, lag/elasticity and collision boundaries. Two shared figures and six worked answers have independent numerical verification. Root 5,061 passes, 79.17% coverage; all final affected/content/static/title/style/type/quality/link checks and complete bounded print/web QA pass.
- **Next step:** Continue the corpus review; exact live artifact 10126445934 verifies energy publication (956/956 records, 239 routes, no failures or serious/critical axe findings).

### DL-#4318 · Spatial Algebra, Physical Inertia and Recursive Dynamics

- **State:** shipped
- **Owner:** codex
- **Issue:** #4318 (epic #4009)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4319 (merged)
- **Branch:** `fix/4318-spatial-algebra`
- **Paths:** `articles/The_Geometry_of_Motion/Volume_0/chapters/ch08_spatial_algebra.tex`, `articles/The_Geometry_of_Motion/quarto/vol0_ch08_spatial_algebra.qmd`, `articles/The_Geometry_of_Motion/figures/spatial_*`, `articles/The_Geometry_of_Motion/geometry_of_motion.bib`, `articles/The_Geometry_of_Motion/Volume_0/main.pdf`, `src/affine_control/dynamics.py`, `src/tools/spatial_inertia_examples.py`, `tests/test_spatial_algebra_rigor.py`, `docs/development/technical-review/spatial-algebra-review.md`
- **Started:** 2026-09-09
- **Last verified:** 2026-09-09 (`c4c1fee6db8915eee49a80b3572ece9ccfe57cd5`)
- **Summary:** Complete paired correction connects frame/power duality, physical inertia, momentum derivatives, planar restriction, composite/joint inertia and constraints. Two figures, fifteen worked answers and shared routines have independent numerical checks. Root 5,050 passes, 79.14% coverage; final affected 37, content 130, static 34, titles 634, style/type/quality/link and complete affected print/web QA pass. Implementation was replayed alone onto protected main b6578132 before first push; all normal commit/push hooks pass.
- **Next step:** Continue the remaining corpus under epic #4009; spatial delivery is verified by live artifact 10123816915 (956/956, 239 routes, zero failures or serious/critical axe findings).

### DL-#4315 · Soft-Tissue Dynamics and Pressure Mechanics

- **State:** shipped
- **Owner:** codex
- **Issue:** #4315 (epic #4009)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4317 (merged)
- **Branch:** `fix/4315-soft-tissue-mechanics`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch20_soft_tissue_pliable.tex`, `articles/The_Physics_of_Golf/quarto/ch20_soft_tissue_pliable.qmd`, `articles/The_Physics_of_Golf/figures/soft_tissue_*`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/main.pdf`, `tests/test_soft_tissue_mechanics_rigor.py`, `docs/development/technical-review/soft-tissue-review.md`
- **Started:** 2026-09-09
- **Last verified:** 2026-09-09 (`b657813291e89def6269d9bb0f258a9e26c3dd8a`)
- **Summary:** Both editions now derive consistent tissue, pressure, inertia and energy models with bounded primary evidence, two shared figures and seven worked answers. Regression passes 4,991 tests with 92.65% coverage; final affected, content, static, style, type, title and site-link checks pass. Complete print/web inspection includes accessible math and corrected exercise numbering.
- **Next step:** Published: main CI 34393037135, textbooks 34393037136, performance 34393037120 and deployment 34393037121 pass. Downloaded exact live artifact 10121457373 passes all 956 records across 239 routes, with zero failures, serious/critical axe findings or retries. Continue the remaining corpus.

### DL-#4313 · Interdisciplinary Golf Synthesis and Evidence

- **State:** shipped
- **Owner:** codex
- **Issue:** #4313 (epic #4009)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4314 (merged)
- **Branch:** `fix/4313-interdisciplinary-synthesis`
- **Paths:** `articles/The_Physics_of_Golf/chapters/ch13_interdisciplinary.tex`, `articles/The_Physics_of_Golf/quarto/ch13_interdisciplinary.qmd`, `articles/The_Physics_of_Golf/figures/interdisciplinary_*`, `articles/The_Physics_of_Golf/golf_physics.bib`, `articles/The_Physics_of_Golf/main.pdf`, `css/interdisciplinary-synthesis.css`, `tests/test_interdisciplinary_synthesis_rigor.py`, `tests/test_audit_quarto_figure_parity.py`, `docs/development/technical-review/interdisciplinary-review.md`, `docs/development/technical-review/build_interdisciplinary_figures.py`
- **Started:** 2026-09-09
- **Last verified:** 2026-09-09 (`fc76f2e1d214fd66101e616ae94fce6d31d6af26`)
- **Summary:** Both editions now connect mechanics, finite-horizon control, impedance, materials, impact and evidence using independently checked examples, two figures and eight worked answers. Local regression passes 4,974 tests with 92.65% coverage; complete affected print/web review and all normal hooks pass.
- **Next step:** Published: main CI, textbooks, performance and deployment pass. Exact artifact 10119982807 passes 956/956 records across 239 routes with zero failures, serious/critical axe findings or retries. Continue the remaining corpus; no further delivery work for this batch.

### DL-#3904 · Series navigation and tangent-space cluster integration

- **State:** shipped
- **Owner:** claude (wave-8 agent W8_3904)
- **Issue:** `#3904` (epic `#3896`)
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4271 (merged)
- **Branch:** `claude/issue-3904-series-nav`
- **Paths:** `_quarto.yml`, `pages/tangent-hyperplanes.qmd`,
  `articles/superposition.qmd`,
  `articles/null-space-constraint-jacobian.qmd`,
  `articles/force-mobility-matrices.qmd`,
  `articles/degrees-of-freedom-and-dimensionality.qmd`,
  `articles/tangent-hyperplanes-series/part-*.qmd`,
  `articles/theory-part5.qmd`, `articles/appendix-applications.qmd`,
  `articles/affine-nature-golf-swing.qmd`, `tests/test_series_navigation.py`
- **Started:** 2026-09-08
- **Last verified:** 2026-09-28 (`c088f9d0`)
- **Summary:** Added three series sidebar groups (theory, tangent-space,
  Geometry of Motion volumes) for prev/next and breadcrumbs; wired the four
  isolated geometry articles into the tangent-space cluster with the canonical
  Related Articles component and hub-side companion links; added return links
  from tangent parts 1–7; chained appendix-applications and
  affine-nature-golf-swing into the theory sequence. Contract test:
  60 passed. All relative link targets verified to exist.
- **Next step:** No further delivery work for this batch; PR #4271 merged as
  `c088f9d0`.

### DL-0035 · Impact Dynamics and Acoustics Review

- **State:** shipped
- **Owner:** codex
- **Issue:** https://github.com/D-sorganization/AffineDrift/issues/4255; parent4253; initial4254/4258 merged
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4356 (merged)
- **Branch:** docs/4255-impact-handoff
- **Paths:** `articles/_includes/impact-acoustics.qmd`, `references/impact-acoustics.bib`, `docs/development/impact-acoustics/`, SPEC and turnover
- **Started:** 2026-09-07
- **Last verified:** 2026-09-10 (963867d7c78e544799ef4b6070eb1779e64c0452; turnover SELF): PR4356 merged after all 15 checks passed, including full-site browser/accessibility qualification. Original local receipts remain source-identified in FORCE_REGULARITY_RESULTS.json.
- **Summary:** Extends the existing theory with contact-force regularity, finite-jump versus impulse, spectral-tail derivation and externally forced candidate-law limits; retains source-identified synthetic status and distinct physical/radiation/perception requirements.
- **Next step:** Resume open #4255 evidence-gated synthesis after reviewed Tools/consumer results; canonical HANDOFF records the checkpoint and outstanding physical/acoustic work.

### DL-0001 · Audit Quality Fixes

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`ff8f89c2`)
- **Summary:** Seeded from local branch `audit/quality-fixes`, which is
  6 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0002 · Audit Webux Fixes

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`a8de0549`)
- **Summary:** Seeded from local branch `audit/webux-fixes`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0003 · Codex Fix Back To Top E2E

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`5ecf36da`)
- **Summary:** Seeded from local branch `codex/fix-back-to-top-e2e`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0004 · Codex Fix Deploy Runner Picker

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`e7e1052f`)
- **Summary:** Seeded from local branch `codex/fix-deploy-runner-picker`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0005 · Codex Fix Image Derivatives Main

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`eeaf1963`)
- **Summary:** Seeded from local branch `codex/fix-image-derivatives-main`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0006 · Codex Fix Local Guard Trigger

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`0e355770`)
- **Summary:** Seeded from local branch `codex/fix-local-guard-trigger`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0007 · Codex Issue 3230 Remaining Tests

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`8e0a1008`)
- **Summary:** Seeded from local branch `codex/issue-3230-remaining-tests`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0008 · Codex Issue 3230 Script Tests

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`0a826c32`)
- **Summary:** Seeded from local branch `codex/issue-3230-script-tests`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0009 · Codex Issue 3254 Sw Precache Cleanup

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`059a8608`)
- **Summary:** Seeded from local branch `codex/issue-3254-sw-precache-cleanup`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0010 · Codex Pr 3096 Accordion Aria

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`34fe1e83`)
- **Summary:** Seeded from local branch `codex/pr-3096-accordion-aria`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0011 · Codex Pr 3257 Current

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`ef70b175`)
- **Summary:** Seeded from local branch `codex/pr-3257-current`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0012 · Codex Pr 3257 Tail

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`14ee8c0e`)
- **Summary:** Seeded from local branch `codex/pr-3257-tail`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0013 · Codex Rl Funnel Facade Delegation

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`90f67166`)
- **Summary:** Seeded from local branch `codex/rl-funnel-facade-delegation`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0014 · Fix 3241 Spec

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`d4748e3d`)
- **Summary:** Seeded from local branch `fix/3241-spec`, which is
  7 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0015 · Fix Affinedrift Metrics Clobber 3273

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`ec259c52`)
- **Summary:** Seeded from local branch `fix/affinedrift-metrics-clobber-3273`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0016 · Fix Ball Flight Finite States 3285

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`5bacbca0`)
- **Summary:** Seeded from local branch `fix/ball-flight-finite-states-3285`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0017 · Fix Dbc Launch Conditions Finite States 3284 3285

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`0a461f82`)
- **Summary:** Seeded from local branch `fix/dbc-launch-conditions-finite-states-3284-3285`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0018 · Fix Dedup Escape Html 3291

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`ae1554b0`)
- **Summary:** Seeded from local branch `fix/dedup-escape-html-3291`, which is
  6 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0019 · Fix Exclude Internal Critic Docs 3913

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`1da2f4a2`)
- **Summary:** Seeded from local branch `fix/exclude-internal-critic-docs-3913`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0020 · Fix Golf Physics 3266 3271 3272

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`3d015a7e`)
- **Summary:** Seeded from local branch `fix/golf-physics-3266-3271-3272`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0021 · Fix Honest Unfinished Content 3918

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`fb59f8dd`)
- **Summary:** Seeded from local branch `fix/honest-unfinished-content-3918`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0022 · Fix Missing H1 Full Layout 3917

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`a338c479`)
- **Summary:** Seeded from local branch `fix/missing-h1-full-layout-3917`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0023 · Fix Rotation Converter 3281 3282 3283

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`a7b810b4`)
- **Summary:** Seeded from local branch `fix/rotation-converter-3281-3282-3283`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0024 · Fix Round Simulator Tests 3293

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`6b1d3f2c`)
- **Summary:** Seeded from local branch `fix/round-simulator-tests-3293`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0025 · Fix Swing Optimizer Dt 3288

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`3626c44e`)
- **Summary:** Seeded from local branch `fix/swing-optimizer-dt-3288`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0026 · Fix Terrain Bounce Roll 3275

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`27f6adf3`)
- **Summary:** Seeded from local branch `fix/terrain-bounce-roll-3275`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0027 · Issue 3221 Sw Networkfirst Local

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`e317d950`)
- **Summary:** Seeded from local branch `issue-3221-sw-networkfirst-local`, which is
  7 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0028 · Issue Golf Docs V1 Ci Fix

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`b776b73b`)
- **Summary:** Seeded from local branch `issue-golf-docs-v1-ci-fix`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0029 · Issue Mech Notation V1

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`e9d62a09`)
- **Summary:** Seeded from local branch `issue-mech-notation-v1`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0030 · Issue Sci V2

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`11a03223`)
- **Summary:** Seeded from local branch `issue-sci-v2`, which is
  6 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0031 · Issue Sec Audit V2

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`fb592f6a`)
- **Summary:** Seeded from local branch `issue-sec-audit-v2`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0032 · Issue Testing 3231 3230 3233 Local

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`3da4daca`)
- **Summary:** Seeded from local branch `issue-testing-3231-3230-3233-local`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0033 · Issue Webperf 3219 3221 3220 Local

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`938c260b`)
- **Summary:** Seeded from local branch `issue-webperf-3219-3221-3220-local`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0034 · Pr 3158 Palette

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`0171a1d2`)
- **Summary:** Seeded from local branch `pr-3158-palette`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-#3903 · Close cluster gaps: proximal–distal, impact/putting, technology

- **State:** shipped
- **Owner:** claude (wave-6 agent W6_3903)
- **Issue:** `#3903` (epic `#3896`)
- **PR:** [#4267](https://github.com/D-sorganization/AffineDrift/pull/4267) (merged)
- **Branch:** `claude/issue-3903-cluster-gaps`
- **Paths:** `articles/intentional-constraint-collapse.qmd`, `articles/passive-distributed-control.qmd`, `articles/proximal-distal-a-journey-through-the-swing.qmd`, `articles/proximal-distal-energy-transfer.qmd`, `resources/research-review-induced-acceleration-analysis.qmd`, `resources/research-review-interaction-forces.qmd`, `articles/secondary-axis-stability.qmd`, `articles/strokes-gained-limitations.qmd`, `articles/impact-mechanics-and-ball-flight.qmd`, `articles/rotation-induced-spin.qmd`, `articles/putting-roll-models.qmd`, `articles/green-simulation.qmd`, `articles/technology-club-fitting.qmd`, `articles/technology-heavy-hit-impact-coupling.qmd`, `articles/technology-launch-monitors.qmd`, `articles/technology-force-measurement.qmd`, `articles/technology-motion-capture.qmd`
- **Started:** 2026-09-07
- **Last verified:** 2026-09-28 (`5aedc884`)
- **Summary:** Wired the three measured cluster gaps from issue #3903: intentional-constraint-collapse and passive-distributed-control joined to the proximal-distal program (companion, monograph, summary, workbench); the two research reviews linked back into the article cluster they review; secondary-axis-stability and strokes-gained-limitations wired into the impact/putting cluster both ways; club-fitting and heavy-hit given the canonical Related Concepts component with reference-point-problem, vendor-reference, and model-interchange targets; unlinked backtick-path and bare-chapter items in the existing technology Related Concepts blocks converted to real links. The pinned `proximal_distal_energy_transfer/index.qmd` hunk was reverted to preserve immutable trust pins.
- **Next step:** No further delivery work for this batch; PR #4267 merged as
  `5aedc884`.

### DL-#3902 · Wire lateral links into Build pages: models, repositories, tools

- **State:** shipped (PR #4269 squash-merged to main as 1e5725de, 2026-09-08)
- **Owner:** claude (wave-6 agent W6_3902)
- **Issue:** `#3902` (epic `#3896`)
- **Branch:** `claude/issue-3902-models-lateral`
- **Paths:** `models/models.qmd`, `models/models-{simulink,mujoco,drake,pinocchio,pendulum,opensim,myosim}.qmd`, `repositories/*.qmd`, `pages/tools.qmd`, `articles/upstreamdrift-educational-integration.qmd`, `articles/rotation-converter.qmd`, `articles/proximal-distal-model-workbench.qmd`
- **Started:** 2026-09-07
- **Summary:** Added the canonical markdown `## Related Articles` component to all 8 `models/*.qmd` and all 6 `repositories/*.qmd` pages plus `pages/tools.qmd` and three isolated articles; 177 new relative markdown content links, every model↔repository pair bidirectional.

## Shipped (Last 90 Days)

Entries stay here for 90 days after merge, then move to the archive.

### DL-#4712 · Two-Hand Wrench Chapter Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4712 (regular)
- **Issue:** #4710 (corpus #4021; epic #4009)
- **Branch:** `fix/two-hand-wrench-rigor-4710`
- **Paths:** `articles/proximal_distal_companion/chapters/ch12_two_hands_one_wrench.qmd`, `references/proximal-distal-energy.bib`, `models/bilateral-hand-wrench-validation.qmd`, `tests/test_two_hand_wrench_review.py`, `reports/technical-review/two-hand-wrench-review.md`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (combined-main suite: 6,034 passed, 29 skipped, 92.88% coverage; final content: 180 passed/four skipped; 39 protocol/history/audit checks; 209-page PDF and 20 browser cases verified)
- **Summary:** Reconcile force/moment origins, map degeneracies, rigid/flexible power and archived sensor/contact evidence; distinguish synthetic model support from human inference. Citation-only updates in three neighboring chapters and the protocol do not renew their scientific reviews.
- **Next step:** Merged to remote main be263f9cd946a6aa8b4a97b086af9eab399c3ac6 at 23:32:17 UTC; all protected CI checks passed (36786787125). Lease and presence released. Provider citation follow-up #4711 remains open.

## Archive

Older entries live in `DEVELOPMENT_LOG_ARCHIVE_<year>.md`.
