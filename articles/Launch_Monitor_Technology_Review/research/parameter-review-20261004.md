# Parameter Chapter: Evidence and Unfinished Acceptance

Issue: #4881, under epic #4009 and corpus #4021. Date: 2026-10-04.
Baseline: `205f089130a03fdee77c6a73074cf6ce7d598c7a`, original chapter 1,585 words.
The entire original chapter was read. The current replacement is **provisional**.
The user requested a committed handoff before final acceptance; do not report this chapter as complete.

## Decisions Already Made

- Keep all existing chapter, section, table and equation labels. Use the existing right-handed world basis: x forward, y upward, z right. The launch spin basis is already defined in chapter 3, equation `eq:axistilt`.
- Separate output reference event from observation interval. Do not silently reconcile the older vendor maximum-compression account with its newer pre-contact speed definition.
- Delete uncited tour means, a universal seven-mph toe/heel difference, and the claim that one definition explains most brand disagreement.
- Declare face-center versus local-contact normals without calling one intrinsically erroneous. Face-to-path is a declared heading difference, not complete relative contact kinematics.
- Treat the published three-degree driver offset as one vendor illustration. The rigid-body conversion requires vector angular velocity, reference-point displacement and translational velocity, not just angular-speed magnitude.
- Separate launch state, speed ratios, observed trajectory descriptors and predicted bounce/roll. Smash factor is not an energy-transfer fraction.
- Use transverse spin magnitude in the two-component sine/cosine equations. Retain axial spin and undefined-axis cases explicitly; do not invent a universal conversion between vendor output conventions.
- Replace the universal modality capability matrix with a provenance/assumptions table. A manufacturer statement is evidence for its definition or claimed method, not independent validation of accuracy.
- Retain the historical `perfectgolfswing` bibliography key with an explicit `nocite` explanation. It no longer supports the removed fixed lateral-curvature rule. All existing keys stay stable.

## Primary Sources Read

These are bounded reading records, not claims that all linked material or products were independently assessed.

| Key                            | Primary Source and Reading Scope                                                                                                                                                    | Use and Limit                                                                                                                                        |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `trackmanclubdata`             | [Club Data Definitions](https://www.trackman.com/blog/club-data-definitions), 2017 technical body                                                                                   | Pre-impact fitting with compression reference; local contact normal; illustrative point offset. Historical vendor account, not all-product taxonomy. |
| `trackmanclubspeed`            | [What Is Club Speed?](https://www.trackman.com/blog/what-is-club-speed), 2024 definition                                                                                            | GC speed before first contact; does not prove general brand-error causation.                                                                         |
| `trackmanspinloft`             | [Spin Loft](https://www.trackman.com/blog/spin-loft), definition and three-dimensional qualification                                                                                | Angle between the declared directions. No universal monotonic spin-rate conclusion accepted.                                                         |
| `trackmanparameterdefinitions` | [Parameter Definitions](https://support.trackmangolf.com/hc/en-us/articles/5089892383515-Practice-Trackman-Data-Parameter-Definitions), updated 2025-11-27; full-swing entries read | Definitions and event distinctions; putting entries not used.                                                                                        |
| `foresightclubdefinitions`     | [Club Head Data](https://help.foresightsports.com/hc/en-us/articles/47214673873811-Club-Head-Data-Measurements-Definitions), updated 2025-12-08; metrics read                       | Shaft-axis closure rate and face-roll lie differ from general angular speed and shaft inclination. No exclusive product capability inferred.         |
| `trackmanlowpoint`             | [Low Point](https://www.trackman.com/blog/low-point), 2024-05-30; technical definition read                                                                                         | Arc-minimum reference. The ground-contact counterexample is our geometric reasoning, not a vendor measurement.                                       |
| `trackmancarry`                | [Carry](https://support.trackmangolf.com/hc/en-us/articles/39726543090971-Parameters-Carry-Tee-to-Green), updated 2025-08-07; full short article read                               | Launch-elevation convention. Actual terrain contact can differ.                                                                                      |
| `trackmaniospin`               | [Radar and Cameras](https://www.trackman.com/blog/radar-and-cameras-for-superior-indoor-golf-accuracy), Fredrik Tuxen, 2026-09-10; article body and FAQ read                        | Vendor describes iO camera-based spin including gyro spin. Its accuracy and superiority marketing was not accepted as independent evidence.          |

Additional context: TrackMan's spin-axis page was read but its universal unchanged-axis language was not adopted. Its older indoor inference description cannot be generalized to later iO hardware. The 40-parameter page was consulted in part; the newer support definitions provide the precise table source. Direct guessed swing-plane/direction/carry blog URLs failed; use the verified support sources instead. No community discussion was used as primary evidence.

## Mathematical Reasoning to Preserve

For rigid points, `vP = vO + omega cross r` at one instant in one frame. With `vO=(40,0,0) m/s`, `r=(0.04,0,0) m`, and `omega=(0,50,0) rad/s`, the correction is `(0,0,-2) m/s` and heading is -2.862405 degrees. Reversing omega reverses the offset; omega parallel to r gives zero correction at the same angular-speed norm. These are manufactured counterexamples, not typical measurements.

Dotting unit directions `(cos(a)cos(p),sin(a),cos(a)sin(p))` and `(cos(l)cos(f),sin(l),cos(l)sin(f))` gives the spin-loft cosine formula in the chapter. For a=-5, l=15, f-p=10 degrees the angle is **22.32050216019335 degrees**, independently computed. A lead draft's 22.31 rounding was corrected to22.32. At equal headings the angle is the absolute elevation difference in the stated interval. Vertical azimuth singularities do not invalidate the vector dot product.

For horizontal forward flight, spin `(1000,-300,3000) rpm` has transverse magnitude3014.962686, total3176.476035 and tilt5.710593 degrees. The axial component accounts for the difference between total and transverse magnitudes. The source spells out rpm versus rad/s conversion. Use chapter3's velocity/world-up frame; it is **not** a Frenet-Serret construction.

Independent values and assertions are saved in `docs/development/technical-review/parameter-checkpoint/independent-checks.json`. Recompute with NumPy cross/dot and Python math; do not treat helper arithmetic as an oracle.

## Delegation and Rejected Suggestions

Four agy CLI helpers used `gemini-3.8-flash-low` with `--print --print-timeout 180s`: original claim inventory, algebra review, numerical verification, and turnover checklist. All exited0. Their transcripts are committed under the checkpoint directory. They had no editing or issue authority.

Rejected or narrowed: universal upward-is-shallower wording; invented impact timing ranges; proprietary radar face inference asserted without evidence; calling the hybrid vendor definition physically invalid; treating global vertical as perpendicular to an arbitrary launch; replacing the launch frame with Frenet-Serret; inaccurate intermediate trigonometric products.

The turnover helper invented paths, commands and Quarto/MathJax steps. **Its checklist is not executable authority.** Specifically, reject `data/trust/*.json`, `references/`, `@sec-` labels, the invented evidence-regeneration module, and direct `gh pr merge --auto` advice. This book is standalone LaTeX; follow the lead's handoff packet and actual repository scripts. Issue assignment alone is not the fleet lease protocol.

## Checkpoint Validation and Limits

- Four-step pdflatex/biber build succeeded in an isolated QA output directory:94pages,101 bibliography entries and101 printed entries, no undefined citations/references.
- The log's overfull warnings occur in the existing patent chapter and bibliography; none was observed in the chapter2 log section. That is a log check, not visual acceptance.
  -63 focused tests passed;665 publishable-source title checks passed. No full parameter-branch regression, final independent technical review, PDF visual inspection or browser acceptance has been completed.
- The canonical `articles/Launch_Monitor_Technology_Review/main.pdf` remains the previously accepted92-page hardware PDF. The provisional94-page PDF is committed separately under checkpoint/render for handoff. **Source and canonical PDF intentionally do not yet match; finish acceptance before opening a publication PR.**
- No changed source/evidence hash is an acceptance certificate. `checkpoint-validation.json` binds the provisional files and records the limits.

## Resumed Final Review: 2026-10-04

The user resumed the goal after the saved pause. Parent PR4879 merged at b33bcf1a37c1cf8665fb6cc3a0f8abd84a1db496; all11hardware/Bosch canonical source/evidence hashes match their accepted records. The independent receipt is reports/technical-review/hardware-bosch-remote-main-receipt.json.

Two additional agy Gemini3.8Flash helper tasks covered claim tracing and notation. The first notation invocation failed before execution because the combined prompt could not launch through the Windows CLI; the narrowed retry completed. The claim-trace helper proposed reversing the backspin axis, which is incorrect: with x forward and y up, eb=x cross y=+z, and positive-z rotation gives backward surface velocity at the ball top. Its alleged component-axis swap is likewise false. Its absolute-value interval suggestion merely restated the existing correct condition. The notation helper confirmed the rigid-point and dot-product identities but again supplied inaccurate rounded intermediate trigonometric products; the executable NumPy/math values remain authoritative.

Lead accepted two narrow qualifications: hold horizontal speed fixed and nonzero in the attack-angle statement, and restrict the displayed contact-point expression to ideal rigid kinematics immediately before contact, with deformational surface velocities needed during compliant impact. Initial PDF inspection found a one-line split of the keypoint callout; Needspace now keeps the box together. Source, bibliography and render acceptance are recorded separately from the historical provisional checkpoint. These changes do not add empirical device validation or claim whole-book technical clearance.

Final fleet pre-PR repair is recorded in reports/technical-review/parameter-review.md: explicit metadata title, title capitalization, one shortened outline heading and historical-preview preservation. No additional scientific claims were introduced.
