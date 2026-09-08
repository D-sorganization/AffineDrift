# Interpretation of Inverse Dynamics: Reading and Building the Manuscripts

## Current Editions

The September 8, 2026 revision distinguishes recovered net loads, reporting
conventions, contact allocation and physiological interpretation. The complete
source is `inverse_dynamics_final.tex`; its compiled companion is
[inverse_dynamics_final.pdf](inverse_dynamics_final.pdf).

The HTML file [inverse_dynamics_article.html](inverse_dynamics_article.html)
is a reading guide linking the current PDF and maintained website articles.
It replaces a broken independent conversion that had stale equations and missing
figures. The legacy `../Inverse_Dynamics_Claude.pdf` filename carries the same
current long manuscript; rebuild it from the same source rather than editing
two independent PDF versions.

The three shorter TeX editions in the parent directory offer technical, coaching
and constrained-dynamics treatments. Each now uses the same wrench, applied-load
and power conventions. Their PDF builds are checked during review; their TeX
sources remain the maintained companion artifacts.

## Technical Scope

- Recover the hand-on-club wrench from momentum balances and known external loads.
- Translate moments consistently and distinguish a pure couple from an offset force.
- Separate a reporting-point change, a changed physical wrench, and contact loads
  in a grasp-map null space.
- Account for gravity and velocity coupling once in standard inverse dynamics;
  distinguish constraint reactions and actuator allocation from muscle recruitment.
- Preserve invariant rigid-wrench power and real radial contact loading.
- Reconstruct the original aerodynamic example with explicit axes and separate
  hypothetical iron loading from the driver study and saved video displays.
- State how ground, body, grip, shaft, collision and sensing constrain different
  parts of a swing or humanoid-manipulation argument.

The original approximately 40% aerodynamic moment reduction is possible for the
specified geometry and force direction. It is not a measured seven-iron correction
or a physiological result. The original approximately 15% hand-position example
changes the physical wrench; it is not an uncertainty interval for one wrench.

## Rebuilding the PDFs

Use a TeX installation with Latin Modern, AMS packages, TikZ/PGFPlots, microtype,
hyperref, booktabs, geometry and tcolorbox. From this directory:

```bash
pdflatex -interaction=nonstopmode -halt-on-error inverse_dynamics_final.tex
pdflatex -interaction=nonstopmode -halt-on-error inverse_dynamics_final.tex
pdflatex -interaction=nonstopmode -halt-on-error inverse_dynamics_final.tex
```

Resolve references, inspect the log for overflow or unresolved labels, render
every PDF page to images and inspect the final layout. Copy the verified output
to `../Inverse_Dynamics_Claude.pdf` to keep that legacy download consistent.
Build each shorter `.tex` from the parent directory with the same three-pass
procedure. A successful compilation alone does not verify mechanics or layout.

## Review Record and Original Material

The decision and validation record is
[the inverse-manuscript review log](../../../../docs/development/technical-review/inverse-manuscript-review.md),
under issue #4291 and epic #4009. It includes corrected reviewer assumptions,
source boundaries, independent calculations and artifact checks.

`FINAL_SUMMARY.md` and `FIGURE_FIXES.md` are historical records of an earlier
version. Their old page counts and publication-readiness assertions do not
certify this revision. The two Markdown posts and twelve original JPGs in the
analysis directory document the originating questions; the revised posts explain
how to read each group without treating exploratory notes as measurements.
