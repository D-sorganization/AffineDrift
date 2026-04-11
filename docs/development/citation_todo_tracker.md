# Citation TODO Tracker

## Issue
#2346: 35 TODO markers requesting citations in Physics of Golf textbook.

## Status
- Total TODOs found: 15 files
- Priority: HIGH — textbook credibility depends on proper citations

## Files Requiring Citation Attention
- `articles\The_Physics_of_Golf\quarto\ch02_language_of_motion.qmd`
- `articles\The_Physics_of_Golf\quarto\ch03_double_pendulum.qmd`
- `articles\The_Physics_of_Golf\quarto\ch04_forces_and_torques.qmd`
- `articles\The_Physics_of_Golf\quarto\ch07_constraint_forces.qmd`
- `articles\The_Physics_of_Golf\quarto\ch10_energy_transfer.qmd`
- `articles\The_Physics_of_Golf\quarto\ch11_flexible_shaft.qmd`
- `articles\The_Physics_of_Golf\quarto\ch13_interdisciplinary.qmd`
- `articles\The_Physics_of_Golf\quarto\ch18_inverse_dynamics_parallel.qmd`
- `articles\The_Physics_of_Golf\quarto\ch19_aerodynamic_drag.qmd`
- `articles\The_Physics_of_Golf\quarto\ch20_soft_tissue_pliable.qmd`
- `articles\The_Physics_of_Golf\quarto\ch21_spine_modeling.qmd`
- `articles\The_Physics_of_Golf\quarto\ch23_dof_urdf_models.qmd`
- `articles\The_Physics_of_Golf\quarto\ch29_joint_damping_friction.qmd`
- `articles\The_Physics_of_Golf\quarto\ch31_swing_plane_launch.qmd`
- `articles\The_Physics_of_Golf\quarto\glossary.qmd`

## Citation Style
Use Quarto's `[@key]` syntax pointing to `references.bib`.
Example: `[@trackman2022]` for TrackMan radar data citations.

## Priority Citations Needed
1. Ball flight equations (D-plane model)
2. Stimpmeter deceleration coefficients
3. Club face angle sensitivity values  
4. SO(3) tangent space identification proofs
5. Euler-Bernoulli beam references

## Action Items
- [ ] Identify canonical sources for each TODO
- [ ] Add BibTeX entries to references.bib
- [ ] Replace TODO markers with @cite keys
- [ ] Run `quarto render` to validate citations
