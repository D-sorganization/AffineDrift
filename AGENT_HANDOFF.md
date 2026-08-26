# Agent Handoff — AffineDrift

Last updated: 2026-08-26

This is current operational state. Historical detail belongs in git/GitHub.

## Merge Governance

- Use pull requests and ordinary protected merges; required status checks must pass.
- Do not require or request a named maintainer's approval when the live ruleset requires zero approving reviews. Review remains optional for risk, expertise, or unresolved feedback, but `@dieterolson` is not a standing release gate.
- Never use admin bypass, force-push, or protection changes to merge a failing or stale head.

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

- **Published Technical Monograph**: [`articles/proximal_distal_energy_transfer/index.qmd`](articles/proximal_distal_energy_transfer/index.qmd)
  - 35 comprehensive technical chapters (`chapters/_ch01_...` to `_ch09_...`) covering multibody mechanics, coordinate-explicit Coriolis, squared-speed/centripetal, gravity, applied, and residual force sources, endpoint virtual-work mappings, multi-station Coulomb friction, and bounded optimization studies.
  - Published technical PDF: [`proximal_distal_energy_transfer.pdf`](articles/proximal_distal_energy_transfer/proximal_distal_energy_transfer.pdf) (244 pages, >= 69,000 words).
  - Executable companion and monograph PDF contracts use the exact governed
    `pypdf==6.16.1` root dependency pin.
  - [`source_manifest.json`](articles/proximal_distal_energy_transfer/source_manifest.json) pins the exact UpstreamDrift #9062 protected squash `9c44fc068ec44788a1b957bbbfee109f59b02dbf`, the release-manifest and claim-registry digests, the embedded generation environment, and both PDF digests. Digest equality establishes provenance, not independent scientific confirmation.
  - `python scripts/verify_proximal_distal_projection.py` independently downloads or reads that authority, verifies 208 byte-identical source files, 21 uniquely mapped flattened figures, 12 normalized immutable-link rewrites, 13 explicitly hashed publication adaptations, the claim registry, and the PDF. CI also pins the complete 254-file local projection tree. Unreferenced SVG derivatives absent from the source manifest are excluded rather than promoted.
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
- **Camera evidence registry (AffineDrift #3956 / AFF-M1):** branch
  `feat/3956-camera-selection-registry` starts from protected main
  `ca33d3ef6f543ff3dfcadda35c3bdf2356acff84`. The versioned registry, strict
  verifier, public camera-selection guide, and contract tests cover FLIR
  BFS-U3-16S2C-CS, Basler a2A1920-160ucBAS, and ZED X One GS through ten required
  purchasing attributes each. The decision is provisional: quote and buy two
  matched cameras for a physical pilot, not the full rig. No complete-system
  cost, legal approval, runtime adapter, timing/bandwidth result, calibration,
  pose result, C3D result, or procurement approval exists. AFF-M2 must consume
  protected Tools calibration contracts after their dependency stack merges;
  do not copy runtime calculations into AffineDrift.
- **Camera price evidence maintenance (AffineDrift #3977):** branch
  `fix/3977-camera-price-evidence` starts from protected main
  `3feec152d9d6354ac60511d432876b0788cecda0`. It separates typed, volatile
  camera-body observations from complete qualified-topology cost. FLIR and ZED
  amounts remain configuration/region-specific vendor observations; the Basler
  amount remains unavailable because its official US page did not expose a
  reproducible amount. All complete-system costs and procurement authority
  remain unavailable/default-deny. RED was proven at exact tests-only SHA
  `6ddc633de575dbd98fee59a144a33a4c3fa6fd5a` on approved OGLaptop runner 3 in
  Repository_Management run `33008490854` / job `98308354626`, using wrapper
  `c8fbcf6fe90a3c50d6f7813820bf7f1b717a4cd3` and explicit `-n 0`.
  The first GREEN passed 20 focused contracts at exact implementation SHA
  `844a41a0a66c243af5f931c423a11e0ba7a78959` in run `33009325059` / job
  `98311192279` on approved OGLaptop runner 3 with the same fixed serial command.
  Adversarial review then added mutation coverage at tests-only SHA
  `1f2227d83e0ab5d338e41c502fafc13857f549ed`: run `33009685827` / job
  `98312433390` failed exactly three contracts on approved OGLaptop runner 2
  (v1 region/currency enums, manufacturer commercial-source enforcement, and
  non-finite amounts). Hardened implementation SHA
  `86aee145b7a6f7d5035033060c331abf18ea0a07` passed all 22 focused contracts
  in run `33009974032` / job `98313408001` on approved OGLaptop runner 1. The
  v1 price vocabulary is intentionally `US|GLOBAL` and `USD|null`; numeric
  camera-body amounts require finite positive values and a referenced
  `vendor_product_page`. This is a narrow validated vocabulary, not a claim of
  general ISO-3166 or ISO-4217 validation.
  This branch intentionally does not absorb #3976's ZED synchronization change:
  merge/rebase #3976 first, retain its 15-microsecond topology statements, and
  advance this branch's spec version from 1.0.226 to 1.0.227 during resolution.
  #3978 separately owns USB-pilot versus distributed-Ethernet topology roles;
  do not infer those roles from camera-body prices or broaden this diff into
  topology selection. Governed render/search derivatives remain paused by the
  DeskComputer capacity-drain directive, and no PR should open while full-PR
  rules would trigger prohibited broad jobs.
- **Camera topology evidence maintenance (AffineDrift #3978):** branch
  `fix/3978-camera-topology-boundary` is intentionally stacked on #3977 exact
  head `96142ebfe91a4e9fc69001376564747243f85904`; it is not a merge authority for
  #3976 or #3977. The registry now separates the FLIR two-camera USB pilot,
  Allied Vision Alvium G5-203 eight-camera distributed reference hypothesis,
  and LUCID Triton2 TRT016S-CC Ethernet/PTP challenger. Each role must dispose
  twelve topology dimensions and remains explicitly unqualified, without
  runtime or procurement authority. The first test-only RED
  `34c00a801ef2ec166e2271025e5ded4d5a275c54` proved the public-article boundary
  on approved OGLaptop runner 2 in Repository_Management run `33010905903` /
  job `98316610479`; test naming
  initially selected only one of the two intended contracts. The corrected
  test-only RED `cad014f6b4fa68f61bd76ff65d2ca907b505cd1b` failed exactly the registry
  and article topology contracts in run `33011056389` / job `98317130366` on
  approved OGLaptop runner 3. Both runs used wrapper
  `cc1fee104fd4c513b393bc4701ff803e14101b01` and explicit
  `python -m pytest -q -n 0 tests/test_mocap_camera_registry_contract.py -k topology`.
  GREEN implementation `e02d042fac818beb064d3e62936201a578955a0a`
  (tree `a0556ce065f69d5c640a1def3d7ac37e50c500f1`) passed all 10 selected
  topology contracts in run `33011853493` / job `98319879099` on approved
  OGLaptop runner 2 with the same exact-SHA, serial wrapper.
  The expanded whole-module contract then caught a real FLIR arithmetic-screen
  defect at hardening SHA `ffbc5831e14abea49eac88ed3c2ea0d95e47e62f`:
  run `33012057652` / job `98320585616` on approved OGLaptop runner 2 failed
  because 5.6245248 Gbit/s did not equal the deterministic 5.6236032 Gbit/s
  result. That run is retained as product RED evidence; checkout and setup
  passed. Corrected SHA `d8b6a1cc0d671fe1c8abd912a13975f1a07d9637`
  then exposed the same defect class in the Allied eight-camera screen:
  run `33012234104` / job `98321213736` on approved OGLaptop runner 4 failed
  because 29.3308416 Gbit/s did not equal 29.3289984 Gbit/s. The hardened
  contract now uses exact decimal arithmetic for every topology record and
  requires the article's formatted figures to match the registry.
  FLIR cable distance and exact OS matrix, Allied validated cable/network
  design, LUCID Arena redistribution terms, and every complete quote remain
  unavailable. All raw bandwidth/storage values are arithmetic screens, not
  measured throughput or storage procurement budgets. Rebase after #3976 and
  #3977 protected integration, reconcile SPEC version order, retain the
  corrected 15-microsecond ZED statement, and rerun bounded serial validation.
  Governed render/search derivatives and a full PR remain paused by the
  DeskComputer capacity-drain directive.
- The source release is pinned to UpstreamDrift #9062 protected squash `9c44fc068ec44788a1b957bbbfee109f59b02dbf`.
- Source release: 608 artifacts, 306 atomic claims, 2,254 evidence references, 328 local artifacts, and 78 external URLs; no source-manifest mismatch remains.
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
