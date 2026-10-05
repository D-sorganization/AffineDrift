# Final Partial-Source Review — #4954

## Scope and Decisions

Complete source review of both ch28_impact_collision editions, intentional-constraint-collapse, inverse-dynamics and inverse-dynamics-inference, including their shared mechanics includes. These five rows previously recorded targeted corrections only. Reconcile book wrappers with the separate accepted chapter receipts; manuscript availability remains distinct from empirical validity or notebook completion.

Correct the spin-loft symmetry statement: global paths -3/+3 degrees preserve spin loft only with face azimuth zero; for a nonzero face use symmetric offsets about that face. The printed normal-only cosine and squared-cosine scalings hold at fixed coefficient C and incident speed. Changing strike, normal or inertial boundary may change C.

The intentional-constraint-collapse title now states a hypothesis, not an established mechanism. Inverse dynamics identifies model-dependent net generalized loads, not unique muscle forces or intent. The inference article uses the full generalized input map bar B consistently and requires the inverse-dynamics load to lie in its range. Shared energy accounting assigns dissipation and external ports once, with conservative forces already represented by potential energy.

Volume II's preface incorrectly called Volume III Chapters 4–10 outlines. Its ten chapters now contain provisional technical treatments with separate review receipts. Correct that availability statement without claiming biological validation. Digest-only book dependency carry-forward preserves historical route dates/revisions; prior canonical record and exact digest replacements are retained locally in this directory.

## Independent Verification

independent-checks.py.txt and independent-checks.json test eight groups of 100 seeded manufactured cases: impact momentum and energy loss, spin-loft symmetry, wrench power, constrained accelerations and reaction work, actuator consistency and external energy bookkeeping. All errors are below 1e-10. A nonzero-face counterexample produces 12.3724558 versus 9.7044746 degrees for globally symmetric paths. These are mathematical checks, not human experiments.

All 62 focused tests pass. Physics PDF (534 pages) and Geometry II PDF (103 pages) build with repeated LaTeX/BibTeX passes. The entire corrected impact chapter, physical PDF pages 225–229, and Volume II preface page 3 were visually read. Filename chapter 28 is typeset as Chapter 17 because of the book's input ordering. Existing title hyphenation/section-number spacing remains readable; no whole-book typography certification is claimed. Seven scoped Quarto builds pass. Browser results are recorded separately before final acceptance.

## Helper and Source Adjudication

Five successful agy Gemini 3.8 Flash jobs reviewed impact/impedance, inverse dynamics, two halves of the book-input inventory and the final prose diff. Helper output is advisory. Rejected false sign objections: forward/up/right coordinates give positive-z backspin and v cross n; wrench translation preserves paired power. A parameter-varying spring's energy derivative legitimately includes half k-dot e-squared. Full column rank does not imply full row rank; rectangular input consistency is explicitly required. The final diff audit returned no findings.

Book-inventory helpers correctly found wrapper bookkeeping but incorrectly equated route-clearance limits with an incomplete scientific review for Physics Chapters 9 and 18; their complete chapter receipts must be retained. Issues 4950/4954 are issue numbers, not PR numbers. Notebooks remain scaffolds and immutable upstream publication rows retain their separate authority.

Primary reading this batch: relevant transcripts of Modern Robotics 8.7 Constrained Dynamics and 3.4 Wrenches, covering workless stationary constraints, projection and wrench power/transport. Prior chapter references remain qualified; no new claim of full primary-paper access is made. One Underactuated manipulator URL failed and its alternate page was only opened, not fully read.

## Turnover and Acceptance

Integrate tail repair 931e7f9b2, then freeze the combined tree and run full regression and central pre-PR/source gates. The earlier tail full run had two metadata failures and regenerated tracked files; it is not a passing receipt. Preserve those failed logs and the 56-test successful repair receipt. Advance the 26 tail rows and these five source rows only after combined acceptance.

Create one regular main-targeted PR closing #4950 and #4954; respect #4953's existing merge-queue position. Never re-arm or update a green queued PR, bypass protection/hooks, or close another session's PR. Verify protected remote-main and deployment separately from local review before declaring the epic complete.

## Accepted Local Checkpoint

Source07c71ed50050253a082189e87ab569673a7d286f passed all 7,283 tests,
29 skipped, 210 deselected, 60 warnings, 93.31% coverage in 512.85 seconds.
Tracked tree stayed clean. The 19 extra source gates initially passed 18: only
root hygiene failed because packaging tests created untracked build/dist/egg-info.
Those directories were verified contained and untracked, moved intact under QA,
and unchanged root hygiene then passed. Failed logs are retained.

Seven HTML routes were scrolled at 390/1440 widths: no document overflow or
MathJax errors. Lazy first captures omitted equations; subsequent scroll-through
views show 41/65/60/586/548/108 math containers in the six root articles. Corrected
equations and prose were inspected in final mobile captures and the desktop
energy viewport. Long equations remain horizontally scrollable; preview update
notifications, CSP and absent-manifest messages are known limits.

The final acceptance report advances 26 tail rows plus five targeted-only rows,
and reconciles five already reviewed book wrappers with 131 direct input entries
across eight print books. All 407 paths remain represented, with zero Indexed or
Targeted-only prefixes. This count is not empirical certification or a count of
unique articles. Preserve all 38 immutable upstream publication rows and existing
review/reading boundaries. Fix one inherited unquoted-comma CSV row without
changing its text.

Supplementary reconciliation maps 27 tracked article/page sources outside the
historical inventory to generator, include, route or full-source receipts. Both
impact includes exactly match #4720 hashes; bibliography body matches its full
#4371 review. Grip chapter TeX matches d7e51655 exactly; QMD differs only in a
resolved link and Related Articles callout. No new science claimed from those
bookkeeping checks. Six successful Flash jobs support this batch; failed tool
access/oversized prompt invocations are excluded.

PR4953 became conflicting after independently merged main5002262d3 introduced
the shared layman component. Its resolution is isolated in the consolidation
worktree. Integrate that checked resolution here before final delivery, preserving
source acceptance and explicitly recording component-only hash amendments.
