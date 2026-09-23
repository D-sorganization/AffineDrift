# Manifesto Notation and Capability Review — #4428

## Scope and Argument

Reread the complete series index, the relevant state/force declarations in
Theory Parts 1–4, all of Part 5 and its shared numerical procedure, and the
single-file edition's canonical-version notice. The index must help readers
choose an argument with the right mathematical and evidential scope.

The original index called G(x)u an actuated generalized force even though it
appears in a full-state differential equation. The replacement traces the
map from generalized load to acceleration to state rate. It includes retained
flexible coordinates, distinguishes stacked from interleaved state ordering,
and states the invertibility, smooth-mode and input-affinity assumptions.

For independent coordinates z with v=zdot, M vdot+h=B u gives
vdot=-M^-1 h+M^-1 B u. Stacking x=(z,v) gives f=(v,-M^-1 h) and
Gu=(0,M^-1 B u). Each equation follows by substitution. B u has generalized
load units; its inverse-inertia image has acceleration units. Position-rate
and velocity-rate blocks need not share units, so a full-state norm needs
declared scaling. DCR requires its projection, norm, input set and denominator
convention and still does not determine correction direction or reachability.

## Corrected Findings

- **P1 — Input Units and State Completeness:** Replace generalized-force wording
  for Gu and the rigid-only state shorthand. Include retained flexible modes,
  state-order consistency, internal-state requirements and constraint/event
  boundaries. Zero declared input retains the specified plant loads; earlier
  inputs can change the state and hence the later drift.
- **P1 — Verification Capability:** Part 5 describes reproducibility checks and
  explicitly withholds a revision-bound run package for historical Simulink
  outcomes. Its index card now describes that protocol, without presenting it
  as an available verified implementation or empirical golf validation.
- **P2 — Series Orientation:** Match Part 4's present beam/pendulum scope and
  title-case the changed card headings. Keep the single-file edition's explicit
  precedence rule and the model-conditioned ZTCF interpretation.

## Adversarial Review and Limits

The compact displayed model does not represent a system with omitted memory,
redundant coordinates or changing contacts. Generalized velocities need not
equal coordinate derivatives outside the declared local convention. A
coordinate permutation cannot justify omitting flexible or physiological
states. Zero input does not remove gravity, retained external loads or the
state consequences of earlier action. A numerical consistency protocol does
not establish a completed run, human prediction or coaching rule.

The two previously corrected manifesto findings were reread: the intervention
card still rejects unique muscular/intent inference, and the page still calls
itself an editorial series rather than a comprehensive validated theory.
This is a complete index-page reread, not a new full review of every linked
article. No new external paper access, numerical solver run or human experiment
is claimed. Historical provenance discrepancies on other site surfaces remain
tracked separately in #4429.

## Presentation and Evidence

The associated rendering record captures local desktop/mobile and light/dark
cases, all eleven mathematical expressions, the two displays and the revised
capability card. A page-local rule preserves relative reading-size math and
stacks the state blocks for narrow screens. Frozen zero-torque sources and
reports from #4427 remain unchanged. Source/render acceptance is bound only
after its checkpoint is committed; CI, main merge and live publication are
separate gates.
