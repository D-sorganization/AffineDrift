# Screw Reference Review Progress

Issue #4832, epic #4009 / corpus #4021. Baseline d678f76746b5020ecd9dd65807e334b6e5bf2581; identical delivered main6b9d4574157e6d48ac4ac4edf6f59dc5d071b6ea. Complete original article read. Source edits, tests, rendering and acceptance remain pending. The earlier preparation document records concrete defects and author-transcript reading scopes. Original route snapshot is reports/technical-review/screw-reference-prior-review.json; preserve that history and all unrelated scientific findings.

## Scientific Plan

Develop the argument from instantaneous geometry through dual loads to solved forward dynamics. Explain finite displacement separately from a time-varying swing. Define pitch, the spatial velocity field and coordinate directions. Distinguish configuration-dependent Jacobian columns from home joint screws. Show an incompatible generalized-effort example whose least-squares wrench leaves a nonzero residual, then explain the chosen metric and units. Separate n-dimensional actuation from a six-dimensional wrench distribution and from any physical grip-load identification.

Retain the valid coadjoint sign. Derive a rigid-body acceleration balance, then state how coupled inertia and constraints define the multibody drift/input fields. Explain modal generalized restoring effort without inventing a canonical dual wrench. Show why retained state and input level determine affine dependence, why reactions may depend on input, and why adding wrenches does not superpose trajectories. Define the ZTCF family and instantaneous ZVCF acceleration consistently with NOTATION.md, including retained memory, contact mode and fixed plant. Match the lay explanation to those distinctions.

## Delegation and Adjudication

Four supplied-text agy CLI Gemini3.8Flash helpers: original inventory, arithmetic fixture, editorial outline and pytest draft. They have no canonical editing, claim or publication authority. Previous corrections are in screw-reference-preparation.md. The current editorial outline also conflates Chasles' finite-displacement theorem with the instantaneous twist representation, treats infinite pitch as an ordinary defined value at zero angular velocity, and suggests modal dual screws without a physical load map. Reject these. Coupled mass assembly is not simply projecting one isolated body's equation. Use a correctly declared moment origin and distinguish fixed model stiffness from biological passivity.

The test draft's numerical premises are correct; before use, add docstrings, use explicit zero relative tolerances where intended, compare exact analytical metric-scaling expressions rather than rounded values, remove the unparameterized ndarray annotation/nested helper, and add only a bounded source-contract test. Existing screw_examples tests already cover general adjoint, finite-screw and power invariance, so reuse those instead of duplicating the implementation. Draft files: screw-reference-editorial-flash.txt and screw-reference-test-draft-flash.txt in local QA. No draft output is acceptance evidence.

## Evidence and Delivery

Eight selected Modern Robotics author page transcripts were read across the preparation: twists, wrenches, space Jacobian, statics, rigid-body dynamics, singularities, manipulability and constrained dynamics. Exact links/scopes are in screw-reference-preparation.md; no full book, video/figure review or human trial. All numerical fixtures are manufactured algebra with declared units/scaling. Radar parent delivery is fully verified in reports/technical-review/radar-systems-remote-main-receipt.json. Current technical review remains unaccepted; 100 source audits plus whole-book consistency are pending.

## Revised Source and Publication Checkpoint

The complete article is revised, with eight manufactured checks (one bounded source contract, seven numerical fixtures). RED: one expected source-contract failure and seven algebra passes. GREEN: 43 combined screw tests pass. The two later agy editorial attempts failed with HTTP 429 / insufficient AI credits; they contributed no review evidence. Four completed helper outputs remain adjudicated. No credit purchase or substitute model dispatch.

HTML renders, and final four mobile/desktop light/dark cells pass with zero browser failures and zero serious/critical axe findings. All 16 displays visually inspected; all 149 math nodes finish with zero errors/lazy placeholders at both widths. Six wide mobile equations scroll to their right edges without page overflow. The initial preview failed because the deployment polyfill cleanup and route manifest were absent. Applied the existing strip_legacy_math_polyfill function and a scoped one-route manifest; retained initial failures. The legacy lay block is intentionally removed by the summary filter when frontmatter is present, so remove that redundant source block and use the visible 41-word summary (grade 9.71) plus takeaways. No whole-site browser claim or PDF claim.

Full regression/static/publication acceptance and source binding remain pending. The evidence refresh changes only current digests; the exact prior route snapshot retains historical source/review identifiers. No new audit credit yet: 100 pending.

## Accepted Source Checkpoint

Full regression passes: 6,686 passed, 29 skipped, 187 deselected and 60 warnings in 791.61 seconds; coverage 79.37%, above the configured 75% floor. A fresh task-specific --basetemp isolates this run from shared pytest cleanup. Source and bounded HTML are lead-accepted; exact commit binding, corpus transition and regular PR remain pending. The accepted review and mutable validation record contain the complete scope and initial failures.

## Bound and Integrated Checkpoint

Source 85eb432d38fd099069ddf2cdd58f45baae055d19 is frozen and pushed. Main 1edc38aaadd4e079b675df7093ee2d02d3c4ab69 integrated; seven findings and one corpus row bound, 99 audits remain. 90 affected tests and four browser cells pass. Normal integration commit/push, regular PR and remote-main verification remain pending.
