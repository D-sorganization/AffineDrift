# Development Log Archive — 2026

### DL-#4865 · Shared Nomenclature Delivered

- **State:** shipped
- **Owner:** codex
- **Issue:** #4865; epic #4009 / corpus #4021
- **Branch:** fix/shared-nomenclature-review
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4870
- **Summary:** Complete shared-source review and six dependent PDF editions delivered at ecc23b233, with final-head CI and exact remote-main evidence. Accepted source a738be703 retains separate full-checkpoint and later clarification validation scopes.
- **Evidence:** reports/technical-review/shared-nomenclature-remote-main-receipt.json; shared-nomenclature-delivery.json; shared-nomenclature-validation.json.
- **Next step:** No remaining #4865 delivery work; #4868 and the broader corpus remain open.
- **Paths:** See https://github.com/D-sorganization/AffineDrift/pull/4870 and the original Evidence field
- **Started:** 2026-10-04 (entry first present in the blamed source commit; actual work start not recorded)
- **Last verified:** 2026-10-04 (metadata source date); Not recorded; metadata provenance `f10a0feff09d` (original entry, not a new scientific or CI validation)

### DL-#4863 · Underactuation Chapter Review

- **State:** shipped
- **Owner:** codex
- **Issue:** #4863; epic #4009 / corpus #4021
- **Branch:** fix/underactuation-review
- **PR:** #4867
- **Summary:** Complete chapter and corresponding combined-volume blocks reviewed; metric decay assumptions and scope clarified while preserving prior mechanics. Eight supplied-text Flash helpers adjudicated. Fifteen print chapter pages plus revised title and twenty web captures inspected; final four browser/axe cells pass.
- **Evidence:** reports/technical-review/underactuation-review.md; 63 focused checks, 208 content cases and 16 publication gates pass. All 72 protected files and 250 other route identities preserved.
- **Next step:** Full suite at 0160547578c00a8cb711f6246c3c1480d48dc567 passed 6810 with 93.24% src coverage. Subsequent eight heading-only prefixes pass 63 focused, 208 content, five gates and four browser/axe cells; mathematical text and PDFs unchanged. Accepted source 30625cf420f79ed7ffbe070a6322d0f5903dc025 binds twelve files and four findings. The 63 post-binding checks pass and checkpoint e12767c10 is pushed. Parent update bfebb9d5210ccc3c0e47d92f3e8b63c4ef014d24/main af4c2d42e is integrated; 100 tests pass with one skip. Integration 63812c493 is pushed. Parent #4862 is verified on remote main at 48261ef8587095832b3360648f4cc6d444d6c36b and integrated with the child tree unchanged. Regular PR #4867 is open with guarded squash auto-merge armed. Verify final-head CI and remote-main delivery. Read-only whole-book preparation and confirmed missing HTML terms are queued under unclaimed #4864. No whole-book, empirical or live-site acceptance.


- **Verified delivery:** PR #4867 merged as `897dd890704a18481ba229d35add610694da0285`; exact tree, 27 changed paths, 12 accepted scientific files and 72 prior files verified on remote main. CI Standard 37170328750 passed; lease/presence released.
- **Paths:** See #4867 and the original Evidence field
- **Started:** 2026-10-04 (entry first present in the blamed source commit; actual work start not recorded)
- **Last verified:** 2026-10-04 (metadata source date); Not recorded; metadata provenance `6be3a480a707` (original entry, not a new scientific or CI validation)

### DL-#4860 · Passive-Stabilization Chapter Review

- **State:** shipped
- **Owner:** codex
- **Branch:** fix/passive-stabilization-review
- **PR:** #4862
- **Summary:** Three source copies reviewed; conservative loaded-loop stiffness bridge, constitutive/rate conventions and citation scope corrected. Five text-only Flash helpers adjudicated; 38 focused, 204 content, 16 gates and 6805 full cases passed (93.24% source coverage). Seven print pages and ten web captures inspected. Complete current source/scoped presentation locally accepted.
- **Delivery:** Regular PR #4862 merged as 48261ef8587095832b3360648f4cc6d444d6c36b; full reviewed tree, 24 owned paths, eleven frozen and 61 prior scientific files verified on remote main. CI Standard 37166080212 passed at final head bfebb9d5210ccc3c0e47d92f3e8b63c4ef014d24. Receipt: reports/technical-review/passive-stabilization-remote-main-receipt.json.
- **Next step:** None for this bounded chapter review. Continue epic #4009 under #4863.
- **Issue:** #4860
- **Paths:** See #4862 and the original Evidence field
- **Started:** 2026-10-04 (entry first present in the blamed source commit; actual work start not recorded)
- **Last verified:** 2026-10-04 (metadata source date); Not recorded; metadata provenance `897dd890704a` (original entry, not a new scientific or CI validation)

### DL-#4858 · Paired Optimal-Control Review

- **State:** shipped
- **Owner:** codex
- **Issue:** #4858; epic #4009 / corpus #4021
- **PR:** #4859
- **Branch:** fix/optimal-control-review
- **Paths:** articles/The_Geometry_of_Motion/Volume_I/chapters/ch05_optimal_control.tex, articles/The_Geometry_of_Motion/quarto/ch05_optimal_control.qmd, tests/test_optimal_control_conventions.py
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 — 74 focused checks, 16 publication gates and full retry 6800 passed/29 skipped/93.24% source coverage; seven revised print pages and sixteen web captures inspected. Initial four PDF-dependency failures repaired without changing audit identities.; metadata provenance `48261ef85870` (original entry, not a new scientific or CI validation)
- **Summary:** Clarify numerical conventions while preserving valid prior optimal-control mechanics and inference limits.
- **Next step:** None for this bounded chapter review. Continue epic #4009 under #4860.
- **Evidence:** reports/technical-review/optimal-control-remote-main-receipt.json; PR #4859 merged as ca0e1b8bed20f58366e95dd453fecffbdf17cb89; complete reviewed tree, 23 owned paths, nine frozen and 52 prior scientific files verified. CI Standard passed at reviewed head; lease/presence released.

### DL-#4855 · Drift, Wrench and Double-Pendulum Power

- **State:** shipped
- **Owner:** codex
- **Issue:** #4855; epic #4009 / corpus #4021
- **PR:** #4857
- **Branch:** fix/drift-wrench-review
- **Paths:** articles/drift-components-wrench-double-pendulum.qmd, tests/test_drift_wrench_review.py, reports/technical-review/drift-wrench-prior-review.json
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 — eight original publication-contract failures, twelve mechanical passes; corrected combined suite 48 passed. Eight Flash helpers adjudicated. HTML render preserves eighteen original section anchors; four browser cells and twelve revised/detail captures pass after correcting clipped equations. Final 48-case rerun and 193 content checks passed; full clean retry 6790 passed/29 skipped/93.24% coverage after preserving prior packaging output and passing six hygiene checks. Initial two hygiene failures retained. Nine Flash helpers adjudicated; complete source accepted at 0feeebd0897f67211e076ffb2139bf4445a9e8ce, with six frozen scientific files. Four scoped findings and one original corpus row are bound; delivery pending.
- **Summary:** Complete the article argument review while preserving valid prior mechanics; distinguish input attribution, segment force/couple power and motor work with explicit frames and independently checked examples.
- **Next step:** Delivered in #4857 as 252c8a086a3a532ee7e2204f94a945ef41f50bd5; 19 owned paths, six frozen and 46 protected files verified, CI passed and lease/presence released. See drift-wrench-remote-main-receipt.json.

### DL-#4853 · DCR Figure Inference Regression

- **State:** shipped
- **Owner:** codex
- **Issue:** #4853; epic #4009 / corpus #4021
- **PR:** #4856
- **Branch:** fix/dcr-figure-rigor
- **Paths:** articles/drift-control-ratio.qmd, articles/figures/core_theory/fig_dcr_vector_decomposition.svg, articles/figures/core_theory/fig_dcr_reachability_tubes.svg, articles/figures/core_theory/fig_dcr_swing_phases.svg
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 — three bounded figure corrections implemented; initial red ten failures/three passes; 32 focused checks passed; three corrected SVGs and twelve page captures inspected; canonical browser four cells pass after existing deployment cleanup; twenty protected files retained; nine Flash helpers adjudicated. Source bound at b6ab9a9229738d764d93975e87e04af1d1b550df; 175 dependent and 185 content checks pass after resolving three generated-metadata failures from the broad run (6775 passed, 29 skipped, 93.24% coverage). Ten Flash helpers adjudicated.
- **Summary:** Reconcile later figures and long descriptions with drift, input-set, observation and finite-time assumptions; preserve valid prior review.
- **Next step:** Delivered in regular PR #4856 as c1d33e780b9a920cf500da2b3adbf2d250441a4b; all 25 owned paths and protected evidence verified on remote main, full CI passed and coordination released. Receipt carried by #4855.

### DL-#4852 · Corpus Status Reconciliation

- **State:** shipped
- **Owner:** codex
- **Issue:** #4852; epic #4009 / corpus #4021
- **PR:** #4854; regular; parent #4851 verified on remote main
- **Branch:** docs/corpus-reconcile-4852
- **Paths:** docs/development/technical-review/corpus-review-index.csv, reports/technical-review/corpus-status-reconciliation.md, reports/technical-review/corpus-status-reconciliation.json, AGENT_HANDOFF.md
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 — 13 historical source/evidence comparisons and 22 retained mechanics tests pass; seven corpus rows corrected (five scope updates and two renamed paths); all 407 current paths exist; 57 document/ledger checks pass; four agy Flash inventories adjudicated; no new scientific acceptance.; metadata provenance `07bcb56f514e` (original entry, not a new scientific or CI validation)
- **Summary:** Distinguish stale bookkeeping from unfinished source review; preserve historical proof and prioritize the longer remaining originals.
- **Next step:** Delivered via regular PR #4854 as 07bcb56f514ebf846ce7d391ec482d8d1b782a1c; all ten owned paths and ten frozen parent files verified; CI passed and coordination released. Receipt carried by #4853.

### DL-#4850 · Musculoskeletal Modeling Conventions

- **State:** shipped
- **Owner:** codex
- **PR:** #4851
- **Issue:** #4850; epic #4009 / corpus #4021
- **Branch:** fix/msk-conventions-rigor
- **Paths:** articles/The_Geometry_of_Motion/Volume_III/chapters/ch02_musculoskeletal_conventions.tex, articles/The_Geometry_of_Motion/Volume_III/main.pdf, tests/test_msk_conventions_review.py
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 — baseline `eaae683256ec0924c43307427a94c9ff61d83318`; complete chapter corrected; 51 focused plus 2 explicit content checks pass; native PDF and 51-page carry checks pass; initial full run 6764 passed/1 Windows encoding failure at b7c433455; seven minifier tests pass under UTF-8; bounded landing/browser checks pass; full UTF-8 retry passed at `387de1628d5f9a67e35a12652cdb43ddfc0592ef`: 6765 passed, 29 skipped, 187 deselected, 51 warnings in 608.05s (0:10:08); 93.24% coverage; chapter accepted at `d53ec669335a900fcf42bd4a6065d1d6d27046a8`; ten frozen files bound; 73 post-binding checks pass.
- **Summary:** Reconcile anatomical frames, declared rotation coordinates, inertia origin/order and inference limits.
- **Next step:** Delivered as `c11e1370798723e2e4787e30fa0d6374e3cf0ac4`; all 24 owned, ten frozen, 67 prior and 172 Geometry paths verified on remote main. Exact-head CI Standard and all textbook builds passed. Receipt is carried by #4852; bounded acceptance retained and coordination released.

### DL-#4847 · Launch-Monitor Validation Program

- **State:** shipped
- **Owner:** codex
- **PR:** #4849
- **Issue:** #4847; epic #4009 / corpus #4021
- **Branch:** fix/validation-program-rigor-4847
- **Paths:** articles/Launch_Monitor_Technology_Review/sections/11-validation-program.tex, articles/Launch_Monitor_Technology_Review/references.bib, articles/Launch_Monitor_Technology_Review/main.pdf, tests/test_validation_program_review.py
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 — PR #4849 at `eaae683256ec0924c43307427a94c9ff61d83318`; nine frozen files, 17 owned paths and 64 prior dependencies verified on remote main; CI and textbook builds pass.
- **Summary:** Distinguish software readiness from preregistration and physical evidence; derive agreement, reference uncertainty, clustering and sample-planning limits while preserving the accepted-pair gate.
- **Next step:** Delivery complete; continue scoped review #4850.
- **Shipped:** 2026-10-03

### DL-#4845 · Degrees-of-Freedom Chapter

- **State:** shipped
- **Owner:** codex
- **PR:** #4846
- **Issue:** #4845; epic #4009 / corpus #4021
- **Branch:** fix/dof-chapter-rigor-4845
- **Paths:** articles/The_Geometry_of_Motion/Volume_IV/chapters/ch01_dof_problem.tex, articles/The_Geometry_of_Motion/Volume_IV/main.pdf, books/human-motor-control.qmd, src/affine_control/ucm_analysis.py, tests/test_ucm_analysis.py, tests/test_dof_chapter_review.py
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 (`5917ebf0ae1f2421b37c0a9ec73bde4c8966daf2`); 11 frozen files, 23 owned paths and 55 prior dependencies verified on remote main; CI 37120237483 and textbook compilation passed.
- **Summary:** Separate task geometry, physical feasibility and neural inference; preserve historical review scope when refreshing shared publication dependencies.
- **Next step:** Delivery complete; turnover PR #4848 merged at a4afe8cc9f573e29fe11f22bf79dae1e39ba4dc9 with CI and remote-file verification. Continue scoped review #4847.
- **Shipped:** 2026-10-03

### DL-#4842 · Impact Physics Chapter

- **State:** shipped
- **Owner:** codex
- **PR:** #4844
- **Issue:** #4842; epic #4009 / corpus #4021
- **Branch:** fix/impact-chapter-rigor-4842
- **Paths:** articles/Launch_Monitor_Technology_Review/sections/03-impact-physics.tex, articles/Launch_Monitor_Technology_Review/references.bib, articles/Launch_Monitor_Technology_Review/main.pdf, tests/test_impact_chapter_review.py
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 (`d907add46b30ecedfc866f36ff5ab2c337bdfa16`); 39 frozen files and complete reviewed tree verified on remote main; CI 37110978517 and textbook compilation passed.
- **Summary:** Correct collision geometry, impulse and gear scaling; separate empirical models and instrument inference with explicit PDF/bibliography carry-forward.
- **Next step:** Scientific delivery complete through PR #4844; PR #4843 finalizes receipts and repairs historical handoff heading duplication. Continue epic #4009 after that turnover is delivered.
- **Shipped:** 2026-10-03


### DL-#4836 · Passive Distributed Control Article

- **State:** shipped
- **Owner:** codex
- **PR:** #4843; original #4841 merged
- **Issue:** #4836; epic #4009 / corpus #4021
- **Branch:** fix/passive-control-rigor-4836
- **Paths:** articles/passive-distributed-control.qmd, src/affine_control/series_elastic_demo.py, tests/test_series_elastic_demo.py
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03 (`d907add46b30ecedfc866f36ff5ab2c337bdfa16`); 39 frozen files and complete reviewed tree verified on remote main; CI 37110978517 and textbook compilation passed.
- **Summary:** Reconcile mechanical topology and energy accounting; distinguish passive mechanics, controlled stability and empirical learning claims.
- **Next step:** Scientific delivery complete through PR #4844; PR #4843 finalizes receipts and repairs historical handoff heading duplication. Continue epic #4009 after that turnover is delivered.

- **Shipped:** 2026-10-03


### DL-#4756 · Complete-State Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** [#4758](https://github.com/D-sorganization/AffineDrift/pull/4758)
- **Issue:** #4756 (epic #4009)
- **Branch:** fix/state-snapshot-rigor-4756
- **Paths:** articles/proximal_distal_companion/chapters/ch03_state_snapshot.qmd, scripts/make_proximal_distal_companion_figures.py, tests/test_state_snapshot_review.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (six new checks;12 publication gates;654 titles;Ruff/Black836;CI-scoped mypy94;221-page PDF/parity/changed-page inspection;4 browser/axe cases;full6401 passes/29 skips/78.9% configured coverage/93.0% src;63 affected); metadata provenance `39f7553b562b` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-10-01 (PR4750 open;seven findings bound;32 final binding checks pass;full6381 pass/one stale-registry failure/29 skips;unsupported release withdrawn;73 integrated checks pass;12 gates;653 titles;Ruff/Black832;four final browser/axe cases); metadata provenance `394a7b40bbff` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-10-01 (73 focused pass;12 gates;653 titles;Ruff/Black831;96 MathJax expressions;full6372 pass/two root-hygiene failures;packaging artifacts preserved;18 follow-up and53 integrated checks pass;strict button9/10 plus two reruns pass with one navigation timeout retained); metadata provenance `4c1ddafa5a51` (original entry, not a new scientific or CI validation)
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

### DL-#4725 · Annotated Reference Library

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4729 (regular)
- **Issue:** #4725 (epic #4009)
- **Branch:** `fix/reference-library-rigor-4725`
- **Paths:** `articles/Launch_Monitor_Technology_Review/sections/appendix-a-references.tex`, `articles/Launch_Monitor_Technology_Review/sections/03-impact-physics.tex`, `articles/Launch_Monitor_Technology_Review/references.bib`, `articles/Launch_Monitor_Technology_Review/main.pdf`, `reports/technical-review/reference-library-review.md`, `tests/test_reference_library_review.py`
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (21 focused passes; 6178 full-suite passes/29 skips; 78.37% combined coverage and 92.95% src-only from same data; 183 post-full content passes/four skips; 78-page PDF and 20 final pages verified; Ruff/Black/titles/content gates pass; broad mypy has nine errors in unchanged production sources); metadata provenance `7eb87e3c94bc` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-10-01 (39 focused/legacy/hygiene checks; four final browser cases, zero serious/critical axe findings; three equations and final PDF pages inspected); metadata provenance `fd508f04cd48` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-10-01 (6086 full-suite passes, 29 skips, 92.95% coverage; 38 focused audit/numerical/hygiene passes; 138 rendered expressions/23 displays visually checked at 390/1440 px; four browser cases and one axe scan, zero serious/critical findings; twelve content gates and Ruff/Black/mypy pass); metadata provenance `644bfd5bebb1` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-30 (40 focused and 46 post-cleanup cases pass; 6,057 full-suite passes/29 skips; separate coverage run passed at 92.95%; 180 content passes/four skips; 76-page book with fifteen final pages visually checked; Ruff/Black/mypy and content gates pass); metadata provenance `2a7c094070c5` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-30 (21 impact checks; 46 post-binding audit/numerical/hygiene checks; 179 content passes; full Windows 6036 passes and three audit/snapshot failures subsequently resolved; 92.88% coverage; Ruff/Black/mypy and 12 content gates; final 12 browser cases and 74 math expressions); metadata provenance `bd1255f15392` (original entry, not a new scientific or CI validation)
- **Summary:** Bound the instantaneous theorem, inertia reduction and historical solver evidence; correct primary-study and human-objective inference; reconcile two linked public summaries without renewing their other review scope.
- **Next step:** Complete. Regular PR #4718 merged to remote main 24cdba4d49abec347bbe56fd51cc7d5ed00ab6a5 at 2026-10-01 00:23:35 UTC; every protected check passed (CI 36792360532). Lease/presence released. Provider follow-up Tools #5393 and separately owned deployment gap #4688 remain open.


### DL-#4710 · Two-Hand Wrench Chapter Review

- **State:** shipped
- **Owner:** codex
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4712 (regular)
- **Issue:** #4710 (corpus #4021; epic #4009)
- **Branch:** `fix/two-hand-wrench-rigor-4710`
- **Paths:** `articles/proximal_distal_companion/chapters/ch12_two_hands_one_wrench.qmd`, `references/proximal-distal-energy.bib`, `models/bilateral-hand-wrench-validation.qmd`, `tests/test_two_hand_wrench_review.py`, `reports/technical-review/two-hand-wrench-review.md`
- **Started:** 2026-09-30
- **Last verified:** 2026-09-30 (combined-main suite: 6,034 passed, 29 skipped, 92.88% coverage; final content: 180 passed/four skipped; 39 protocol/history/audit checks; 209-page PDF and 20 browser cases verified); metadata provenance `24cdba4d49ab` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-30 (ten RED regressions; 98 focused checks GREEN; full Windows suite 6,028 passed, 29 skipped, 92.95% coverage; 179 content checks passed, four skipped; Ruff/Black/mypy/SPEC/evidence checks pass); metadata provenance `be263f9cd946` (original entry, not a new scientific or CI validation)
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

### DL-#4477 · Companion Opening and Whole-Swing Ledger

- **State:** shipped
- **Owner:** codex
- **PR:** #4478
- **Issue:** #4477 (corpus #4021; epic #4009)
- **Branch:** `fix/4477-ledger-rigor`
- **Paths:** `articles/proximal_distal_companion/chapters/ch01_follow_the_energy.qmd`, `articles/proximal_distal_companion/chapters/ch29_whole_swing_ledger.qmd`, `articles/proximal-distal-a-journey-through-the-swing.qmd`
- **Started:** 2026-09-28
- **Last verified:** 2026-09-28 (17 focused checks; full suite 5,626 passed/29 skipped/132 deselected, 92.88% coverage. Content 131 passed/four skipped; static checks pass. Four browser cases and 207-page PDF verified; archived NPZ consistency and seven provider hashes verified.); metadata provenance `e2cc43616f31` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-28 (All 16 focused checks pass; full suite 5,609 passed/29 skipped/132 deselected, 92.88% coverage. Content 131 passed/four skipped; static checks pass. Four browser cases pass, zero severe axe findings; eight display equations visually inspected.); metadata provenance `1a8dd00b7221` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-28 (Complete article corrected; seven source/example failures reproduced; all 16 checks pass. Full suite 5,593 passed/29 skipped/132 deselected, 92.88% coverage; content 131 passed/four skipped; static checks pass. Four browser cases pass, zero severe axe findings; all ten display equations visually reviewed.); metadata provenance `1a8dd00b7221` (original entry, not a new scientific or CI validation)
- **Summary:** Separates model interventions and causal inference, corrects spatial/beam/mass mechanics and replaces nonexistent wire guarantees with explicit synthetic proposals.
- **Next step:** Merged and publication verified at 1a8dd00b (deployment 36397339440). No current development; broader goal paused.

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

### DL-#4471 · Markerless Camera Measurement Rigor

- **State:** shipped
- **Owner:** codex
- **PR:** #4472
- **Issue:** #4471 (corpus #4021; epic #4009)
- **Branch:** `fix/4471-camera-rigor`
- **Paths:** `articles/markerless-mocap-camera-selection.qmd`, `data/markerless_mocap/camera_evidence_registry_v1.json`, `tests/test_camera_selection_rigor.py`
- **Started:** 2026-09-27
- **Last verified:** 2026-09-27 (Full article and 57 registry claims inspected. RED: ten numerical passes, six source failures; GREEN: all 16 plus 14 registry contracts pass. Manufacturer modes and study transfer corrected.); metadata provenance `994cd2be25a7` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-27 (14 focused checks pass after six source RED failures; 5,519 full-suite passes with two temporary Playwright root-hygiene failures, resolved and all six hygiene tests pass; 92.88% src coverage. Content lint 131 passed/four skipped. Ruff, Black, title audit and mypy pass. Native 15-page PDF visually checked; ten standalone renders and twenty browser cases pass.); metadata provenance `54d73e39df5d` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-22 (SELF; PR4426 merged as99aa5835; deployment35796355561 succeeded with live artifact10725510305,960/960 and four chapter cases pass; CI gravity constant naming corrected without numerical change; all eight full textbook builds and Python3.12 CI pass; complete paired rewrite; 20 numerical checks and 14 attribution contracts pass; 128 matching body expressions; all ten print pages and 18 desktop displays inspected; four production browser cases pass, 139 rendered expressions per case and 11 complete mobile scroll endpoints); metadata provenance `4fe70151c4e6` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-22 (SELF; live publication verified; entire article rewritten; 15 independent mechanics/calibration/capture cases and 18 inventory checks pass; four production browser cases pass with zero serious/critical axe violations; all168 math expressions render in each case; all 28 desktop equations and four tables visually inspected; four expanded cases and every wide scroll endpoint pass); metadata provenance `ded63640e864` (original entry, not a new scientific or CI validation)
- **Summary:** Finds missing rotational inertia in slope acceleration, omitted first-order lateral resistance, spinless-only skid assumptions, incorrect V-groove geometry and a false universal capture limit. Primary Penner paper and official USGA sources inform corrections; preparation notes preserve access limits and derivations.
- **Next step:** Publication verified at ded63640 via deployment35792227837 and live artifact10722988337;960/960 and all four putting cases pass. Preserve frozen evidence a17f5ded.

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
- **Last verified:** 2026-09-22 (SELF; protected PR merged, successful successor deployment35774559003 at main581857cb; downloaded live artifact10716514261 passes960/960 cases; all eight anatomy/preface records independently inspected, HTTP200, no page overflow, no serious/critical axe violations; prior scientific/render validation retained in review reports); metadata provenance `581857cb2481` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-22 (SELF; protected PR merged, successful successor deployment35774559003 at main581857cb; downloaded live artifact10716514261 passes960/960 cases; all eight anatomy/preface records independently inspected, HTTP200, no page overflow, no serious/critical axe violations; prior scientific/render validation retained in review reports); metadata provenance `4ac3a34a5d08` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-21 (PR #4407 merged 2026-09-21T21:47:01Z as `fix(deploy): ignore third-party embed localStorage pageerrors (#4406)`; issue #4406 closed.); metadata provenance `7435503a09f4` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-22 (merge32010d08d9980896c51f0c93ac875f23eb818556; successful exact deployment34730740904; downloaded live artifact10309497076:960/960 cases pass; independently inspected four companion-route records, all HTTP200 with zero overflow and no serious/critical axe violations; prior detailed numerical/render validation retained in technical review reports); metadata provenance `32010d08d998` (original entry, not a new scientific or CI validation)
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
- **Last verified:** 2026-09-22 (merge32010d08d9980896c51f0c93ac875f23eb818556; successful exact deployment34730740904; downloaded live artifact10309497076:960/960 cases pass; independently inspected four companion-route records, all HTTP200 with zero overflow and no serious/critical axe violations; prior detailed numerical/render validation retained in technical review reports); metadata provenance `32010d08d998` (original entry, not a new scientific or CI validation)
- **Summary:** Restores subordinate heading levels without changing chapter prose or incoming anchors. Rebuilds and synchronizes both PDFs with the corrected Chapter30 science. Preserves mobile equation type size. Integrates protected nullspace main squash7f0fed76; retains current turnover records through three documentation conflicts.
- **Next step:** None for this delivery; broader corpus work continues under #4009/#4021.

### DL-#3902 · Wire Lateral Links Into Build Pages: Models, Repositories, Tools

- **State:** shipped (PR #4269 squash-merged to main as 1e5725de, 2026-09-08)
- **Owner:** claude (wave-6 agent W6_3902)
- **Issue:** `#3902` (epic `#3896`)
- **Branch:** `claude/issue-3902-models-lateral`
- **Paths:** `models/models.qmd`, `models/models-{simulink,mujoco,drake,pinocchio,pendulum,opensim,myosim}.qmd`, `repositories/*.qmd`, `pages/tools.qmd`, `articles/upstreamdrift-educational-integration.qmd`, `articles/rotation-converter.qmd`, `articles/proximal-distal-model-workbench.qmd`
- **Started:** 2026-09-07
- **Summary:** Added the canonical markdown `## Related Articles` component to all 8 `models/*.qmd` and all 6 `repositories/*.qmd` pages plus `pages/tools.qmd` and three isolated articles; 177 new relative markdown content links, every model↔repository pair bidirectional.
- **PR:** #4269
- **Last verified:** 2026-09-08 (metadata source date); Not recorded; metadata provenance `5aedc884a511` (original entry, not a new scientific or CI validation)

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
- **Last verified:** 2026-09-10 (PR #4363 merged as `docs(architecture): adopt maintainable Mermaid C4 architecture-map contract (#1595)`; SPEC.md change log row added 2026-09-10 #4363.); metadata provenance `b2677925b5c6` (original entry, not a new scientific or CI validation)
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

### DL-#4839 · Site Glossary Scientific Consistency

- **State:** shipped
- **Owner:** codex
- **PR:** #4840 (regular; merged)
- **Issue:** #4839; epic #4009
- **Branch:** fix/glossary-rigor-4839
- **Paths:** data/glossary.yml, pages/glossary.qmd, tests/test_site_glossary.py
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03; merge ffed849156fc50ce836e9cc6ca85c19184a6c12d on remote main; CI37099199797 success at head15ba42. All seven current and 18 parent evidence files unchanged; peer PR4835 changes explicitly reconciled.
- **Summary:** Audit 72 glossary definitions and publication; see site-glossary-review.md.
- **Next step:** Delivered; site-glossary-remote-main-receipt.json. Lease and presence released.

### DL-#4832 · Screw Reference Geometry and Dynamics

- **State:** shipped
- **Owner:** codex
- **PR:** #4838 (regular)
- **Issue:** #4832; epic #4009 / corpus #4021
- **Branch:** fix/screw-reference-rigor-4832
- **Paths:** articles/screw-theory-reference.qmd, tests/test_screw_reference_review.py
- **Started:** 2026-10-03
- **Last verified:** 2026-10-03; merged 503fb4fe6e686fcdcc13a8ac56c5039d313fbff6; CI37093639733 success on d041ad383e9b711a3560e10ef280f8519c1d883d. All five current and 13 parent frozen files unchanged; 24 exact owned blobs and one additive peer SPEC row verified.
- **Summary:** Screw reference revision accepted.
- **Next step:** Delivered; reports/technical-review/screw-reference-remote-main-receipt.json. Lease/presence released.

### DL-#4831 · Radar Observability and Spin-Axis Review

- **State:** shipped
- **Owner:** codex
- **PR:** #4833 (regular; merged)
- **Issue:** #4831; epic #4009 / corpus #4021
- **Branch:** fix/radar-rigor-4831
- **Paths:** articles/Launch_Monitor_Technology_Review/sections/04-radar-systems.tex, articles/Launch_Monitor_Technology_Review/references.bib, tests/test_radar_systems_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-03 remote main 6b9d4574157e6d48ac4ac4edf6f59dc5d071b6ea; CI37082657317 and textbook build37082657226 succeeded on exact head d678f76746b5020ecd9dd65807e334b6e5bf2581; all23owned blobs, entire tree and all8frozen radar files preserved; ancestry verified.
- **Summary:** Complete chapter draft corrects phase/harmonic ambiguities, conditional axis inference, patent delay algebra, device/ball modes and correlated face inference. Research dossier records primary-reading limits. One corpus row accepted; 100 source audits and whole-book consistency remain.
- **Next step:** Delivered; receipt reports/technical-review/radar-systems-remote-main-receipt.json. Lease/presence released.

### DL-#4825 · Ideomotor Prediction and Action Review

- **State:** shipped
- **Owner:** codex
- **PR:** #4829 (regular; merged)
- **Issue:** #4825; epic #4009 / corpus #4021
- **Branch:** fix/ideomotor-rigor-4825
- **Paths:** articles/ideomotor-theory-and-predictive-brain.qmd, src/affine_control/ideomotor_demo.py, tests/test_ideomotor_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-03 merge 53f75b29125cdc1f5da8d0c09020b3b05f04b783; CI37075895860 succeeded on ca4a23487; 18 owned files exact plus three shared-policy reconciliations match validated094; all five frozen source files and remote-main ancestry verified.
- **Summary:** Full article draft separates prediction/task errors, dynamics/actuation, prior/likelihood precision, free-energy identity and action selection. Repaired zero-action Euler example with a bounded constant-torque search and typed nominal DOP853 predictor. Seven Flash outputs adjudicated. Complete article and bounded publication accepted; six findings bound; primary-reading limits recorded. 101 source audits and whole-book consistency remain.
- **Next step:** Delivered; receipt reports/technical-review/ideomotor-remote-main-receipt.json. Lease/presence released. Newer local094 turnover ships through radar PR4833.

### DL-#4815 · Lagrangian Mechanics and Counterfactual Reference

- **State:** shipped
- **Owner:** codex
- **PR:** #4818 (regular); parent #4814 verified on remote main
- **Issue:** #4815; epic #4009 / corpus #4021
- **Branch:** fix/lagrangian-rigor-4815
- **Paths:** articles/lagrangian-reference.qmd, tests/test_lagrangian_reference_review.py, css/lagrangian-reference.css
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 41c7a6df057ae0fd35f85b1bf001afdc19596f4b; exact-head CI37046038628 succeeded;22owned blobs and entire merge tree equal91bf834;remote-main ancestry verified.
- **Summary:** Review eight mechanics decisions spanning energy functions, coordinates, flexible inertia, damping, input levels, constraints, boundary power and counterfactuals. Seven Flash helper outputs adjudicated. Source 13bd1cc29c3249e284cd379fdfb60679cc44f93e committed; eight findings bound and all other routes preserved. Binding 50c169c27d52595de7e5361dff4ae2f83daacbed and accepted source are verified on the remote topic; integration checkpoint91b32cca96a56a14426ea86f987a8445ca60ff4b is verified on remote topic; queued Chapter18 issue#4817 has a committed preparation note and no acceptance credit. There are 105 source audits plus whole-book consistency remaining.
- **Next step:** Delivered; see reports/technical-review/lagrangian-remote-main-receipt.json. Lease/presence released19:36UTC. Chapters18/28 ship separately in one combined PR.

### DL-#4811 · Negative Torque, Conjugate Power, and Causal Evidence

- **State:** shipped
- **Owner:** codex
- **PR:** #4812 (regular); parent #4810 verified on remote main
- **Issue:** #4811; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/negative-torque-rigor-4811
- **Paths:** articles/proximal_distal_companion/chapters/ch13_negative_torque.qmd, scripts/make_proximal_distal_companion_figures.py, tests/test_negative_torque_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; protected merge 48265e2002b9c5b326993935bae726b1e3667717; CI37019006638 succeeded; all25owned blobs and entire tree match accepted80b00bf271fcfd6ef33cd979350fa122f0d24bca.
- **Summary:** Separate club-side and joint power, moment transport, physical energy inputs, reaction geometry, pointwise/forward/finite-strategy evidence and human attribution. Eight agyFlash helpers read/adjudicated. Eight decisions bound;177priorfindings preserved,185totalfindings and107sourceaudits pluswholebookreview remain.
- **Next step:** Delivered. See reports/technical-review/negative-torque-remote-main-receipt.json. Lease and presence released at15:17UTC. No remaining work for this bounded review.

### DL-#4807 · Velocity Summation and Sequence Evidence

- **State:** shipped
- **Owner:** codex
- **PR:** #4810 (regular); parent #4808 verified on remote main
- **Issue:** #4807; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/sequence-rigor-4807
- **Paths:** articles/proximal_distal_companion/chapters/ch08_summation_of_speed.qmd, scripts/make_proximal_distal_companion_expanded_figures.py, tests/test_sequence_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; protected merge a2e4725f94261c1c41af30a1d2f2ca1e30347f21; CI37010363062 succeeded;25owned blobs and whole tree match accepted93f04ccfdf32cbe6ceb066a3fb2a30e35598b12f.
- **Summary:** Distinguish velocity sums, vector peak timing, energy/power and causal claims; correct finite-study interpretation and citation scope; replace uncomputed figure coupling label with a normalized schematic. Four implementation Flash helpers read and adjudicated. Eight findings bound (177 total), prior 169 preserved; 108 source audits plus whole-book consistency remain. Protected delivery pending.
- **Next step:** None for this delivered chapter. Lease and presence released; sequence-remote-main-receipt.json records proof. Chapter13 delivery remains separate.

### DL-#4806 · Sensitivity, Identifiability, and Measurement

- **State:** shipped
- **Owner:** codex
- **PR:** #4808 (regular); parent #4804 verified on remote main
- **Issue:** #4806; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/sensitivity-rigor-4806
- **Paths:** articles/proximal_distal_companion/chapters/ch21_sensitivity_identifiability.qmd, scripts/make_proximal_distal_companion_expanded_figures.py, tests/test_sensitivity_review.py, references/proximal-distal-energy.bib
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; protected merge acbaf49ec23f95f3a25fa887c4a9f000e13ca8dc; exact-head CI37001380667 succeeded; 26 owned Git blobs and the whole merged tree match accepted 891b38bcf34b967025e7d4d1d733e8ee9c1e888a. Historical local validation and its limits remain in sensitivity-validation.json.
- **Summary:** Clarify local/global inference, finite provider regression, rank limits, noise and nuisance parameters, hand-wrench maps, ensemble probabilities and held-out evidence. Ten Flash preparation/test/editorial/record helpers read and adjudicated; lead retains scientific decisions. Only Chapter 21 credited; 109 source audits plus whole-book review remain.
- **Next step:** None for this delivered chapter. Lease and presence released; receipt in reports/technical-review/sensitivity-remote-main-receipt.json. Chapter 8 remains separately in review.

### DL-#4801 · Two-Link Coordinates, Reactions, and Limits

- **State:** shipped
- **Owner:** codex
- **PR:** #4804 (regular, combined Chapters7/19; child4805 merged into topic only)
- **Issue:** #4801; epic #4009 / corpus #4021
- **Branch:** fix/pendulum-rigor-4801
- **Paths:** articles/proximal_distal_companion/chapters/ch07_one_pendulum_to_two.qmd, tests/test_pendulum_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 (`29aa7fe9dc553d81ef5fd14a13653c09675f2d36`); PR4804 exact-head CI36992387220 succeeded; all39 owned paths and whole parent tree match accepted a931f3e. Local regression and marker checks are retained in the frozen review/validation records.
- **Summary:** Correct coordinate/input maps, moving-hand force balances, energy/velocity interpretation, singular limits, underactuation and evidence scope. Preserve153 prior findings; eight new findings bind exact accepted source;161total;110corpusfiles pluswholebookreview remain.
- **Next step:** None for this delivered chapter; see active Chapter21 issue4806 and corpus4021 for remaining work.


### DL-#4799 · Model Comparison and Evidence Boundaries

- **State:** shipped
- **Owner:** codex
- **PR:** #4804 (regular, combined Chapters7/19; child4805 merged into topic only)
- **Issue:** #4799; epic #4009 / corpus #4021
- **Branch:** fix/model-ladder-delivery-4799
- **Paths:** articles/proximal_distal_companion/chapters/ch19_model_ladder.qmd, tests/test_model_ladder_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 (`29aa7fe9dc553d81ef5fd14a13653c09675f2d36`); PR4804 exact-head CI36992387220 succeeded; all39 owned paths and whole parent tree match accepted a931f3e. Local regression and marker checks are retained in the frozen review/validation records.
- **Summary:** Eight scientific corrections qualify capabilities, port power, hidden state, implementation independence and inference. All 145 prior findings preserved; eight new findings bound to exact source blobs; 111 corpus files remain; eight supplied-text Flash helpers reviewed. Exact commands and reading/visual scopes in model-ladder-validation.json and model-ladder-review.md.
- **Next step:** None for this delivered chapter; see active Chapter21 issue4806 and corpus4021 for remaining work.


### DL-#4769 · Speed, Energy, and Power Review

- **State:** shipped
- **Owner:** codex
- **PR:** #4770 (regular; merged to main as099dc2cbf)
- **Issue:** #4769 (epic #4009)
- **Branch:** fix/speed-energy-rigor-4769
- **Paths:** articles/proximal_distal_companion/chapters/ch05_speed_energy_power.qmd, scripts/make_proximal_distal_companion_figures.py, tests/test_speed_energy_review.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (6,382 full-regression passes;two temporary-root failures resolved, six root retests pass;12 gates;223-page PDF/HTML;4 browser profiles;8 findings bound to 4c80a4a26d060791b7d3505d0a27a5657c6a2eed;79 preserved;119 sources pending); final-head CI36929938103 passed, all23 changed blobs verified on remote main, lease/presence released; receipt reports/technical-review/speed-energy-remote-main-receipt.json.
- **Summary:** Correct point/body energy, power-conjugate motion and whole-club/shaft/head accounting; qualify evidence and counterfactual inference. Preserve79 earlier findings; Chapter5 complete; the broader corpus and whole-book audits continue under epic #4009.
- **Next step:** None for this delivered scope.


### DL-#4766 · Patent Catalog Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** #4768
- **Issue:** #4766 (epic #4009)
- **Branch:** fix/patent-catalog-rigor-4766
- **Paths:** articles/Launch_Monitor_Technology_Review/sections/appendix-d-patent-compendium.tex, articles/Launch_Monitor_Technology_Review/sections/07-patents.tex, articles/Launch_Monitor_Technology_Review/references.bib, articles/Launch_Monitor_Technology_Review/preamble.tex, articles/Launch_Monitor_Technology_Review/main.pdf, articles/Launch_Monitor_Technology_Review/research/patent-catalog-review-20261001.md
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (PR4768 merged as55f21d8fb; all22 bound blobs identical; final-head CI Standard and textbook builds passed; patent-remote-main-receipt.json)
- **Summary:** All 168 references plus Gazette adjudicated; 14 grouped corrections; 64 completed Flash jobs with failed attempts excluded. Two audited sources credited;120 full-source audits plus whole-book consistency remain.
- **Next step:** Complete; all22 bound paths verified on remote main55f21d8fb; issue closed and lease/presence released.

### DL-#4774 — Moving-Base Mechanics

- **State:** shipped
- **Owner:** codex
- **PR:** #4782
- **Issue:** #4774
- **Branch:** fix/moving-base-rigor-4774
- **Paths:** articles/proximal_distal_companion/chapters/ch17_moving_base.qmd
- **Started:** 2026-10-01
- **Last verified:** 2026-10-02; remote main 4c025bbf0b822f7576f1ea60afc3d21f47945e59; final CI 36951827315 succeeds; all 20 delivered blobs match.
- **Summary:** Eight corrections bound; 96 prior findings preserved; 117 sources pending.
- **Next step:** None; delivered and verified on remote main.

### DL-#4783 — System Boundaries and Contact Work

- **State:** shipped
- **Owner:** codex
- **PR:** #4785 (regular)
- **Issue:** #4783; epic #4009 / corpus #4021
- **Branch:** fix/system-boundary-rigor-4783
- **Paths:** articles/proximal_distal_companion/chapters/ch02_choose_the_system.qmd, tests/test_system_boundary_review.py, scripts/make_proximal_distal_companion_expanded_figures.py, references/proximal-distal-energy.bib
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; 227-page PDF/HTML and four browser profiles pass; 6432-pass full run had two stale-digest failures; 71 follow-up checks pass; CI SVG CRLF mismatch corrected to bound Git LF bytes; 25 evidence checks pass.
- **Summary:** Distinguish body boundaries, contact/COM work, gravity ledgers, rigid transport, observer power and deformable load allocation. Nine findings bind e96394591; 104 prior findings preserved; 116 source audits remain.
- **Next step:** None; PR4785 delivered at0bcc9f8663ea10d3c2a846cb7443472bec69cd3f, CI36956637268 and22changed Git blobs verified.

### DL-#4771 — Measured Golfer Evidence

- **State:** shipped
- **Owner:** codex
- **PR:** #4772 (regular, attached)
- **Issue:** #4771; epic #4009 / corpus #4021
- **Branch:** fix/measured-golfers-rigor-4771
- **Paths:** articles/proximal_distal_companion/chapters/ch24_measured_golfers.qmd, scripts/make_proximal_distal_companion_expanded_figures.py, tests/test_measured_golfers_review.py
- **Started:** 2026-10-01
- **Why:** Wrong systematic-review attribution and overbroad instrument, EMG, statistical and validation claims.
- **Change:** Full Chapter 24 revision, targeted figure, four bibliography additions, manufactured covariance checks and explicit primary-source reading scopes. Nine findings bind eight exact Git blobs at f565c72885e73d9e463debc336322691f46ea11a; 87 historical findings remain intact. Chapter audit credited; 118 corpus sources plus whole-book consistency remain.
- **Last verified:** 2026-10-02; PR #4772 merged a4cf9b56c; final e58 CI 36947184666 passed; ancestry and all 22 reviewed/delivered Git blobs match.
- **Next step:** None; delivered and verified on remote main.

### DL-#4786 — Open Evidence and Reproduction

- **State:** shipped
- **Owner:** codex
- **PR:** #4788 (regular)
- **Issue:** #4786; epic #4009 / corpus #4021
- **Branch:** fix/open-evidence-rigor-4786
- **Paths:** articles/proximal_distal_companion/chapters/ch27_open_evidence.qmd, tests/test_open_evidence_review.py, references/proximal-distal-energy.bib
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; 6481-pass full run had four failures; final55affected checks,226-page PDF/HTML,four browser profiles and653titles pass. Eight findings bind028720c0a5e7ec6e298cfb4615aa98c9cf6e8c31.
- **Summary:** Separate artifact identity, numerical agreement, independent verification and empirical validation; bound provider qualification and improve connected mechanics examples. Preserve 113 prior findings; 115 audits remain.
- **Next step:** None for Chapter27: PR4788 merged8bead8523, CI36961840257 passed, all18changed blobs verified; lease/presence released.

### DL-#4789 — Biological Ambiguity and Load Inference

- **State:** shipped
- **Owner:** codex
- **PR:** #4790 (regular, attached)
- **Issue:** #4789; epic #4009 / corpus #4021
- **Branch:** fix/biological-ambiguity-rigor-4789
- **Paths:** articles/proximal_distal_companion/chapters/ch25_biological_ambiguity.qmd, tests/test_biological_ambiguity_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; source53023631e; 6497 full-regression passes; 34 editorial follow-up checks; 228-page PDF/HTML, four browser profiles, 72 math expressions and 653 titles pass.
- **Summary:** Eight bounded corrections connect wrench allocation, muscle-force inference, geometric stiffness, tendon energy and human evidence. 121 prior findings preserved; eight new findings bound; eight agy Flash helpers reviewed.
- **Next step:** None for Chapter25: PR4790 merged70a0c6422, CI36965483957 passed;21exact blobs plus clean three-way SPEC merge verified;8peer paths preserved; lease/presence released.

### DL-#4763 · Geometry Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** [#4765](https://github.com/D-sorganization/AffineDrift/pull/4765)
- **Issue:** #4763 (epic #4009)
- **Branch:** fix/geometry-rigor-4763
- **Paths:** articles/proximal_distal_companion/chapters/ch04_geometry_machine.qmd, scripts/make_proximal_distal_companion_expanded_figures.py, tests/test_geometry_machine_review.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (prior full validation retained; main integration preserves55 delivered findings within79 and6 ground-reaction findings; preload/shaft source, archive and test parity verified; initial full run 6419 passed/3 metadata failures, 78.86% coverage; corrected digests/history and preserved generated packaging outputs; 69 recovery checks and Jest546 pass; Ruff/Black838/mypy94 pass; prior-head CI36893253026 green)
- **Summary:** Correct geometric force, power, singularity and inertia mappings; reproduce scalar allocation evidence and repair moment-arm figure. Flash support and lead scientific adjudication. Nine findings bound to source 1293c48c575b28986c41a2a826d6ed2030ba85fb;70 earlier findings preserved;122 full-source audits plus whole-book consistency remain.
- **Next step:** Delivered through merged PR #4765 on remote main 39f7553b562b6d83e5aff36d9277bbcbfcaff401; source/evidence parity verified in reports/technical-review/geometry-remote-main-receipt.json. Predecessors #4758/#4762 and issues #4756/#4759/#4763 are closed. No remaining work for this bounded review.

### DL-#4759 · Robust-Speed Technical Review

- **State:** shipped
- **Owner:** codex
- **PR:** [#4762](https://github.com/D-sorganization/AffineDrift/pull/4762)
- **Issue:** #4759 (epic #4009)
- **Branch:** fix/robust-speed-rigor-4759
- **Paths:** articles/proximal_distal_companion/chapters/ch23_robustly_fast.qmd, scripts/make_proximal_distal_companion_figures.py, tests/test_robust_speed_review.py
- **Started:** 2026-10-01
- **Last verified:** 2026-10-01 (seven new checks;64 affected;12 publication gates;653 titles;Ruff/Black837;mypy94;221-page PDF/parity/visual inspection;4 browser/theme checks;full6408 passes/29 skips/78.9% configured coverage/93.0% src)
- **Summary:** Correct risk, Pareto, sampling and causal claims; replace mismatched figure with eight-program archive and independently reproduce stored metrics. Six Flash support jobs and lead adjudication. Eight findings bound to source 4f3c2b3daec076f4c806d67e0d84768d2e0ed8fd;62 prior findings preserved;123 full-source audits plus whole-book consistency remain.
- **Next step:** Delivered through merged PR #4765 on remote main 39f7553b562b6d83e5aff36d9277bbcbfcaff401; source/evidence parity verified in reports/technical-review/geometry-remote-main-receipt.json. Predecessors #4758/#4762 and issues #4756/#4759/#4763 are closed. No remaining work for this bounded review.


### DL-#4791 — Constraint Reactions and Identifiability

- **State:** shipped
- **Owner:** codex
- **PR:** #4800 (regular, attached; original#4794 frozen)
- **Issue:** #4791; epic #4009 / corpus #4021 / companion #4059
- **Branch:** feat/technical-review-consolidated-20261002
- **Paths:** articles/proximal_distal_companion/chapters/ch06_constraints_push_back.qmd, tests/test_constraint_reaction_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; combined PR4800:6560Python passes/79.03%coverage;547Jest passes;12publication gates;Ruff/Black853/mypy95;232-page accepted PDF exact;fresh HTML and chapter math/zoom checks pass. Inherited dark-theme contrast failure retained; see model-ladder-consolidation.json.
- **Summary:** Eight corrections connect physical feasibility, work, inference, two-hand moments, shared drift and compliant limits. Preserve129 prior findings; seven agy Flash helpers reviewed. Eight findings bound to eight exact files; all129prior scientific fields and commits preserved;111corpus audits remain after Chapter19.
- **Next step:** Complete: PR4800 merged as041a83a8c;31owned paths accounted for,CI36974008090 successful. See constraints-experiment-remote-main-receipt.json. Lease/presence released; original PR already closed.


### DL-#4795 — Experimental Inference and Falsification

- **State:** shipped
- **Owner:** codex
- **PR:** #4800 (regular, attached; original#4798 frozen)
- **Issue:** #4795; epic #4009 / corpus #4021 / companion #4059
- **Branch:** feat/technical-review-consolidated-20261002
- **Paths:** articles/proximal_distal_companion/chapters/ch26_experiment_can_say_no.qmd, tests/test_experiment_design_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02; combined PR4800:6560Python passes/79.03%coverage;547Jest passes;12publication gates;Ruff/Black853/mypy95;232-page accepted PDF exact;fresh HTML and chapter math/zoom checks pass. Inherited dark-theme contrast failure retained; see model-ladder-consolidation.json.
- **Summary:** Eight corrections connect measurement, mechanical controls, causality, uncertainty and evidence. Seven agy Flash helpers reviewed. All137prior scientific findings and commits preserved; eight new findings bind eight exact files;111corpus audits remain after Chapter19.
- **Next step:** Complete: PR4800 merged as041a83a8c;31owned paths accounted for,CI36974008090 successful. See constraints-experiment-remote-main-receipt.json. Lease/presence released; original PR already closed.

### DL-#4813 · Timing, State Events, and Actuator History

- **State:** shipped
- **Owner:** codex
- **PR:** #4814 (regular); parent #4812 verified on remote main
- **Issue:** #4813; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/timing-rigor-4813
- **Paths:** articles/proximal_distal_companion/chapters/ch22_timing_state_question.qmd, scripts/make_proximal_distal_companion_figures.py, tests/test_timing_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 263c28c23c9ccc89602d0e1dd44f41be15722a99; exact-head CI37036705535 succeeded;25owned blobs and whole merged tree match cfc2; remote-main ancestry verified.
- **Summary:** Review complete state versus scalar events, transverse/grazing timing sensitivity, actuator preload and rise time, bounded provider evidence, phase-work Jacobians, prospective information and causal timing experiments. Seven Flash helper outputs adjudicated. Eight decisions bound to source 8f9ec2361fbddeda985d6adf9bcbbc37270b2bc9;185prior retained,193total;106sourceaudits pluswholebookreview remain.
- **Next step:** None for this delivered scope.


### DL-#4819 · Practical Synthesis Evidence and Causal Comparisons

- **State:** shipped
- **Owner:** codex
- **PR:** #4820 (regular, combined Chapters18/28); parent #4818 verified on remote main
- **Issue:** #4819; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/synthesis-rigor-4819
- **Paths:** articles/proximal_distal_companion/chapters/ch28_practical_synthesis.qmd, scripts/make_proximal_distal_companion_review_figures.py, tests/test_synthesis_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 merge29472661de971899bfb7cdc4a3f92b3e9eee19aa; exact-head CI37056378767 passed; all40owned blobs/whole tree/main ancestry verified.
- **Summary:** Lead accepted eight scientific decisions connecting wrench/power, hidden hand allocations, task velocity, feasible interventions, finite Pareto results, measurement limits and frontend scope. Five Flash outputs adjudicated. Source 1a7521e581bab0e6aa40df3f9bf0cb5ddafdee66 committed; eight findings bound with201 prior findings preserved,209total and103pending source audits. All44post-binding checks pass; source and binding c19ff2d993ea0a0a0f1cd8151e54b03df93d1869 are verified on remote topic with normal hooks.
- **Next step:** None for this delivered scope.


### DL-#4817 · Forward Solver Guarantees and Validation

- **State:** shipped
- **Owner:** codex
- **PR:** #4820 (regular, combined Chapters18/28); parent #4818 verified on remote main
- **Issue:** #4817; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/synthesis-rigor-4819
- **Paths:** articles/proximal_distal_companion/chapters/ch18_forward_model.qmd, scripts/make_proximal_distal_companion_expanded_figures.py, tests/test_forward_model_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 merge29472661de971899bfb7cdc4a3f92b3e9eee19aa; exact-head CI37056378767 passed; all40owned blobs/whole tree/main ancestry verified.
- **Summary:** Correct fixed-mode KKT assumptions, multiplier units, projection/work ledgers, moving-boundary compatibility, input memory, counterfactuals, evidence scope and coordinate/contact comparisons. Six successful Flash outputs adjudicated. Eight findings bound to the accepted source;193 prior companion findings preserved,201total;104 source audits and whole-book consistency remain.
- **Next step:** None for this delivered scope.

### DL-#4821 · Counterfactual Intervention and Evidence Review

- **State:** shipped
- **Owner:** codex
- **PR:** #4824 (regular); merged to remote main 037f42d4d551ff59e1661d539f5e7e49e8ca48d8
- **Issue:** #4821; epic #4009 / corpus #4021 / companion #4059
- **Branch:** fix/counterfactual-rigor-4821
- **Paths:** articles/proximal_distal_companion/chapters/ch11_counterfactual_scissors.qmd, scripts/make_proximal_distal_companion_figures.py, tests/test_counterfactual_review.py
- **Started:** 2026-10-02
- **Last verified:** 2026-10-02 full regression6636pass/29skip/187deselected/79.32%coverage; finalPDFcontents/boundaries pass; source c27c09f3b08725ba485faa81a63673484746d957; binding 53ef3b688b225be03232409a6fe737e7e5608eac verified remote;47postbinding checks pass; registration SELF. Previous checks: 2026-10-02 baseline dc1884f2084a1caaa1b135201e751e330afe24e2; four focused passes;12gates/655titles/894filequality;238pagePDF,53math,4browsercells pass;initial27affected passes plus2scratch-hygiene failures remediated with6passes; final29affected checks pass.
- **Summary:** Eight issue findings distinguish complete-state intervention, nonlinear finite effects, geometry controls, strategy comparisons and human inference. Supplied-text Flash helpers support data arithmetic and test drafting; six helper outputs lead-adjudicated; source c27c09f3b08725ba485faa81a63673484746d957 accepted and eight findings bound with209prior findings preserved. 217total;102source audits plus whole-book consistency remain.
- **Next step:** Delivered. Exact-head CI37064262227 succeeded; 23 owned blobs match and the shared SPEC update from PR4827 is explicitly verified in reports/technical-review/counterfactual-remote-main-receipt.json. No remaining work for this bounded chapter.
