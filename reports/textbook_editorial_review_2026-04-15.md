# Textbook Editorial Review - 2026-04-15

Run context: recurring textbook review automation for AffineDrift.

Primary scope:

- Drifter Manifesto overview: `pages/drifter-manifesto.qmd`
- Dynamics / Control Is Motion: `books/control-is-motion.qmd`, `articles/tangent-hyperplanes-series/part-2-dynamics.qmd`, `articles/The_Geometry_of_Motion/Volume_II/`
- Golf biomechanics and modeling: `articles/The_Physics_of_Golf/`, `articles/The_Geometry_of_Motion/Volume_III/chapters/ch05_multibody_bio.tex`

## Commissioning Verdict

The material is promising but still uneven as a publication program. The strongest pieces are the local mathematical explanations: control-affine decomposition, variational dynamics, transverse stabilization, and the biomechanical motivation for moment-arm mappings. The weakest publication risks are overconfident explanatory language, model-dependent numerical claims presented too broadly, and inconsistent citation provenance between the web-facing Quarto sources and the LaTeX manuscripts.

This run moved the corpus toward a publishable standard by making the authorial contract more explicit: established control theory is separated from AffineDrift diagnostics, finite-perturbation claims are separated from variational equations, and golf DCR language is framed as model-dependent rather than universal.

## Direct Source Edits Made

### Drifter Manifesto

Edited `pages/drifter-manifesto.qmd`.

Changes:

- Reframed the overview as a research program rather than a completed theoretical foundation.
- Split provenance into three layers: established nonlinear control, AffineDrift counterfactual diagnostics, and golf-specific hypotheses.
- Replaced the malformed control-affine notation with `\(\dot{x}=f(x)+G(x)u\)`.
- Added a notation baseline covering `x=(q,\dot{q})`, `f(x)`, `G(x)u`, and the need for hybrid or compliant models outside smooth phases.

Publication impact:

- Readers now get a clearer contract before entering the theory sequence.
- The page no longer implies peer-reviewed validation for ZTCF, ZVCF, or DCR.

### Dynamics / Control Is Motion

Edited:

- `books/control-is-motion.qmd`
- `articles/tangent-hyperplanes-series/part-2-dynamics.qmd`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch04_orbital_stability_and_transver.tex`
- `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`
- `articles/The_Geometry_of_Motion/geometry_of_motion.bib`

Changes:

- Replaced the global-sounding "hidden linearity" claim with a precise statement about first variations along a reference trajectory.
- Replaced barred Unicode notation with `x^*(t), u^*(t)` in the dynamics article.
- Introduced the residual term `R_2(delta x, delta u)` so the finite-perturbation limitation is explicit.
- Clarified that superposition is exact for the variational equation, not for finite perturbations of the original nonlinear system.
- Corrected the Shiriaev, Freidovich, and Gusev citation to IEEE TAC 55(4), 893-906, DOI `10.1109/TAC.2010.2042000`.
- Added Hauser and Hindman 1995 maneuver-regulation citation and included it in the transverse-linearization theorem citation chain.
- Corrected the Control Is Motion overview from "Shiriaev et al., 2005" to the 2010 transverse-linearization reference.

Sources checked for citation correction:

- Shiriaev, Freidovich, and Gusev DOI: https://doi.org/10.1109/TAC.2010.2042000
- Hauser and Hindman DOI: https://doi.org/10.1016/S1474-6670(17)46893-5

Publication impact:

- The core dynamics claim is now defensible in a graduate-level nonlinear-control context.
- The citation chain better supports maneuver regulation, transverse linearization, and orbital-stability claims.

### Golf Biomechanics and Modeling

Edited:

- `articles/The_Physics_of_Golf/main.tex`
- `articles/The_Physics_of_Golf/chapters/ch05_affine_structure.tex`
- `articles/The_Physics_of_Golf/quarto/ch05_affine_structure.qmd`
- `articles/The_Geometry_of_Motion/Volume_III/chapters/ch05_multibody_bio.tex`

Changes:

- Replaced the preface's broad "5:1 to 30:1" impact claim with model-dependent language.
- Clarified that high DCR does not mean the golfer is passive at impact.
- Added citations to Isidori and Bullo/Lewis for control-affine form.
- Added smooth-phase scope language for the affine model, noting impacts and discontinuous contact require hybrid or compliant extensions.
- Recast DCR as a diagnostic requiring a norm or weighting matrix rather than a coordinate-free scalar.
- Added a weighted DCR definition with `W`, `u_max`, and `epsilon`.
- Replaced "elite golfers maximize DCR" with the more defensible claim that skilled golfers exploit high-DCR phases.
- Corrected the bi-articular muscle discussion: energy transfer does not occur "without metabolic cost"; cost depends on activation, contraction velocity, and force history.
- Corrected moment-arm notation from a dot product to column-vector scalar multiplication and cited Zajac/Delp for the muscle-to-generalized-coordinate bridge.

Publication impact:

- The golf chapter now makes fewer coach-like claims and more model-auditable claims.
- The biomechanics chapter no longer overstates bi-articular energy transfer.

## Remaining Editorial Risks

High priority:

- Several later golf chapters still use "negligible control" and "ballistically committed" language. Those claims should be tied to the same weighted DCR definition or softened.
- The LaTeX and Quarto versions of The Physics of Golf are not consistently synchronized. Future runs should continue editing both when the same chapter exists in both formats.
- Generated or stale artifacts such as `.bbl` files may still carry older bibliography output until the textbooks are rebuilt.

Medium priority:

- The Control Is Motion book page uses prose citations rather than Quarto citation keys. This is acceptable for now, but a future pass should add the cited maneuver-regulation and hybrid-zero-dynamics references to the global Quarto bibliography through the repository's bibliography data pipeline.
- The tangent-hyperplanes series still uses barred Unicode notation in adjacent parts. This run fixed Part 2 only.
- DCR examples should state the selected norm, acceleration block, torque bound, and segment parameters wherever a numerical regime is reported.

Low priority:

- The Drifter Manifesto page is still raw HTML, which makes citation rendering and semantic structure harder to maintain than native Quarto.
- Some "In Plain Language" passages remain rhetorically useful but should be checked for scientific precision before a print edition.

## Next Recommended Pass

Focus on The Physics of Golf chapters 6, 8, and 14. They still contain late-downswing control-language that should be brought into alignment with the revised DCR definition in Chapter 5.
