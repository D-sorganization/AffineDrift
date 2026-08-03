# The Physics of Golf — development plan

**Corpus:** LaTeX, 35 files (~16,100 lines) plus a Quarto mirror of 32 chapters.
**Review:** 2026-07-31 — 157+ findings, 31+ P0 across chapters 1–23 (24–32 in progress).
**Epic:** [#3521](https://github.com/D-sorganization/AffineDrift/issues/3521)

## What is right, and should be preserved

- **`ch06` states the signature claim correctly:** `τ_total = τ_ZTCF + τ_input`. The historically
  wrong `= τ_ZVCF` identity is gone.
- **`ch06`'s "Minimum Reporting Standard for DCR" box is the strongest passage in the book** — it
  is the model for how every quantitative claim on this site should be framed.
- **`ch23` states the URDF closed-loop limitation correctly** — URDF is a tree format; SDF or
  engine constraints are the workaround.
- **`ch18` correctly identifies closed-chain inverse dynamics as indeterminate.**
- The Quarto mirror is a **good port** and is in places _ahead_ of the book — COR as a speed
  ratio, shaft frequency at 3–5 Hz, hedged smash-factor language.

## The three problems

1. **Worked examples that do not follow from their models** — at least eleven verified cases
   ([#3528](https://github.com/D-sorganization/AffineDrift/issues/3528)).
2. **Chapters contradicting each other on canonical numbers** — a "100 mph" swing evaluated at
   32 mph; ground reaction force below body weight
   ([#3529](https://github.com/D-sorganization/AffineDrift/issues/3529)).
3. **Theorems refuted by the book's own later calculations** — Coriolis power proved zero, then
   computed as 384 W ([#3530](https://github.com/D-sorganization/AffineDrift/issues/3530)).

## Priority order

1. Build integrity ([#3491](https://github.com/D-sorganization/AffineDrift/issues/3491)) — the
   master file is truncated mid-comment; five chapters have structural breaks.
2. Canonical parameter set (#3529) — most other numeric findings resolve downstream of it.
3. The numerical companion (#3528) — shares infrastructure with the Geometry of Motion companion
   (#3518). It would have caught **every P0** in this book.
4. Theorem corrections (#3530), then applied-chapter corrections (#3531).
5. Citation work — the fascia chapter especially
   ([#3506](https://github.com/D-sorganization/AffineDrift/issues/3506)).

## What this corpus needs added

- **`ch32_putting`** is a 58-line orphan, included by nothing and referenced nowhere. Putting is a
  genuine gap: Stimpmeter and green speeds (8–13 ft), the skid-to-roll transition in roughly the
  first 15–20% of the roll, capture width. Finish it and wire it into both trees, or delete it.
- **`ch09b_passive_stabilization`** (830 lines) exists in LaTeX only — website readers cannot
  reach it.
- **Aerodynamics gaps** in `ch19`: no backspin rate, no `C_d(Re)` curve, no spin decay.
- **The free moment** is entirely absent from `ch15`, a chapter about ground-driven rotation.
- **Fascia sourcing.** The chapter's rhetorical stance — separating real myofascial force
  transmission from Anatomy Trains speculation — is exactly right for this audience and is worth
  doing properly. It needs the literature already sitting unused in the bibliography.
- **Figures.** **31** `tikzpicture` figures in the LaTeX (all `\label`'d, only 3 `\ref`'d from
  prose), zero reach the web mirror, zero raster images anywhere in the book. The `62` previously
  recorded here double-counted: `\begin{figure}` and `\begin{tikzpicture}` were tallied separately
  for the same 31 figures. Full inventory and a rough plot-vs-schematic split (owner decision
  input) posted to [#3708](https://github.com/D-sorganization/AffineDrift/issues/3708).
