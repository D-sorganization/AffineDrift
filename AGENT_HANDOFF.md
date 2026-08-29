# Agent Handoff — AffineDrift

Last updated: 2026-08-28

This is current operational state. Historical detail belongs in git/GitHub.

## Merge Governance

- Use pull requests and ordinary protected merges; required status checks must pass.
- Do not require or request a named maintainer's approval when the live ruleset requires zero approving reviews. Review remains optional for risk, expertise, or unresolved feedback, but `@dieterolson` is not a standing release gate.
- Never use admin bypass, force-push, or protection changes to merge a failing or stale head.

## ZTCF Intervention Contract (#4016 — PR #4048 Open)

- Lease: `codex-20260828-affine-a5`, expiring 2026-08-29T14:44:17Z; issue
  comment `#issuecomment-5460882100` records the exact claim.
- Non-draft PR: `https://github.com/D-sorganization/AffineDrift/pull/4048` on
  `feat/4016-ztcf-contract`; hosted Python 3.12 checks are merge authority.
- `data/ztcf/ztcf_intervention_v1.schema.json` is the normative public record;
  `data/ztcf/planar_golf_forward_fixture_v1.json` pins the sole supported golden
  result to protected source `524c28926f364631ed06b15be9c6fdf440acce64`.
- `src/affine_control/ztcf_contract.py` executes only the registered planar
  Python adapter. Unavailable or engine-unsupported records fail closed;
  MATLAB, Simulink, and cross-engine parity remain explicitly unavailable.
- Canonical and paired Physics of Golf sources distinguish simulated trajectory
  difference, contribution measure, causal estimand, and physiological
  interpretation. A successful replay does not identify muscle, effort, intent,
  human strategy, model adequacy, or finite-horizon reachability.
- RED/GREEN evidence: collection initially failed on the absent contract
  module. The final focused contract passes 7 tests; 133 adjacent tests pass;
  after reconciling protected #4017, the `content_lint` lane passes 78 tests
  with 4 documented skips and the full Python 3.13 suite passes 3,343 tests
  with 30 documented skips.
  Ruff, Black,
  focused strict mypy, and diff checks pass. Quarto 1.8.26 renders both QMD
  sources; direct `pdflatex` compiles the 605-page paired book. After the final
  protected-main merge, the normative contract was re-inspected at desktop and
  mobile HTML viewports without clipping or unreadable content; the paired PDF
  page was inspected earlier in the same slice. Python 3.12 remains the
  protected lane authority.

## Ultimate Companion Planar-Scope Repair (#4015 — PR #4045 Merged)

- Epic #4008 coordinates the companion program; issue #4015 removes two
  unsupported planar 90 percent fidelity claims.
- Protected merge `7b1ccde2afb103f200e0d4a010411560471bb6f4` replaces them with an explicit
  pedagogical planar-model boundary and the evidence contract required before
  any quantitative 2-D-to-3-D comparison can be published.
- Required focused gate:
  `python -m pytest tests/test_planar_model_scope_contract.py -m content_lint -q`.
  Current evidence: 2/2 focused contracts and the complete `tests/` lane
  (3,252 passed, 29 skipped, 63 deselected) pass; Ruff, Black, focused strict
  mypy, terminology, and two isolated Quarto renders pass. The revised critic
  response was inspected at 1440 x 1000 with the disclosure expanded and has
  no overflow or clipping. All exact-head hosted gates passed before the
  ordinary protected squash merge.
- After merging protected DCR PR #4044, the combined planar-scope, DCR, and
  mechanical-claim selection passes 14 tests; the repository content-lint lane
  passes 68 tests with 4 documented skips and 3,284 deselections. Black, Ruff,
  terminology, title-case, cross-reference, display-math, and diff checks pass.

## DCR Reachability Correction (#4013 — Protected PR #4044 Merged)

- Protected merge `524c28926f364631ed06b15be9c6fdf440acce64` owns the corrected
  article, analytic counterexample in `src/affine_control/reachability.py`, and
  corpus regression
  in `tests/test_dcr_reachability_contract.py`.
- DCR is a declared magnitude ratio, not a controllability or finite-horizon
  reachability certificate. Keep `f(x)+G(x)\mathcal U(x)`,
  `G(x)\mathcal U(x)`, and `\mathcal R(T;x_0)` distinct.
- The exact constant-additive-drift scenario translates `[-1, 1]` to
  `[99, 101]` without changing width. Control-cone, drift-tube, pancake,
  timing, and face-variance conclusions remain unavailable until a governed
  event-level computation declares horizon, controls, metric, and uncertainty.
- Workstation Python 3.13 evidence before the protected-main reconciliation:
  76 focused reachability and publication tests passed; the full suite passed
  3,255 tests with 29 documented skips. After merging protected #4014, the
  combined DCR, mechanical-claim, and publication regression selection passes
  76 tests.
  Ruff, Black, strict mypy, terminology, title-case, cross-reference,
  display-math, and isolated Quarto 1.8.26 render gates pass. Python 3.12 is not
  installed in this worktree environment; do not treat 3.13 evidence as a
  substitute for the protected Python 3.12 lane.

## Ultimate Companion Scientific Repair (2026-08-28)

- Epic #4008 coordinates the AffineDrift--UpstreamDrift companion program;
  scientific trust is #4009 and the generated software companion is #4010.
- Issue #4014 merged through protected PR #4043 at
  `b427347ccd5c18182b68274538c92c1e31906174`: its
  content contract blocks torque/load/effort/muscle-cause conflation; the
  torque example now distinguishes pointwise generalized torque from power
  and work; accessible and technical force-taxonomy copy states the
  model/measurement/identifiability boundary.
- Required focused gate:
  `python -m pytest tests/test_mechanical_claim_contract.py -m content_lint -q`.
  Current evidence: 6/6 claim-contract tests and 3/3 adjacent public-content
  hygiene tests pass; the complete `tests/` lane is 3,252 passed, 29 skipped,
  and 67 deselected. Ruff and Black pass; strict mypy passes for the new test
  (the full local mypy lane lacks the optional Streamlit dependency). All four
  affected pages render to isolated HTML, and the revised appendix was
  inspected at a 1440 x 1000 desktop viewport. This protected authority is now
  part of `main` at `b427347ccd5c18182b68274538c92c1e31906174`; #4014 is closed,
  and its claim boundaries must remain intact in subsequent scientific repairs.
- Issue #4017 merged through protected PR #4047 at
  `64624ca9ff9390be0b42f5b714b021718cc4ba85`: the Physics of Golf Quarto
  and LaTeX chapters no longer add parallel sensory and motor
  pathways into a single round-trip delay or treat feedforward and feedback as
  exclusive. Short-latency (20--45 ms), long-latency (50--100 ms), voluntary
  (>100 ms), and late visually guided responses are separated from their
  task-, phase-, and outcome-dependent mechanical authority. Golf-specific
  reliance claims remain experimental pending time-locked perturbation,
  muscle, motion, and outcome evidence.
- Required focused gates:
  `python -m pytest tests/test_sensorimotor_claim_contract.py -m content_lint -q`,
  `python scripts/audit_book_citations.py --chapter ch24_motor_control_brain --check`,
  and `python scripts/check_bibliography_cross_file.py`.
- Current #4017 evidence after merging protected #4044: 11 combined #4013,
  #4014, and #4017 contract tests pass; the full default Python lane passes
  3,255 tests with 29 documented skips; the content-lint lane passes 71 tests
  with 4 skips and 3,284 deselections. Strict mypy, Ruff, Black, terminology,
  title-case, display-math, Quarto citation resolution, and cross-bibliography
  identity gates pass. Both affected Quarto chapters render in isolation and
  were inspected at a 1440 x 1000 desktop viewport with one H1, no broken
  media, and no horizontal overflow. The chapter-pair citation audit retains
  one pre-existing edition-specific Jorgensen key in each tree; both new
  long-latency citations are shared by the Quarto and LaTeX editions.

## Website Adversarial Review & Cross-Linking Program (2026-08-21)

A full adversarial review of website content, organization, and cross-article
linking was completed and converted into tracked GitHub issues. No content
changes were made in that session — the deliverable is the issue set below.

- **Cross-Article Linking Epic #3896** with sub-issues #3897–#3905 (C1–C9).
  Measured baseline: the link graph is a star through five hub pages; 53/98
  top-level content pages have zero outbound content links; all models/ and
  repositories/ pages are lateral orphans; `categories:` exists on only 12/98
  pages. Architecture decided: one canonical Related Articles component
  (theory-core callout style), controlled `categories:` taxonomy in `config/`,
  CI enforcement by extending `scripts/link-checker.py` (author-curated links,
  validated — not auto-generated), and Quarto sidebar/prev-next for series.
  Sequencing: C1→C2→C3 are the foundation; C4–C9 are per-cluster wiring.
- **Defect issues filed (verified, with evidence in each issue):**
  - #3906 (P1): monograph ch03b/c/d figure paths (`data/...`, `../figures/`)
    don't resolve from the including `index.qmd`; contract-test regex masks it.
  - #3907 (P1): 30 companion chapters + `volume2_content.qmd` are include
    partials without `_` prefix — rendered twice (assembled + untitled orphans).
  - #3908 (P1): 57 internal markdown files (governance/operations/security/
    issue write-ups) inside `docs/` are deployed wholesale to GitHub Pages.
    (72 tracked non-HTML files total; the other 15 are css/js/svg/pdf assets,
    including the intentional CI-enforced CSS mirrors — not part of the defect.)
  - #3909 (P1): sitemap generator glob is non-recursive → 82 of ~253 URLs;
    coverage CI checks only sitemap→source.
  - #3910 (P2): both textbook landing pages link zero of their own chapters;
    ch09b fully orphaned.
  - #3911 (P2): navigation coherence (models hub links no sub-pages, resources
    hub unreachable, canonical theory series absent from navbar, tools vs
    software split, books-nav sidebar inconsistency, ~20 label/title mismatches).
  - #3912 (P2): Article Index missing 9 top-level articles + 38 rendered pages.
  - #3913 (P2): tangent-space material published as four parallel sets;
    `_CRITIC` review memos and packaging artifacts render publicly (editorial
    decision required before excluding).
  - #3914 (P2): 76 rendered pages lack `title:` front matter; "Section Y"
    placeholder title; 7 "Figure Pending" TOC headings; drifter-manifesto slug
    collision (the single-file edition itself is deliberate and canonical-marked).
- **Known non-defects (do not re-file):** `inverse-dynamics` vs
  `inverse-dynamics-inference` are distinct; `passive-distributed-control` vs
  Physics of Golf ch27 are distinct; the drifter-manifesto single-file edition
  is intentional; navbar hrefs all resolve; the `../../critiques/` link works
  via browser root-clamping (hygiene only, folded into #3897).
- **Content-quality sweep issues (second wave, verified):**
  - #3916 (CI): benchmark workflow fails at collection — PyYAML missing from
    `requirements-benchmarks.txt` (pre-existing on main; noted on PR #3915).
  - #3917 (P1): ~50 `page-layout: full` pages render with no H1 (CSS hides the
    title block; pages author no hero heading); plus 7 multi-H1 articles.
  - #3918 (P1): unfinished content navbar-promoted — empty Book Reviews page,
    five self-described research-review stubs, learning-paths template
    placeholder, Volumes II–IV advertised "Start with Chapter 1" with zero
    readable chapters.
  - #3919 (P2): formatting — double section numbering (4 articles), math `|`
    breaking the rotation-converter table, 18 heading-level skips, orphan
    "Defense" TOC headings.
  - #3920 (P2): editorial residue — duplicate-content notice on
    affine-nature-golf-swing, revision-history blocks, maintainer instructions,
    tracker numbers in prose, I-vs-we voice inconsistency.
  - #3921 (P2): internal consistency — Volume I chapter titles/sources/read
    links disagree, phantom "Section N" references, empty cross-referenced
    `#sec-methods`, technology page "three instruments" above ten articles.
  - #3922 (P2): development-roadmap page stale and self-contradicting.
  - #3923 (P2): five repository/model pages describe a repository but link none.
- **Verified clean (from the same sweep — don't re-audit):** 0 unresolved
  `@sec-/@fig-/@eq-` refs; 0 unresolved `[@key]` citations against the six
  wired `.bib` files; 0 `Author1995?` artifacts; every image has alt text;
  `description:` present on all 98 top-level pages.
- Prose/style quality is owned by the pre-existing writing-quality program
  (#3821, children #3823–#3828) — the issues above deliberately exclude it.

## Publication Architecture & Proximal-to-Distal Monograph

AffineDrift is the publication home of textbooks (_The Physics of Golf_, _The Geometry of Motion_, _Volumes I–IV_), articles, and scientific monographs. UpstreamDrift remains the computational, claim, and evidence authority for the proximal-to-distal program:

- **Merged immutable refresh ([#3992](https://github.com/D-sorganization/AffineDrift/issues/3992), [PR #3993](https://github.com/D-sorganization/AffineDrift/pull/3993)):** protected AffineDrift squash
  `9b9cbcc2199f1fbf8cd281beb08c57d543b552b1` is verified as the exact
  remote `main`. It pins protected UpstreamDrift #9151/#9152 squash
  `85cce4d3307bb7ad3953d9fc6e583e370803515c`, adds the
  articulated same-state drift/contact-attribution chapter and figure, and
  stages the byte-identical 252-page, 1,980,545-byte source PDF. Local
  projection verification passes with 214 source-identical files, 21 flattened
  figures, 12 immutable-link rewrites, and 15 declared adaptations across the
  complete 262-file projection. The finding is deliberately adverse to simple
  transfer narratives: positive contact alignment with total acceleration
  coexists with negative contact power in every registered state, so the
  pointwise result is not evidence of positive work, accumulated transfer, or
  clubhead-speed gain. All protected #3993 checks passed, including the full
  Python, E2E, responsive-layout, benchmark, JavaScript, link, and quality
  lanes. Preserve the untagged-PDF, Type 3, and unembedded-font
  archival limitations unless independently fixed and requalified.
  Local validation is green for all 64 proximal--distal tests, the complete
  3,296-test non-GUI lane (3,270 passed, 26 skipped), Ruff, Black, strict MyPy,
  title governance, terminology, internal links, cross-references, isolated
  Quarto HTML rendering, and visual inspection of the new PDF treatment. The
  unfiltered Windows 3.12 suite remains collection-blocked only by the inherited
  PyQt6 `QtGui` DLL ABI in
  `tests/tools/test_wrist_universal_joint_window.py` (`0xc0000139`); do not
  misclassify that workstation dependency boundary as a publication failure.

- **Published Technical Monograph**: [`articles/proximal_distal_energy_transfer/index.qmd`](articles/proximal_distal_energy_transfer/index.qmd)
  - 37 comprehensive technical chapters (`chapters/_ch01_...` to `_ch09_...`) covering multibody mechanics, coordinate-explicit Coriolis, squared-speed/centripetal, gravity, applied, contact, and residual force sources, endpoint virtual-work mappings, multi-station Coulomb friction, and bounded optimization studies.
  - Qualified technical PDF: [`proximal_distal_energy_transfer.pdf`](articles/proximal_distal_energy_transfer/proximal_distal_energy_transfer.pdf) (252 pages, >= 69,000 words).
  - Executable companion and monograph PDF contracts use the exact governed
    `pypdf==6.16.1` root dependency pin.
  - [`source_manifest.json`](articles/proximal_distal_energy_transfer/source_manifest.json) pins the exact UpstreamDrift #9151/#9152 protected squash `85cce4d3307bb7ad3953d9fc6e583e370803515c`, the release-manifest and claim-registry digests, the embedded generation environment, and both PDF digests. Digest equality establishes provenance, not independent scientific confirmation.
  - `python scripts/verify_proximal_distal_projection.py` independently downloads or reads that authority, verifies 214 byte-identical source files, 21 uniquely mapped flattened figures, 12 normalized immutable-link rewrites, 15 explicitly hashed publication adaptations, the claim registry, and the PDF. CI also pins the complete 262-file local projection tree. Unreferenced derivatives absent from the source manifest are excluded rather than promoted.
  - The pinned profile is computational-release ready. It is not archival/PID ready: the PDF is untagged and retains Type 3 and unembedded font resources.
  - Dual web & PDF rendering registered in `_quarto.yml` (resources, `books-nav` sidebar, and `Read` navbar).
- **Lay Companion Book**: [`articles/proximal-distal-a-journey-through-the-swing.qmd`](articles/proximal-distal-a-journey-through-the-swing.qmd) (30 chapters, PDF).
- **Web Summary Article & Workbench**: [`articles/proximal-distal-energy-transfer.qmd`](articles/proximal-distal-energy-transfer.qmd) and [`articles/proximal-distal-model-workbench.qmd`](articles/proximal-distal-model-workbench.qmd).

## Shipped Technology & Biomechanics Articles

- **Club Fitting Simulation & Identification (Epic #4549, Child C9)**:
  - [`articles/technology-club-fitting.qmd`](articles/technology-club-fitting.qmd): Forward twist counterfactuals, shaft forward dynamics (lead/lag/droop), divergence theorem watertight polyhedral mesh inertia tensor integration, and OEM fitting document interchange.
- **Multibody Impact Coupling & Heavy Hit (Epic #4562, Child H5)**:
  - [`articles/technology-heavy-hit-impact-coupling.qmd`](articles/technology-heavy-hit-impact-coupling.qmd): Proves tau^2 decoupling law (contact duration ~400 us vs flexural wave transit ~2300 us), apparent striking mass decoupling fraction eta > 0.99, and MJCF/URDF/.osim model interchange.

## Research Evidence & UpstreamDrift Alignment

- **Markerless mocap authority (AffineDrift #3954, parent #3952):** AffineDrift
  owns only public pedagogy, sanitized visualization, compatibility reports, and
  immutable evidence projections. Tools owns public contracts; UpstreamDrift
  owns runtime orchestration and qualification. Use ADR 0001 and
  `affinedrift/mocap-publication-projection/v1`; never publish raw video, PII,
  secrets, AGPL components, moving links, or unqualified lab/model claims.
  Local branch `feat/3954-mocap-authority-projection` is not pushed. Python
  3.12 passes 16 focused tests plus Black, Ruff, and strict mypy; its full lane
  is workstation-blocked at collection by the inherited PyQt6 `QtGui` DLL ABI.
  Supplementary Python 3.13 evidence is 3,248 passed, 29 skipped, and 75.3%
  coverage; the isolated Quarto render also passes. No protected mocap release
  or physical-lab qualification exists yet; next pin merged Tools #4706 and
  UpstreamDrift #9063 authorities.
- **Camera evidence registry (AffineDrift #3956, #3976, #3977, #3978 / AFF-M1):**
  branch `fix/3976-camera-benchmark-evidence` qualifies and updates the evidence surface.
  The versioned registry, strict verifier, public camera-selection guide, and contract
  tests cover five cameras: FLIR BFS-U3-16S2C-CS (fast-motion USB pilot lead), Basler
  a2A1920-160ucBAS (high-res USB alternate), Allied Vision Alvium G5-203c (distributed
  8-camera 5GigE reference-rig hypothesis), LUCID Triton2 TRT016S-CC (distributed
  2.5GigE/PTP challenger), and Stereolabs ZED X One GS (long-cable GMSL2 evaluation).
  ZED X One GS synchronization evidence is refreshed to the current 15 µs vendor claim
  (#3976). Regional list prices for camera bodies are scoped typed (FLIR USD 371.00,
  Stereolabs USD 399/424) without implying total system cost (#3977). The two-camera
  USB pilot and eight-camera distributed Ethernet evaluations remain strictly distinct
  decisions (#3978). Default-deny procurement and human approval boundaries remain
  mandatory. AFF-M2 must consume protected Tools calibration contracts after their
  dependency stack merges; do not copy runtime calculations into AffineDrift.
- The protected source release is pinned to UpstreamDrift #9151/#9152 squash `85cce4d3307bb7ad3953d9fc6e583e370803515c`.
- Source release: 702 artifacts, 328 atomic claims, 2,495 evidence references, 419 local artifacts, and 78 external URLs; no source-manifest mismatch remains.
- Articulated same-state attribution covers 234 states across MuJoCo 3.12.0 and Pinocchio 4.1.0. Configuration contributes 75.5--91.0% and contact 9.41--23.5% of the mass-metric acceleration projection, but contact generalized power is negative in every state. Treat these as pointwise synthetic mechanics projections, not energy fractions, human evidence, or strategy guidance. The next scientific gate is matched forward impulse/work through contact transitions with shaft/base coupling, uncertainty, and adverse loading.
- The coordinate-force study evaluates 135 preregistered control programs; 91 meet the declared qualification contract. It reports signed and absolute tangent impulse, power, work, speed, and residual closure without relabeling coordinate terms as anatomical forces or independent causal mechanisms.
- #3882's immutable publication-projection, portable-link, generated-metadata, and deployment contract is enforced by the manifest, verifier, and publication tests. External archival/PID and human-validation gates remain separate.
- **Critical Adverse Results**:
  - Ground screen: 0/384 coupled--fixed cells admitted under registered 5% match (ground damping asymmetry). Post-hoc screen admits 60 cells with mixed signs.
  - Shaft screen: 126/384 coupled--rigid cells match, rejecting universal passive-shaft speed benefit.
  - Initialization sensitivity: natural-zero (32.8 N), gravity-only (565.5 N), conditional (510.3 N) peak ground forces.
- Governed human data (#8556): synchronized bilateral 6-axis grip wrenches remain the external validation gate.

## Launch-Monitor Professional Release Program

- AffineDrift issue #3883 is the publication stream under the cross-repository Tools epic #4583.
- Issue #3893 / `docs/3893-source-backed-sg-traceability` pins the canonical
  source-backed SG contract (`fb4e6e41...`), Tools integration (`a7b6dc437...`),
  and approved visual authority (`10d7f6fc...`) without treating provenance or
  visual approval as independent statistical or baseline validation.
- `articles/Launch_Monitor_Technology_Review/sections/11-validation-program.tex` documents the approved Release A/Release B boundary, ShotLink training quarantine, explicit-identity rule, and UpstreamDrift statistical authority.
- The technology review may publish qualified aggregate findings and method limitations, but it must not expose private source files or describe an internal emulator as a certified vendor model.
- Rebuild the complete PDF and inspect every rendered page whenever this chapter, the program results, or the running-header contract changes.

## Definitional Integrity (Epic #3834 — Verified Closed)

- `NOTATION.md` is normative public semantic authority.
- Drift is the complete autonomous vector field of the declared plant.
- Zero declared control does not mean zero muscle activation or effort.
- DCR compares drift with bounded control capacity.

## Scientific Trust Remediation (#4012 — Protected PR #4046 Merged)

- Protected merge `bb50862bd9993f5101bd9da71ee9a78f124cfb6e` corrects the A1
  control-affinity and attribution defects across Theory Parts 1-2, the
  foundational monograph, and the single-file manifesto.
- A state-dependent gain belongs in $G(x)$ and does not by itself make a system
  non-affine in the declared input; state-only aerodynamics belong in $f(x)$.
- Additivity is not orthogonality. Drift and input vectors may align, oppose, or
  be oblique under a declared metric.
- The shared `_includes/control-affine-attribution-boundary.qmd` is the rendered
  authority boundary: attribution is conditional on model, coordinates,
  declared input, parameters, intervention, horizon, and identifiability.
  Algebra alone does not identify intent, individual-muscle forces, biological
  effort, or a unique real-world cause.
- `tests/test_control_affine_scientific_trust.py` is the corpus contract and must
  remain in the `content_lint` CI lane.

## Gate Commands & Verification

Run locally before pushing:

```bash
python -m pytest tests/test_proximal_distal_*.py -v
python -m pytest tests/ -q
python scripts/check_terminology.py
python scripts/check_image_budget.py
python -m ruff check .
python3 -m pytest tests/test_markerless_mocap_projection_contract.py -q
python3 -m pytest tests/test_mocap_camera_registry_contract.py -q
python3 scripts/verify_mocap_camera_registry.py data/markerless_mocap/camera_evidence_registry_v1.json
```

Monograph verification:

```bash
python -m pytest tests/test_proximal_distal_technical_monograph_contract.py -v
```

Do not infer human technique/physiology; bypass branch protection; add unverified claims; or duplicate computational engines from UpstreamDrift.
