# Shaft Memory Technical Review

Issue #4751 is a child of epic #4009. Scope: the full companion Chapter 15,
its shaft-energy figure, the relevant provider arrays and selected recording
code. This is not a complete re-review of the linked technical monograph or a
rerun of its dynamics. The companion route's 41 earlier findings are preserved
in `shaft-memory-prior-review.json`.

## Scientific Decisions

1. **Power and Storage:** A passive spring does not create energy, but its
   strain energy changes as it exchanges work. Only the complete conservative
   system with no net boundary work conserves mechanical energy. The figure
   now derives input power from a prescribed spring–mass–damper motion and
   separates energy in joules from power in watts. Negative drive power returns
   energy to the actuator; it is not labeled delivery to the clubhead.
2. **Deforming Interfaces:** Full material-point force power already includes
   deformation. Its reference-motion and modal decomposition is an alternative
   representation, not an extra power source. A zero resultant wrench can
   still do deformation work. Intrinsic contact moments need a compatible
   angular decomposition; rigid-interface reduction is conditional.
3. **State and Intervention:** Rigid-to-flexible comparisons need a state map,
   compatible constraints, contact memory, inertias and energy. Resetting modes
   changes the initial condition and may require work and impulse. An SPD
   two-coordinate example increases kinetic energy from 0.725 to 1 J when its
   modal rate is zeroed at the same rigid rate. Opposite modal velocities need
   not produce a distinguishable chosen endpoint. Model ablations alone do not
   identify the mechanism in a golfer.
4. **Stiffness and Validation:** Fixed force and fixed displacement give opposite
   static stiffness–storage trends; forced resonance defeats a universal dynamic
   trend. Isolated beam verification, coupled numerical checks, domain screens
   and held-out physical validation answer different questions. Classical
   Euler–Bernoulli beam rotary-inertia omission does not prohibit a tip body's
   rotary inertia. Bending modes in two planes are not two frequencies in one
   plane.
5. **Counts and Selection:** The 384 trajectory runs and 384 horizon comparison
   cells have different axes. Recomputed matching gives 28, 0, 40 and 58 cells
   at 4, 10, 25 and 50 ms. The two rejected coarse-step probes are additional
   runs. A symmetric relative rule with 1 N and 1 microjoule floors becomes an
   absolute tolerance below the floors. It matches peak station load and grip
   plus shaft damping loss, not every load history or total grip work.
   Post-registration selection is descriptive, not a human causal estimate.
6. **Endpoint:** The provider records `norm(qd[14:17])`, the club-frame origin's
   translational speed. Clubhead-point rotation and deformation velocity are
   missing from that metric. The quoted interval is coupled minus rigid across
   selected fixed horizons, not clubhead speed at impact. At 50 ms alone the
   matched range is -0.0207842342 to +0.0063393134 m/s. Both signs limit a
   universal positive claim about this synthetic observable only.
7. **Distinct Model Screens:** The articulated first-mode atlas passes its
   registered numerical and linear-domain checks. The separate planar forward-
   modal baseline reaches a tip-deflection ratio 0.1347566 above its 0.05
   threshold. Small contact-power residuals cannot repair that failed model-use
   screen. Observed articulated maxima are not the acceptance thresholds.
   Ground reaction and free moment remain absent from the articulated tier.

## Source Boundaries and Reproduction

The articulated JSON, NPZ and recording code were read from UpstreamDrift
commit `a1a613999eb0c744da96caa040941955eb210a21`. The isolated beam and
forward-modal JSONs use the imported monograph revision
`85cce4d3307bb7ad3953d9fc6e583e370803515c`. Chapter links pin these revisions.
The machine-readable receipt `shaft-memory-provider-evidence.json` records
the exact input hashes, array axes, matching rule, counts and horizon ranges.
The NPZ SHA-256 is
`bf49e945b838fc0307f5f50d58fcfad6b9755a0ff389a4e8eb9943bd49dcbf3b`.

To reproduce the summary from that NPZ, select activation indices 3 (coupled)
and 0 (rigid) in `peak_station_force_n` and
`terminal_dissipated_work_j`; apply the declared floored relative rule to both
and intersect their masks. Subtract index 0 from index 3 in
`final_club_translation_speed_m_s`, then summarize only selected entries at
each last-axis horizon. The recomputed mask and every unmasked speed difference
agree with the provider's saved arrays. This is an array verification, not an
independent simulation execution or an empirical uncertainty analysis.

The isolated one-mode/six-mode RMS comparison uses different pulse durations
and force/moment inputs, so it motivates testing excitation sensitivity without
identifying a universal frequency cutoff. The isolated reference chapter was
read fully; forward-modal prose and implementation were consulted selectively.

The [Betzler et al. publisher abstract](https://www.tandfonline.com/doi/abs/10.1080/14763141.2012.681796)
reports 20 golfers and two clubs differing in bending stiffness, with small
average speed and recovery effects. It supports the chapter's bounded human-
evidence paragraph; no full-paper reanalysis or universal fitting conclusion
is claimed. Existing bibliography identity and DOI are retained.

## Delegation and Verification

Five supplied-text agy `gemini-3.8-flash-high` jobs handled source inventory,
provider-code inventory, numerical-test drafting, notation review and a turnover checklist. The lead
read the sources, recomputed provider arrays and adjudicated all edits. Rejected
suggestions included unsupported 50–150 mm empirical deflections, confusing an
observed maximum with a threshold, calling power observer-frame invariant,
reducing the accepted grid by two additional rejected probes, and changing the
chapter hierarchy without accounting for its Lua publication filter.

The draft tests also called a nonexistent NumPy cumulative-trapezoid API; the
accepted test uses an explicit trapezoidal sum. Six synthetic cases cover
interface power, zero-wrench deformation, reset energy/momentum, stiffness and
resonance, the figure's integrated energy ledger, and club-origin versus head
velocity. The new figure test failed before its helper existed; all six then
passed, together with five existing complete-claim-audit checks. Rendering and
final repository validation are recorded separately in the validation receipt.

## Final Validation Checkpoint

The final companion has 218 pages; canonical and public PDFs are byte-identical.
All revised Chapter15 pages and adjacent chapter boundaries were inspected,
including a final reflow that removed an almost-empty references-only page.
The figure and both display equations were also inspected in mobile/desktop
browser views. Four public-site viewport/theme cases pass, with no serious or
critical axe violations, no page overflow and no MathJax errors. Both display
equations fit the 390-pixel viewport. Twelve publication gates pass; the initial
structural warning came from a generated Quarto .tex intermediate, preserved
outside the canonical source tree rather than added to a waiver baseline.

The full run reports 6,385 passed, four failed, 29 skipped and186 deselected in
790.59 seconds. The lead incorrectly overlapped that run with Quarto rendering:
three failures read the canonical PDF while it was absent, different from the
public copy or partially written; one caught its changed audit digest. After
rendering finished, exact source/public parity was verified, evidence digests
were refreshed, and all63 checks in the six affected modules passed on stable
files. The original full run remains failed; this is not a claim of a green
full rerun. Coverage is78.4% for src plus scripts and93.0% for src alone.
Repository Ruff and Black834 checks pass; optional notebook-formatting
dependencies are absent. Packaging-test outputs were preserved under QA.
Future full regressions must run after rendering and digest refresh finish.
