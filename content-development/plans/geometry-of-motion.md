# The Geometry of Motion — development plan

**Corpus:** LaTeX Volumes 0–V (77 files, ~31,600 lines) plus a Quarto mirror covering only
Volumes 0–II (28 files).
**Review:** 2026-07-31 — 350 findings, 50 P0.
**Epic:** [#3509](https://github.com/D-sorganization/AffineDrift/issues/3509)

## State of each volume

| Volume | Subject                               | Health                                                                                                                                             |
| ------ | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | Mathematical foundations              | **Worst in the corpus.** Wrong signs in the core identities everything else uses. Chapters 1–3 (linear algebra, state space, manifolds) are clean. |
| I      | Affine / superposition theory         | Conceptually correct, mathematically unreliable. The prose is well ahead of the equations.                                                         |
| II     | Trajectories, stability, optimization | Central theorem self-defeating; accessibility errors.                                                                                              |
| III    | Biomechanics                          | Three of five code listings produce wrong physics. Chapter 6 is exemplary.                                                                         |
| IV     | Human motor control                   | Citation layer collapsed; two canonical results stated backwards.                                                                                  |
| V      | Software platform                     | Calls none of the engines it is about.                                                                                                             |

## What is right, and should be preserved

- **Volume I Theorem 3.1** states the affine claim correctly — affine in the input at a frozen
  state, incremental map linear, with an explicit warning that trajectory superposition is false.
  This is the reference formulation; other content should be brought into line with it.
- The refuted `τ_total − τ_ZTCF = τ_ZVCF` identity is **absent** from Volumes I and V.
- **Volume III chapter 6** correctly and repeatedly states that inverse dynamics yields net joint
  loads only. Follow its hedging style.
- Volume I ch03b is clean; ch07's golf sections are well hedged.
- Volumes III–V honestly disclose that they are PDF-only on the web. That is the right pattern.

## Priority order

1. **Build integrity first** ([#3491](https://github.com/D-sorganization/AffineDrift/issues/3491)).
   No volume compiles. One missing `\providecommand{\dd}` blocks all six.
2. **Volume 0's sign errors**
   ([#3510](https://github.com/D-sorganization/AffineDrift/issues/3510),
   [#3511](https://github.com/D-sorganization/AffineDrift/issues/3511)) — they propagate into every
   other volume.
3. **The numerical companion**
   ([#3518](https://github.com/D-sorganization/AffineDrift/issues/3518)) — estimated to resolve 10
   of Volume I's 15 P0s and two thirds of Volume 0's findings.
4. Per-volume corrections (#3512–#3517).
5. Notation unification ([#3522](https://github.com/D-sorganization/AffineDrift/issues/3522)) —
   blocked on the `NOTATION.md` owner decision.

## What this corpus needs added

- **Validation against Pinocchio** for `Ad`, `ad`, spatial cross products, spatial inertia,
  `exp`/`log` on SE(3), RNEA, ABA and CRBA. A single machine-checked conventions-and-identities
  module would catch roughly two thirds of Volume 0's findings.
- **Volume V made real** — one genuinely executing chapter (Pinocchio, with an `ID(FD(τ)) = τ`
  round-trip assertion) would do more for credibility than fixing every P2 in the volume. Or
  rewrite the preface to describe what the volume actually is: a from-scratch NumPy treatment,
  which is legitimate and useful, just not what is currently advertised.
- **Web coverage disclosure.** Volume 0 on the web is 1,841 lines against 12,102 in the book —
  about 15%, with Rodrigues, the SE(3) log, BCH, Chasles, Plücker, CRBA and the RNEA/ABA
  derivations all absent, and nothing saying so.
- **Volume II's golf case study** is a 50-line stub containing no numbers. Fill it or drop the
  promise.
- **Volume IV's missing standard material**: Fitts's law, schema theory, contextual interference,
  the retention/performance distinction.
- **Figures.** 102 figure/TikZ environments exist in the LaTeX and **zero** reach the web mirror.
