# Impact Dynamics and Acoustics Review

Research epic [#4253](https://github.com/D-sorganization/AffineDrift/issues/4253),
review slice [#4254](https://github.com/D-sorganization/AffineDrift/issues/4254).
Reviewed 2026-09-07. This is the continuation record for the review; the root
`AGENT_HANDOFF.md` remains the canonical repository handoff.

## Scope and Method

This is a targeted critical literature review, not a systematic review or a
meta-analysis. Search families covered golf shaft/impact coupling, grip boundary
conditions and strain propagation, rotating-beam prestress/Coriolis effects,
modal vibration, impact-sound prediction, and perceptual feel. Searches used
primary publisher records, university repositories and author manuscripts.
Backward references were followed from the impact and acoustic papers.

Priority was given to direct experiments, explicit numerical assumptions and
reported validation limits. Search snippets locate a paper; the access status
below states what was actually inspected. Abstract-only items support only their
reported high-level conclusions. Paywalls and publisher 403/429 responses were
not treated as successful full-text reading. No quantitative pooled effect is
claimed. Personal websites, equipment marketing and coaching anecdotes were not
used to establish a mechanism.

The public theory is `articles/technology-heavy-hit-impact-coupling.qmd`, with
two included chapters in `articles/_includes/`. Preserve its existing route.
`INVENTORY.md` records software scope. Source corrections and independent
calculations supersede the former universal decoupling argument.

## Primary Evidence Ledger

| Source and Access | Relevant Evidence | Limit and Program Consequence |
|---|---|---|
| [McNally, McPhee and Henrikson 2018](https://doi.org/10.3390/proceedings2060245); seven-page publisher PDF inspected via [repository mirror](https://pdfs.semanticscholar.org/5f78/0348a8b77f80cc30e75cd04e0ca0272a63e0.pdf), sections 2–4 | Flexible-club versus free-head launch/rotation comparison; motion-driven shaft and finite contact model | Bending stiffness scaled 1.5; 40 training and 20 test impacts within 12 mm of face center; wider face maps extrapolate contact calibration. A motivating mechanism and comparison design, not a universal correction. |
| [Corke et al. 2018](https://doi.org/10.3390/app8030422); [university full text](https://pure.ulster.ac.uk/ws/files/12405099/applsci_08_00422.pdf), methods/results/discussion inspected | Clamped steel 9-iron, incoming balls, axial/torsional strain timing; limited remote-grip influence for that setup | Torsional return was near the end of contact; axial arrival was earlier but small. Distinguish local shaft behavior from remote reflection. Use the independently derived, dimensionally complete beam dispersion relation; a quoted flexural speed is not a universal calibration. |
| [Milne and Davis 1992](https://doi.org/10.1016/0021-9290(92)90033-W); [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/1517274/) inspected | Simulation plus swing-strain measurements; limited shaft-flexibility role in their study | Historical pre-impact evidence. Full numerical methods were not independently requalified here; no universal conclusion about contact or sound follows. |
| [MacKenzie and Boucher 2017](https://doi.org/10.1080/02640414.2016.1157262); [author manuscript](https://www.sashomackenzie.com/publications/MacKenzie%202017%20The%20influence%20of%20golf%20shaft%20stiffness%20on%20grip%20and%20clubhead%20kinematics.pdf), methods/results inspected | Repeated stiffness comparisons in 33 golfers; grip and shaft-recovery contributions can change together | Delivery is a mediator. Matched speed alone does not hold orientation, angular velocity or elastic state fixed. This is not an acoustic study. |
| [Brown and McPhee 2018](https://doi.org/10.3390/proceedings2060239); publisher abstract/method excerpt inspected, full text not retrieved | Fixed-free versus hand-held excitation and a compliant grip model | Identify the boundary dynamically; do not infer a participant's six-axis impedance by summing hand/arm masses from XML. |
| [Chiementin et al. 2019](https://doi.org/10.3390/app9102050); [full text](https://mdpi-res.com/d_attachment/applsci/applsci-09-02050/article_deploy/applsci-09-02050-v2.pdf?version=1558607724), Tables 2–5 and discussion inspected | Measured grip conditions alter bending modal properties and modeled hand vibration | One participant/club and a 0–500 Hz identification band. Table 3 generally increases damping with stronger grip, but the concluding sentence says it decreases. Table 1 also has head material/property inconsistencies. Do not promote these values to universal damping or audible-band head calibration. |
| [Roberts et al. 2005, Sound](https://doi.org/10.1016/j.jsv.2004.11.026); [university abstract](https://repository.lboro.ac.uk/articles/journal_contribution/Evaluation_of_impact_sound_on_the_feel_of_a_golf_shot/9570947) inspected | Subjective feel covaries with measured sound characteristics | Correlation is not identification of shaft/grip causation. Separate original-level and level-matched listening. No new numerical effect size is extracted from abstract-only access. |
| [Roberts et al. 2005, Vibration](https://doi.org/10.1016/j.jsv.2004.08.030); [publisher abstract](https://www.sciencedirect.com/science/article/pii/S0022460X04007151) inspected | Perceived feel compared with vibration at the hands | Auditory and tactile estimands require separate measurement and normalization. Do not treat a low accelerometer RMS as proof of a preferred sound. |
| [Mase et al. 2012](https://doi.org/10.1177/1754337112442782); publisher record/abstract inspected | Golf-specific finite-element and boundary-element sound prediction | Architectural precedent for radiation modeling; this review does not reproduce its solver or calibration. |
| [Delaye et al. 2016](https://doi.org/10.1016/j.proeng.2016.06.309); [published full text](https://shura.shu.ac.uk/12988/1/Senior%20modelling%20the%20sound.pdf), methods/results inspected | Titanium plate impact with BEM/Rayleigh acoustic comparisons | Pressure amplitudes and decay remained model-sensitive; mesh refinement mattered. Use the plate as an intermediate validation fixture, then independently qualify the assembled head. |
| [Sharpe 2010](https://doi.org/10.15368/theses.2010.41); [thesis abstract](https://digitalcommons.calpoly.edu/theses/272/) inspected | Plate-to-driver modeling progression explicitly reports poor driver-spectrum agreement | Retain unsuccessful validation as evidence. A realistic-sounding output is not an acceptance test. |
| [Moreira 2011](https://doi.org/10.15368/theses.2011.207); [thesis abstract](https://digitalcommons.calpoly.edu/theses/649/) inspected | Improved meshing and BEM/Rayleigh procedures, with plate experimental comparisons | Additional implementation reading; claims about generic driver/hybrid predictions do not replace equipment-specific held-out tests. |
| [Rodrigues et al. 2024](https://arxiv.org/abs/2401.17519); preprint abstract inspected | Rotating-beam bending/traction/torsion, stiffening/softening and comparison cases | Mathematical reference for later detailed reproduction. Not a golf experiment and not represented here as an independently reproduced model. |

Existing bibliography entries `roberts2001contacttime`, `petersen2009clubface`,
`mcnally2018shaftimpact` and `mackenzie2017shaft` are reused. New entries live in
`references/impact-acoustics.bib`; no duplicated citation keys are intended.
Secondary reviews are useful discovery maps but do not turn their summarized
numbers into independent experiments.

## Independent Mathematical Audit

1. With the former composite inputs, the elementary rod speed is 7500–10000 m/s;
   the stated slower range was arithmetically inconsistent. Real laminate branch
   speeds still require qualification. Steel's one-way example is shorter than
   contact, so the old lay explanation was internally contradictory.
2. The former arm term evaluates to 0.1956 kg, not 7.5 g. Its common-pivot model
   is itself only an artificial comparison. The extra lever-arm division was
   unjustified and the claimed universal bound was unsupported.
3. A finite initially relaxed spring can give quadratic short-time incremental
   impulse; damping or prestress supplies linear-order terms. Rigid coupling is
   a singular limit. Generalized torque impulse and linear ball impulse cannot
   be compared without their kinematic projection.
4. Full tensor point mobility follows directly from linear/angular impulse
   equations. Directional mass is the reciprocal of projected inverse mass,
   not the projection of its matrix inverse under a different constraint.
5. Tensile geometric stiffness and skew gyroscopic coupling have different
   energy properties. Derive rotation consistently; adding centrifugal loads
   to an already complete inertial formulation can double-count inertia.
6. A half-sine impulse fixes its peak once duration and impulse are specified.
   A launch-only COR model cannot identify that waveform or a sound spectrum.
7. A rigid-shaft comparison is not a proven ordering of flexible resonant or
   preloaded systems. The existing clipped speed-discrepancy score is not a
   mass contribution, impedance fraction or physiological measurement.

## Research Dependencies

- AffineDrift #4254: this review and corrected theory. #4255: subsequent
  evidence synthesis; remains open until qualified outputs exist.
- Tools #5069: tensor reference; #5071: old-model semantics/event audit;
  #5072: loaded shaft and grip impedance; #5073: finite contact/head modes;
  #5074: sound measurement/radiation; #5075: reports and application integration.
- UpstreamDrift #9701: inventory/design; #9703: state/wrench adapters;
  #9704: registered counterfactuals; #9705: physical/perceptual validation.

Order: verified contracts → loaded-structure identification → coupled contact →
qualified radiation → controlled perception → synthesis. Signal-ingestion and
experimental planning can proceed alongside structural work. Production sound
claims depend on all relevant validation stages.

## Continuation State

- Workspace: `C:/Users/diete/Repositories/AffineDrift-impact-acoustics`.
- Branch: `docs/4253-impact-dynamics-acoustics`; base `39fa6cca`.
- Implementation commit: `SELF`; PR #4258; initial implementation `cd0afdfa1a8fa7eda60377282dd4afc4965cd1b6`.
- Completed locally: source review, primary evidence ledger, rewritten theory,
  new references, RED publication regressions followed by 5 passing tests.
- Validation: full pytest 4,468 passed / 30 skipped / 4 integration failures;
  all four repaired (evidence digests and QA artifact location), with 37 affected
  tests passing on rerun. Coverage 92.51%. Ruff, Black, 622-source title check,
  SPEC and trust-evidence checks pass. Quarto HTML render succeeds; 93 math
  expressions have zero MathJax errors and no page overflow at 1440/390 px.
  The existing page template blocks its external polyfill under CSP and warns
  about preloads; rendered math still succeeds. Local QA artifacts/logs stay
  under this directory and are not publication evidence.
- Delivery is in PR #4258; normal protected checks/review remain pending. Parent
  research epics remain open; no physical/perceptual experiment was performed.
- Preserve original checkouts, including AffineDrift generated untracked files
  and UpstreamDrift's modified vendor entry. Work occurs in isolated worktrees.
- Do not reuse frozen ControlTower campaign checkpoints as new outcomes or
  touch its WSL storage/recovery state. No experiments with people were run.
