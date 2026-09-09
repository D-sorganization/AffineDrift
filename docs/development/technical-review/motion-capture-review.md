# Motion Capture Technical Review

## Scope and Delivery State

Issue #4324 is a native child of epic #4009; corpus #4021 remains unfinished.
Branch: fix/4324-motion-capture-rigor, worktree
C:/Users/diete/Repositories/AffineDrift-technical-review. Initial parent is
2e0fe28ffac9f94c514ec052f434812a467a178a. Rotation PR #4323 merged as
625b0fc4ff1135eaef3bf81b0852089f4129c1f1; its production checks are running.
PR: https://github.com/D-sorganization/AffineDrift/pull/4325 (open). The original 333-line, indexed 6,174-word
articles/technology-motion-capture.qmd was read completely before correction.
The camera-selection companion is outside this complete-review scope.

Claim was free; lease comment 5609338858 expires 2026-09-10T00:01:08Z.
Central presence comment 5609387649 expires 00:05:45Z. Inbox has no messages
or conflicts but reports an unrelated rejected-identity warning; this is not
evidence that the repository is vacant. ADR 0001 preserves AffineDrift's
educational/publication role, Tools contracts and UpstreamDrift capture runtime.
The original checkout and immutable proximal_distal_energy_transfer publication
remain untouched. No subagents are used.

## Confirmed Problems

- Triangulation is conditionally observable; a calibration residual does not
  establish independent dynamic accuracy. Instrumentation is not solved.
- A ranked table mixes millimetres and degrees, tasks, cohorts and definitions.
  Convention differences are not automatically errors in a common estimand.
- Soft tissue artefact can contain systematic and variable components; filtering
  and constraints have conditional benefits. Bone pins are another direct
  tracking method. Thickness alone does not determine the largest error.
- Euler composition differs from averaging within a declared chart. Screw
  descriptions retain frame, origin, interval, anatomy and scalar choices;
  pitch invariance under rigid coordinate changes is not temporal conservation.
- Axis conditioning depends on rotation magnitude, cluster geometry and noise.
  A golf transition need not have zero three-dimensional angular velocity.
- Axial-roll ambiguity of two endpoints does not apply to every vision model;
  priors, additional landmarks and body models require separate validation.
  Between-system comparisons do not isolate camera count or label bias.
- Unaided IMUs measure specific force and angular velocity, not orientation
  directly. Correlation is not agreement or validation of another product.
- Frame displacement is distinct from exposure blur, rolling shutter,
  synchronization and aliasing. A failed literature search is not evidence
  against submillisecond contact duration or high distal angular speed.
- Relative-angle errors depend on covariance; common orientation error can
  cancel. Kinematic peaks do not identify energy flow or neural control.
- Vendor statements need dated attribution, quantities and operating bounds.
  Radiography has registration/calibration limits; no method is universally right.

## Success Criteria

Verify retained empirical claims against primary sources; preserve historical
heading destinations; replace false categorical claims with a connected
measurement-to-mechanics treatment. Independently verify manufactured timing,
geometry, uncertainty and axis-conditioning examples. Render and inspect the
whole article, equations, mobile/desktop and both themes. Run required content,
static, style, type, link and configured regression gates before protected PR
delivery. Record failed attempts as well as successful checks. No complete
corpus or publication claim is made at this checkpoint.

## Source Reading Boundaries

The four content-development/technology-research dossiers are discovery notes,
not validation evidence. Their verification flags contain assertions that the
article itself contradicts, including impact duration and K-Vest sensor count.
MDPI direct page opens returned HTTP429; PMC HTML opens returned browser
challenges. Neither is counted as a full-paper read. Europe PMC's public
fullTextXML API provided the three full texts below. An initial local XML
parser failed because lxml was unavailable; standard ElementTree extraction
then succeeded. Downloading full text does not mean every part was read.

| Source | Material Actually Read | Boundary of the Published Claim |
|---|---|---|
| Fiorentino2017, DOI10.1016/j.gaitpost.2017.03.033 | Publisher abstract, including methods/results | Eleven adults, hip tasks, STA3–54mm and hip differences; not golf-wide tolerances |
| Karduna2000, PMID10854878 | Indexed abstract/result | Up to50degrees for some scapular coordinates under sequence changes; not camera error |
| Bourgain2022, DOI10.3390/sports10060091 | Relevant methods/reporting and full X-factor-definition paragraphs in full-text XML | 92-study review; torso/pelvis versus shoulder/pelvis constructs across studies; not a controlled same-swing doubling |
| KimSE2023, DOI10.3390/s23208433 | Sections2.1–2.5.3, result explanations and Tables2/3 relevant to claims | Two custom100Hz IMUs atT1/L4,36golfers; ICC/LoA scope, not K-MOTION validation |
| KimW2025, DOI10.3390/jfmk10030315 | Participant table, acquisition description, computation section2.4, relevant results/discussion | Two-person exploratory study; inconsistent skill labels; inertia principal directions are not observed ISA |
| Uhlrich2023, DOI10.1371/journal.pcbi.1011462 | Abstract and complete relevant validation methods/results (publisher lines389–425) | Ten adults, four activity families,18rotationalDOFs,4.5degree aggregateMAE; no golf-shoulder guarantee |
| Marsan2019, PMID31741482 | Complete abstract, not full six-page paper | Thirteen golfers,seven definitions,strong sequence dependence; no reference method |
| Keller2023 SKEL, DOI10.1145/3618381 | Primary PDF first page and introduction into second-page related work | Surface/skeleton mapping and biomechanical model purpose; no numerical accuracy or golf validation claim |
| OpenCV4.13.0 calib3d | Pinhole/projection/distortion and frame equations, official page lines15–155 | World-to-camera convention; independent stereo sensitivity derivation added here |
| JCGM100 Section5; VIM2.47 | Official ISO HTML linearization/correlation prose and BIPM definition | Local covariance propagation and correlated differences; equation image fetch failed, matrix identity independently derived/tested |
| Gallego et al., arXiv1904.08405v3 | Complete abstract | Asynchronous brightness-change sensing and reduced conventional blur; not anatomical golf validation |
| GEARS golf page | Relevant product/specification text | Eight1.7MP cameras,360fps,0.2mm vendor wording; not independently validated anatomical accuracy |
| K-MOTION FAQ | Complete relevant four-sensor answer | Four-sensor configuration only; no extrapolated product validation |
| Sportsbox accuracy report | Complete methods, quantitative and summary prose | Thirty single-swing records,selected event metrics,AMM3D reference; reported averages not maximum errors |

The SKEL page timed out and the web PDF reader rejected its24MB length. A
normal primary-source PDF download and pypdf extraction succeeded; the paper's
figures were not visually audited and no figure-derived claim is retained.
Removed numerical claims include unverified scapular/hip-centre/moment ranges,
cross-system camera-count effects, forearm impossibility, a universal markerless
noise floor and the unsupported historical explanation of Woltring's reception.
This is withdrawal of inadequately bounded assertions, not evidence that the
underlying studies or methods are invalid. No claim of an exhaustive absence
of published golf validation survives.

## Implemented Treatment

The article now follows observations, reconstruction, anatomy, kinematic
definitions and mechanical inference. It preserves the original substantive
topics while replacing a false hierarchy with an outcome-specific uncertainty
budget. Stereo depth, moment-arm sensitivity, exposure and sampling, aliasing,
derivative noise, common-frame cancellation, correlated angle differences,
axis reconstruction/conditioning and nonunique peak order have independent
manufactured checks. Constant pitch is separated from temporal conservation,
energy, efficiency and causality. Grip power, stationary contact, retained
state and additional measurements connect the argument to the golf research
program. ADR0001 boundaries remain unchanged; no capture runtime was added.

## Validation and Publication Inspection

- RED: three withdrawn-claim regressions fail on the original article;
  sixteen independent manufactured numerical cases pass.
- GREEN: all19focused checks pass after the rewrite. Black100 and Ruff pass.
- Configured root: `py -3.12 -X utf8 -m pytest --cov --cov-report=xml
  --timeout=60` passes5,097, skips29, deselects131 in389.79seconds.
- Content lane:130pass,4skip. Full Ruff passes; Black687files passes;
  configured strict mypy91sources passes; full tracked Python quality plus
  the new test file passes; canonical link site gate passes.
- Initial title/static pass found one title-case mismatch in a callout heading.
  The heading was reworded; all34static contracts then pass. No formula or
  implementation changed. Final title audit passes all636source files.
- First browser harness had one syntax typo, then a stale accessible-name
  assumption for the layman button. Both are harness defects; the current
  snapshot named the original button `Expand In Layman's Terms`.
- Seventeen overlapping desktop body images have all been visually read.
  All12equation details and36table captures (three horizontal positions,
  two tables,320/390/1440pixels,both themes) have also been visually inspected.
- Final rendering passes. All70math expressions typeset, including6displays;
  no MathJax errors, raw display delimiters, duplicate IDs or broken internal
  fragments are found. All26original rendered heading destinations survive.
- Four mobile table keyboard cases focus and scroll successfully. The14-case
  width/theme grid has no page overflow. Final title/callout changes were then
  checked at320/390/1440pixels in both themes, again without page overflow.
- Visual review found that the original custom explanation changed ARIA state
  but remained clipped by the shared CSS sibling selector. A native Quarto
  collapsible callout now displays the entire explanation. Both themes verify
  visible expanded content (1210.56pixels high at390pixels) and successful
  collapse. The shorter title wraps without splitting long words on mobile.
  No shared CSS or JavaScript changed.
- Axe checks at390/1440pixels in both themes have zero serious/critical
  findings; the final markup was checked again at1440pixels. Existing minor
  mobile aria-allowed-role and moderate duplicate table-landmark names remain.
  Browser console reports include errors/warnings; this is not a zero-console
  certification. One supplemental harness attempt failed on an offscreen
  theme button; scrolling to the header before clicking resolved it.
- After the final title/callout markup changes, the19focused checks and content
  lane130pass/4skip pass again. Root coverage is79.19%; the full5,097-test run
  preceded these presentation-only changes. No new runtime implementation,
  JavaScript or PDF was introduced.

## Remaining Delivery Work

Portable development-log validation reports only preexisting peer entries:
DL-#3903 lacks a usable SHA and DL-#3902 lacks PR/Last verified fields. These
entries are preserved. The final render regenerated unrelated trust summaries
with dates, platform-dependent hashes and formatting; these build side effects
were inspected and restored, without changing their canonical source data.

Commit the canonical correction and evidence with normal hooks, then replay
only this issue's commits after2e0fe28f onto the resulting main state before
first push. Its remote branch gained
ba7e7b1d (a formatting-only CSS commit) from another actor; preserve it through
the parent merge. PR creation,protected checks and exact publication remain.

## Protected Delivery Checkpoint

Implementation6c004373 was replayed alone after2e0fe28f onto rotation squash
625b0fc4, producing b1a4a030a03044158aea1af747782d53d913c02a before first push.
The parent-tree difference was inspected: only rotation-converter.css formatting
changed, and that peer change is preserved. The first rebase attempt stopped
on an empty-diff handoff index mismatch; an index refresh resolved it without
altering content. No force push or hook bypass was used. All normal commit and
push hooks pass. Full PR4325 is open with Fixes#4324 and agent/scientific labels.
The SPEC row is keyed once to4325. Protected checks and exact publication remain.
