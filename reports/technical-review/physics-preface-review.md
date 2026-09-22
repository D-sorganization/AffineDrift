# Physics of Golf Preface Review

## Scope and Diagnosis

Issue [#4413](https://github.com/D-sorganization/AffineDrift/issues/4413), under
Physics #4054, corpus #4021 and epic #4009, covers the print preface in
`articles/The_Physics_of_Golf/main.tex` and the web entry point
`articles/The_Physics_of_Golf/quarto/index.qmd`.

Both complete prefaces were read against the corrected affine, counterfactual,
energy, muscle-torque and joint-modeling chapters. The print preface still
described drift as muscles going limp, called momentum a force, framed physical
effects as free assistance, and inferred late-swing control limits and elite
skill from drift ratios. The web preface was more careful, but its equation-free
definition still framed the split as inherited dynamics versus deliberate
intervention, without explaining how the selected input and state change it.
Its prior source-only review did not cover the print edition.

## Findings and Corrections

1. **P1, corrected — Meaning of drift.** Define the affine state-derivative
   equation with explicit time dependence. Distinguish its kinematic and dynamic
   components from a physical-force classification. Zero input means zero in a
   declared channel; it does not identify a flaccid physiological state.
2. **P1, corrected — Energy and control inference.** Momentum is not a force or
   energy source. Stored elastic energy has a prior source. Ideal stationary
   constraints have zero total constraint power; moving supports need work
   accounting. A high norm ratio does not establish unavailable task correction,
   a universal loss-of-control phase, or the cause of elite performance.
3. **P2, corrected — Connected reasoning in both editions.** Use the same core
   preface to connect joint geometry, moment arms, muscle dynamics, grip closure,
   support and shaft state. Explain instantaneous decomposition versus forward
   intervention and distinguish calculation, measurement and human-outcome
   evidence. Preserve the web contents, useful deep-link targets and print
   preamble; add reading links to the relevant derivational chapters.

## Argument and Evidence Boundaries

The preface presents the book's investigation, not an empirical finding that
drift dominates every golfer or that one technique reduces injury. Its equation
is conditional on affine dependence on the chosen input and on the smooth mode
being modeled. Explicit time dependence covers prescribed loads without silently
treating the system as autonomous. Changing contact or impact requires further
rules. Choosing muscle excitation rather than torque can change the state,
input dynamics and affine structure.

The revision follows the model and intervention definitions already developed
in Chapters 5 and 6, the work accounting of Chapter 10, the inverse-inference
limits of Chapter 16 and the anatomy/contact distinctions of Chapter 22.
These internal links explain the reasoning; they do not substitute for external
human validation. No new numerical performance, physiological or clinical claim
is introduced.

The definitions section of Tedrake's primary teaching notes,
[Fully Actuated Versus Underactuated Systems](https://underactuated.mit.edu/intro.html),
was read to cross-check affine dependence at fixed state/time, the role of input
bounds and the dependence of actuation statements on model fidelity. The
[Multibody Dynamics](https://underactuated.mit.edu/multibody.html) chapter was
consulted for the mechanical formulation. These sources support the modeling
framework; they do not establish a golf-specific phase law or clinical result.

## Validation and Publication Boundary

- Quarto 1.8.26 renders the entry page with the normal public configuration.
- The standard public verifier passes four desktop/mobile light/dark cases,
  with zero serious or critical axe violations.
- Full settled scrolling renders all seven MathJax expressions in each case,
  with no math errors, lazy placeholders, page/display overflow or broken local
  anchors. The former scope, analytical-idea and reader-guidance targets survive.
  Representative desktop/mobile captures were visually inspected.
- The actual unchanged book preamble compiles the isolated preface to two pages.
  Both pages were rasterized and visually inspected; no overfull box or unresolved
  reference warning remains. This is not a full-book visual acceptance.
- The title-case audit passes all 638 sources and the Quarto citation checker
  passes. Existing LaTeX structure/environment tests pass all 54 checks. No new
  behavioral code or test that merely mirrors the prose was added.
- A source-boundary comparison preserves the print preamble and material after
  the preface, and preserves the web table of contents and following project
  section. The review evidence must be bound to its committed checkpoint before
  route acceptance; protected merge and exact-main deployment remain pending.

Raw rendering artifacts stay in the local technical-review QA directory. The
durable verification record is `physics-preface-render-verification.json` beside
this report. The wider corpus remains an active review program.
