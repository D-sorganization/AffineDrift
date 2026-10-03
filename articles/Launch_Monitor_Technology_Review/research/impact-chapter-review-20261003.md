# Impact Chapter Review Research — 2026-10-03

Issue #4842; epic #4009 / corpus #4021. Active worktree `AffineDrift-impact-chapter-review`, branch `fix/impact-chapter-rigor-4842`, baseline `4d5c21bcb389dda237d810d50de257dcb84d015a`. Passive-control PR #4841 is still awaiting CI/merge. No impact source acceptance or corpus credit yet.

## Coordination and Reading Scope

Claim check found no held lease. Issue lease receipt 5966690690 and central presence receipt 5966690853 expire at approximately 09:17 UTC. The central inbox is incomplete because of malformed comments and board limits; its empty session list is not proof that no peers exist. Only the claimed chapter, bounded bibliography/PDF dependencies and its review evidence are owned. Routine agy Gemini 3.8 Flash is unavailable after two insufficient-credit failures; no new helper output is claimed.

The complete original Chapter 3 has been read. Existing preparation is in `docs/development/technical-review/impact-chapter-next-review-preparation.md`. Also read the existing impact reference's contact mobility, scalar restitution, launch weighting, spin-axis frame and coupled launch/spin sections. Chapter 2's reference-point/sign conventions were read through the parameter tables and directness hierarchy; its other claims are not accepted by this review. The book's CONVENTIONS.md requires preserved labels/keys, sentence-per-line prose, a common bibliography and explicit source provenance.

## Additional Primary Reading

[Henrikson et al. (2020), DOI 10.3390/proceedings2020049027](https://doi.org/10.3390/proceedings2020049027): publisher fetch failed with HTTP429, but an eight-page primary-paper copy at https://pdfs.semanticscholar.org/85d6/34c59fa8658a17fae5044d5c17c0fd8deed8.pdf was read throughout. Pages 3 and 7 were visually inspected, including Figures 6–7. The stated model uses constant friction, adjusts incident speed for normal inelasticity, and assumes a fixed impact surface. The plate comparison and player-data comparison have different conditions. Figure 6's friction effect depends on incidence; Figure 7 illustrates force reversal. The printed page-3 mean-error inequality is greater-than 1 degree; do not silently change it to less-than or claim a verified sub-degree bound. No raw-data reanalysis or independent reproduction of its contact solver was performed. All four authors are visible on the title page; the current bibliography lacks that field.

[Tutelman, gear effect part 1](https://www.tutelman.com/golf/ballflight/gearEffect1.php): main text, equations and table read again; images and linked datasets not inspected. The unit conversion and Equation 2a contain no extra factor of 100. The historical ratio spread is a sample statistic, not total prediction accuracy. The velocity-to-spin step assumes synchronization at separation and neglects coupled tangential recoil; retain it as a bounded heuristic, not a general impact solution. Existing one-inch/150-mph trajectory numbers are author model outputs, not independent measurements.

[Tutelman, 3-D launch model](https://www.tutelman.com/golf/ballflight/3dlaunch.php): complete main-page reading recorded previously; opening reread here. The historical coordinates and approximations must not be identified silently with modern target-frame angles. Linked inverse model/appendix and image pixels remain outside the reading scope.

## Derivation Plan

Use a right-handed forward/up/right basis, retaining positive horizontal angle to the right and positive elevation upward. Keep the monitor's declared reference point and time separate from contact-point incident velocity. Reconstruct the latter with rigid-body point transport; use a separate symbol for it in the collision equations.

Derive the full spherical dot product for obliqueness. For the centered, initially nonspinning, isotropic, fixed-normal contact idealization, derive the spin direction from the tangential impulse moment. The cross product degenerates for parallel vectors. Use an outgoing-velocity/up-based frame for signed tilt; a generic three-dimensional spin vector can also have an axial component.

State the normal contact effective mass and conditional restitution impulse before distinguishing normal ball velocity from speed norm. A tangential impulse changes both launch and spin: independently fitted scalar rules need a consistency check. A fixed mass/COR cosine table is an illustrative normal-component ratio, not a measurement rejection threshold.

Retain all existing labels, correct the diagram arithmetic, bound source-specific fits and derive the inclined-plane low-point example with its plane-side and angle conventions. Tests should exercise numerical counterexamples and conservation/geometric identities, without adding a duplicate general-purpose contact solver.

## Dependency Plan

Thirty-two frozen parent files match at this new checkout. Two planned dependencies (the book bibliography and PDF) belong to the radar acceptance. Before changing either, preserve the old standalone review/delivery records and immutable historical hashes. Add an explicit carry-forward record linking old and new versions and the unchanged radar source. Verify the radar chapter's rendered text after rebuilding. Do not silently refresh its old verification commit or claim a new review of every book chapter. The remaining thirty frozen files must remain byte-exact.

Inventory inspection clarified the dependency mechanism: neither this LaTeX chapter nor the radar chapter has a route in the 251-route website claim inventory. Radar acceptance is a standalone source/PDF record, with `trust_inventory_unchanged: true`. Keep that ledger untouched rather than inventing a route or mutating a nonexistent prior route record. New source acceptance will use a dedicated immutable evidence receipt and exactly one corpus row; the old radar receipt continues to describe its historical version.

## Initial Regression Evidence

The first six-case run failed the existing diagram arithmetic, the extra gear factor and the universal-instrument/smash claims as intended. Two independent impulse/unit checks passed. A fourth failure was a mistyped expected inclined-plane angle in the new test (2.895299 rather than the independently calculated 2.8953337877 degrees); that expected value was corrected before editing the chapter. Preserve `impact-chapter-red.txt` as the initial record, not as evidence that all four failures belonged to the old source.
