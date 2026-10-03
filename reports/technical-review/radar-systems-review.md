# Radar Systems Chapter Review

Issue #4831; epic #4009 / corpus #4021. Baseline `802e9adc55698d6db4fd926456a1514e2966991d`. Complete original and revised Chapter 4, added bibliography entries and tests read by the lead. The complete source and bounded publication are lead-accepted on 2026-10-02. Source checkpoint SELF. Exactly one corpus row receives complete-review credit; 100 source audits plus whole-book consistency remain.

## Scientific Changes

The revised chapter explains how observations, geometry and model assumptions combine to produce launch-monitor outputs. For golf-swing analysis, shared estimator inputs can create correlated errors: agreement between an inferred face angle and its launch-direction input is not an independent test of a biomechanical explanation.

- Distinguish Doppler conversion, spectral spacing, range resolution and detection range; remove unsupported product-band assignments and a universal 24 GHz range limit.
- Include integer phase branches, half-wavelength endpoint ambiguity, restricted viewing domains, array geometry, calibration and target association.
- Bound K-LD7 interface/settings evidence and Full Swing's proposed CW/FMCW arrangements without presenting them as independent golf-shot validation.
- Project rigid-feature velocity onto the line of sight and distinguish harmonic candidates from an identified spin fundamental. The rotational velocity term vanishes for an axis along that view; this is not a universal statement about every possible scattering observable.
- Derive conditional lift extraction and fixed-axis constraints using air-relative velocity. Treat rank, normalization, sign, noise and conditioning explicitly. Changing flight direction can add spin information under an adequate constant-spin/force model; it does not guarantee observability or accuracy.
- Check US10775492B2's displayed dimensions and baseline ratio. For the manufactured example, the printed patent ratio gives 66.5868 degrees while the conditional algebraic elimination gives 30 degrees. This does not validate a replacement sensor algorithm or interpret patent scope.
- Separate measured flight, extrapolation and normalization; qualify TM4 setup distance, Garmin R10 RCT mode/fallback, Rapsodo RPT versus RCT, and X3C generation-specific instructions.
- Declare club reference point, time, frame and surface orientation. Derive local face-inverse sensitivities and common-reference cancellation while retaining collision-model and covariance limits.
- Separate pickup rate from accuracy, bound the Leach comparison to its devices/protocol, and require an explicit measurement role for each fused sensor.

## Evidence and Boundaries

Detailed derivations, primary URLs, read scopes and helper adjudications are in `articles/Launch_Monitor_Technology_Review/research/radar-systems-review-20261002.md`. External readings are explicitly partial. No full patent, legal-status assessment, new human study, sensor experiment or universal vendor ranking is claimed.

Seven scientific/preparation helpers and one additional report-drafting helper used agy CLI Gemini 3.8 Flash. The lead corrected the report helper's overstatements: changing airspeed only can add information, the invisible term is projected rotational point velocity, shared inputs are conditional rather than universal, and the corrected delay elimination must not be credited with the patent's erroneous numeric answer. Its claim that independent references are the only conceivable way to distinguish true change from artifacts was also too broad. No canonical editing or publication authority was delegated.

The eight new manufactured checks and reused related tests total 56 passing affected checks. Static checks, 898 Python quality checks, 12 publication gates and 656 title checks pass. The first full regression stopped at the existing deployment-evidence hashing test's 60-second timeout; the unchanged retry passed 6,668 tests with 29 skips, 187 deselections, 60 warnings and 79.36% coverage in 736.16 seconds. Both logs are preserved; no test or timeout was relaxed.

Only Chapter 4 receives a full new source audit. All 19 other book source/build files retain their Git blob identities; all 83 existing bibliography records are unchanged. Five entries are added; four formerly cited records remain as uncited historical background so all 88 records still print. Earlier acceptance reports remain frozen. The entire trust inventory and all 217 companion findings remain unchanged. This book has no matching rendered route, so no route record is fabricated.

The 84-page PDF contains nine chapter displays. Revised chapter pages, contents, boundaries and bibliography are inspected within the scope recorded in the render report. Existing warnings and technical claims in other chapters are outside this acceptance: Chapter 3's remaining vertical-weighting and gear-effect generalizations and Chapter 5's camera/product statements remain pending full audits. Those neighboring pages were inspected for publication continuity, not scientifically accepted.
