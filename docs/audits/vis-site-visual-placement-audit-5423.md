# VIS-SITE-1: Site Visual-Placement Audit (#5423)

Status: draft. Nothing here is published. Every placement below stays a draft
until Dieter approves it (epic #5427).

## Method

- Pages were found by searching the rendered `.qmd` sources on `main` for the
  five required topics: ZTCF, the kinematic sequence, the motion-measurement
  series (#5408), Alpha War (#5395) and putting.
- For each page, the current visuals were counted (figure blocks, `<img>` and
  video embeds), and the page was checked against the `_quarto.yml` render list.
- A source is "pinned" only when a UpstreamDrift (UD) artifact exists at a
  known commit or run. The run ids come from the UD figure-run map at
  b753c279, which traces the proximal-distal release figures. Anything else
  is "needs render", with the UD code or issue that would produce it.
- Priority: P1 means a concept the page cannot teach well without a visual and
  a pinned source exists; P2 means high value but a render is needed first; P3
  means useful later or blocked by a gate.

## Placement Table

| Page | Concept | Proposed visual | Source UD model/run | Priority |
| --- | --- | --- | --- | --- |
| `articles/The_Physics_of_Golf/quarto/ch06_zero_torque_counterfactual.qmd` | ZTCF: what the club does when joint torques are switched off (chapter has no figures) | Static figure: ZTCF drift against active control, from the proximal-distal release | UD docs/research/proximal_distal_energy_transfer/figures/fig_ztcf_drift_control.svg, release-preset/make_figures run 44c11639c1f3 @ b753c279 | P1 |
| `articles/zero-torque-counterfactual.qmd` | ZTCF: clubhead path under active torque against zero-torque branches (3 static figures today) | Side-by-side 3D animation: the full swing and a ZTCF branch released at the top and at mid-downswing | needs render: charts exist in UD scripts/research/proximal_distal_energy/wscg_ztcf_additivity_charts.py (UD #14440); the animation needs an accepted best-match model (UD #14442) | P2 |
| `articles/The_Geometry_of_Motion/quarto/ch07_counterfactuals.qmd` | ZTCF and ZVCF additive decomposition: total force equals ZTCF plus ZVCF (no figures) | Tip-to-tail vector diagram of ZTCF plus ZVCF at several downswing instants | needs render: UD #13624 ZTCF/ZVCF exports; AD #5122 is blocked on them | P2 |
| `articles/The_Physics_of_Golf/quarto/ch30_kinetic_chain.qmd` | Kinematic sequence: segment angular-velocity peaks from proximal to distal (no figures) | Static figure of the sequence, then a short 3D clip that highlights each segment at its peak | UD docs/research/proximal_distal_energy_transfer/figures/fig_kinematic_sequence.svg, release-preset/make_figures run 44c11639c1f3 @ b753c279 | P1 |
| `articles/proximal-distal-energy-transfer.qmd` | Kinematic sequence and energy transfer (32 static figures today, all traced) | One 3D golfer-in-motion clip synchronised with the energy-budget figure | needs render: the best-match MuJoCo model is rejected at gate G3 (UD MATCH status table), so no physically accepted motion exists yet | P2 |
| `articles/technology-motion-capture.qmd` | Kinematic sequence as measured by motion capture (no figures) | Embedded video: marker IK of a swing, face-on and down-the-line | needs render: the UD MATCH OpenSim OS9 renders come from a private licensed capture and must stay private; a public or synthetic capture is needed | P2 |
| `articles/rotation-representations-reference.qmd` | Motion measurement: Euler/Cardan angles, axis-angle and quaternions for one segment rotation (no figures) | Interactive 3D: one pelvis rotation shown in each representation, including gimbal lock | needs render: canonical metric definitions in UD #14421; series plan in AD #5408 | P2 |
| `articles/rotation-converter.qmd` | Motion measurement: converting between rotation representations | Live 3D orientation preview beside the converter inputs | needs render: an AffineDrift widget; no UD run applies | P3 |
| `articles/The_Physics_of_Golf/quarto/ch32_putting.qmd` | Putting: stroke and roll physics (no figures) | Embedded video of a putt rolling on a sloped green, with the break line | needs render: UD scripts/export_putt_scene.py writes the ud.putt_scene/1 file; no video has been rendered from it | P2 |
| `articles/putting-roll-models.qmd` | Putting: the skid-to-roll transition (no figures) | Animated ball showing skid, then pure roll, with a speed trace | needs render: UD putting_green engine (src/engines/physics_engines/putting_green) | P2 |
| `articles/green-simulation.qmd` | Putting: green slope and break (no figures) | Interactive green with break lines read from the putt scene | needs render: UD scripts/export_putt_scene.py (ud.putt_scene/1) | P3 |
| `branch:research/alpha-war-thesis` | Alpha War thesis (epic #5395, draft PR #5327); not on `main` | Figures set by the epic #5395 children, on the thesis branch | needs render: draft branch under the Assessment Board gate; publishing needs Dieter's written approval | P3 |

## Findings

- The two P1 rows can start now: both figures are already in the UD release,
  traced by run, and the proximal-distal article already embeds the same
  kinematic-sequence figure. A new placement needs a record or exemption under
  the published-figure gate (`scripts/check_figure_projection_records.py`).
- No physically accepted 3D motion exists yet. Every golfer-in-motion row waits
  on an accepted best-match model (UD MATCH, UD #14442), so #5425 and #5426
  should start from a synthetic or public source, or wait for that gate.
- The MATCH renders are derived from a private licensed capture. They must not
  be embedded on the public site.
- The putting pages have no visuals at all, and UD already exports a putt scene
  file. Rendering a video from it is the cheapest route to putting visuals.
- Proximal-distal companion chapters are excluded from the render list, so they
  are not listed here.
