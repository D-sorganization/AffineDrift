# Club-Fitting Mechanics Technical Review

Issue: [#4473](https://github.com/D-sorganization/AffineDrift/issues/4473), under corpus #4021 and epic #4009. Reviewed 2026-09-28.

## Complete Article Scope

The complete article, its mathematical examples and all three JSON examples were reviewed. The objective remains reproducible equipment counterfactuals connecting identified properties to flexible response, delivery, contact and fitting decisions. No engine integration, camera collection, physical club test or human trial was performed.

## Corrected Findings

1. **Spatial velocity and wrench conventions.** The original point-shift matrix had the wrong sign for its stated offset. Correct the angular-first point shift, name measured/expressed frames, retain pose separately and demonstrate dual wrench power invariance. A velocity at one reference point cannot silently substitute for another.
2. **Intervention and event semantics.** Separate nonzero input replay, fixed feedback policy, prescribed handle motion and zero declared input. Name the initial-state map, retained passive/boundary loads and smooth-mode/event assumptions. Compare a fixed diagnostic horizon separately from branch-specific contact, including a possible miss. Estimated net torque is not identified muscle activation.
3. **Causal limits.** Withdraw the assertion that every observed-minus-predicted residual is neural adaptation. Parameter, measurement, initialization, omitted-load and numerical errors are competing explanations. Modeling complements empirical fitting rather than making measured trials obsolete.
4. **Beam dimensions and preload.** The previous mixed displacement/torsion PDE used bending stiffness and translational mass for all channels. Separate bounded Euler–Bernoulli bending and Saint-Venant torsion, with polar mass per length and explicit boundary conditions. Replace the energy-dimension centrifugal expression with a steady radial force example. Remove unsupported universal droop, twist and acceleration ranges. Forces use their actual application points and any free couples.
5. **Beam coupling and convergence.** Replace a diagonal spring matrix presented as an element with a coupled cantilever tip stiffness and independently checked compliance. Suppressing rotation and allowing rotation are different boundary conditions. Static equivalence does not establish dynamic equivalence; no element-count default certifies convergence.
6. **Mesh factors and physical identification.** Correct signed tetrahedron volume from 1/3 to 1/6 of the scalar triple product and the first moment to 1/24. The unit tetrahedron and its translated copy check volume/centroid; analytic moments check centroid inertia. Watertight exterior geometry does not identify hollow walls, material densities or inserts. Exact polyhedron integration does not remove geometric or numerical uncertainty.
7. **Assembly frames and realizability.** Include component-to-assembly rotations before parallel-axis addition, preserve tensor off-diagonal signs and require principal-moment triangle inequalities as well as nonnegative moments. Convert g·cm² to kg·m² consistently in the synthetic example.
8. **Proposed data versus implemented standards.** Repository searches found no schemas or runtime implementation for the three wire identifiers previously advertised; all three advertised schema URLs returned HTTP 404 on 2026-09-28. Remove their nonexistent schema URLs and interchange guarantees. Keep three explicit synthetic proposals with unit quaternions, named velocity point/frames, consistent inertia axes, explicit missing fields and no engine-run claim. The sparse trajectory is expressly not dynamically validated.
9. **Statistics and downstream prediction.** Distinguish mean confidence intervals from individual-outcome dispersion; state known-normal assumptions for the arithmetic example. Name parameter-profile interventions for derivatives, contact-event discontinuities, impact/flight inputs and conditional optimization. Withhold invented carry gains, confidence claims and equipment recommendations.

## Source Verification

Primary sources were read on 2026-09-28 and registered in references/club-fitting.bib:

- [Drake SpatialVelocity](https://drake.mit.edu/doxygen_cxx/classdrake_1_1multibody_1_1_spatial_velocity.html): ordering and measured/expressed/reference-point conventions. The numerical point shift and dual power check were derived independently.
- [Delft Euler–Bernoulli treatment](https://interactivetextbooks.citg.tudelft.nl/computational-modelling/structural_linear/euler_bernouilli.html) and [element stiffness derivation](https://oit.tudelft.nl/CIEM5000/2026/lecture1/other_elements.html): small linear beam assumptions and coupled stiffness. The latter uses the opposite slope sign; the article explicitly uses positive dw/ds and transforms the conjugate convention consistently.
- [Eberly, Polyhedral Mass Properties](https://www.geometrictools.com/Documentation/PolyhedralMassProperties.pdf), revision 2009-11-03: constant-density polyhedral integration. The article's signed-tetrahedron formula and analytic simplex tests are independent derivations, not a claim that a surface file identifies manufactured density.
- [MuJoCo modeling documentation](https://mujoco.readthedocs.io/en/stable/modeling.html): compiler, coordinate and contact/constraint choices. No version-specific Drake/MuJoCo/OpenSim compatibility was tested or asserted.

The linked equipment-response protocol was inspected locally: it is a manufactured-synthetic validation proposal and explicitly supplies no fitting recommendation. New links point to existing source routes. No unsupported commercial/OEM values are retained as observations.

## Delegation and Adjudication

Four supplied-text-only agy Gemini 3.8 Flash calls completed in two parallel pairs. The initial jobs inventoried equations and JSON inconsistencies; the final jobs checked revised mathematics and inference. No tools, file edits, network access or permission bypass was delegated. The parent independently derived and tested each adopted correction.

Accepted the arithmetic factor, dimensional, axis-name, missing-schema and uncertainty distinctions. The final mathematics review correctly narrowed the center-of-mass moment-arm statement; actual force application points and free couples are now explicit. Rejected supposed defects based on excerpt boundaries, the difference between an analytical symbol and a JSON field name, an optional summary omitting a detail, and a predetermined bending-axis permutation without a declared local basis. A deterministic algorithm can produce statistical summaries of a declared ensemble; determinism itself does not contradict uncertainty.

## Validation

RED: nine independent numerical cases passed, seven article/example contracts failed. One initial JSON read used the Windows default encoding; it was corrected to UTF-8 before recording the seven substantive failures. GREEN: all 16 cases pass. Full suite: 5,593 passed, 29 skipped, 132 deselected, 92.88% source coverage. Content lint: 131 passed, four skipped. Ruff, Black (723 files), mypy (91), title case (638), tracked/current Python quality (760), citation resolution and bibliography checks pass.

Quarto 1.8.26 renders the final page. Four mobile/desktop light/dark production browser cases pass with zero serious/critical axe findings. Full-scroll inspection loads all 89 math expressions and ten display equations without math errors or document overflow. All display equations were inspected at both widths; the long preload and assembly equations were split into readable rows. Source and render evidence is frozen separately before publication. Numerical fixtures and synthetic JSON are not hardware or human validation.
