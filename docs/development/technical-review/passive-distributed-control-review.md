# Passive Impedance, Distributed Feedback and Stability Review

## Scope and State

Issue #4336, native child of #4009; corpus #4021 and Physics #4054.
Parent shaft delivery cbd611369542cb3c63a1b4bf171936e8b665867c; branch
fix/4336-passive-impedance-rigor. Both complete original editions and all
12 exercises were read, including web-only coaching sections. No canonical
chapter corrections or numerical/rendered validation have been completed yet.
Preserve peer ch29/impact operators and immutable publication. No subagents.

## Confirmed Findings

- An additive impedance vector field includes q-dot in its top block, double-counting the kinematic equation. The active input channel, held activation and full-state counterfactual are conflated. ZTCF is incorrectly defined as a fraction of motion; 40–50% and 70–80% attribution claims have no defined metric or cited reproducible study.
- A moving-reference Lyapunov derivative omits reference-velocity and parameter-power terms, uses absolute instead of error kinetic energy for tracking, and treats negative-semidefinite damping as strictly negative everywhere. Unknown forces are assumed dominated without bounds. The critical-damping example K=100,D=20,m=1 is incorrectly called a spiral.
- The 20,000 decisions/s versus 40 parameters comparison confuses sample counts, parameter counts and information rates. Behavioral bandwidth is treated as a universal neural-processing ceiling. Fixed pre-tuning is asserted while time-varying feedforward, reference and impedance are also prescribed.
- Impedance is conflated with stiffness, passive tissue, active co-contraction and delayed neural feedback. Gamma drive and reflex circuits are oversimplified; maintained activation is claimed to need no ongoing effort. Hogan's framework is overstated as an exclusive cortical mechanism.
- A universal proximal/distal impedance schedule and kinetic-chain energy direction are asserted without measured perturbation evidence. Co-contraction is assumed to monotonically set both stiffness and damping. Grip pressure and subjective feel are treated as identified impedance.
- Force is expressed in kilograms. High distal stiffness is said to block impact transmission, dissipate energy and prevent injury without a mechanical or clinical basis. Impact duration and inertia cannot identify a safe stiffness range. Exercises recommend unexpected physical perturbations during a live swing; replace with simulation or an appropriate controlled non-striking identification example.
- The editions differ substantially; web-only coaching claims reinforce unsupported posture, waggle and training prescriptions. All 12 exercises require corrected premises and worked answers.

Acceptance: paired rigorous treatment distinguishing mechanical passivity, active intrinsic mechanics and distributed feedback; exact drift augmentation and declared counterfactual; proper equilibrium and tracking proofs with external/parameter power; independent damping and delay examples; bounded primary evidence; safe, identifiable applied exercises; complete rendered print/web and repository validation. Explain how impedance, activation, feedback, energy and impact objectives interact without presenting a modeled mechanism as a measured universal golf prescription.


## Derivation Plan

For x=(q,v), additive impedance contributes [0; M^-1 tau_imp]; the upper
kinematic block is zero. Define the held controller and input channel before
calling a term drift. Held coactivation is an active operating condition,
not zero excitation or absence of physiological energy consumption.

For stationary reference and physical conservative forces, use total storage
V=0.5*v^T*M(q)*v+U_g(q)+0.5*(q-q0)^T*K*(q-q0), measured relative to a strict
local energy minimum. With Mdot-2C skew and symmetric positive damping,
Vdot=v^T*tau_external-v^T*D*v. Zero velocity can make Vdot zero away from
equilibrium; use invariant-set reasoning with an isolated minimum, bounded
sublevel set and specified damping. Negative stiffness or unbounded disturbance
cannot be fixed by merely asserting large damping.

For a moving reference, retain reference power and parameter power. With
fixed-reference damping, the extra storage terms are
-e^T*K*q0dot + 0.5*e^T*Kdot*e. A moving damper reference adds its own power.
A separate exact constant-inertia tracking example with feedforward M*qdd_d
has error dynamics M*edd+D*ed+K*e=d_ext and error storage derivative
-ed^T*D*ed+ed^T*d_ext. This tracking certificate does not say the actual
moving mechanism is unpowered or validate a biological controller.

For I=1,K=100, D=5/20/50, classify poles and show underdamped spiral,
critical repeated real pole, overdamped real nodes. More damping can make
the slow recovery slower. Non-increasing mechanical energy does not mean
every coordinate or task error decreases monotonically. Measure finite-time
perturbation amplification and task output, not only asymptotic convergence.

For a sinusoidal imposed perturbation e=A*cos(omega*t), delayed restoring
feedback -kr*e(t-delay) has mean mechanical power
0.5*kr*A^2*omega*sin(omega*delay). Positive gain and an apparently restoring
sign do not ensure passivity. Compare with immediate damping's negative
mean power; label this a manufactured frequency-domain calculation, not an
estimated human reflex or a full delay-system stability proof.

Separate linear mechanical impedance Z(s)=I*s+D+K/s (torque/angular velocity)
from dynamic stiffness I*s^2+D*s+K (torque/angle). Declare operating point,
input/output, frequency band, delay and perturbation magnitude. Joint-to-hand
mapping also depends on posture, Jacobian and load, so grip pressure or EMG
alone cannot identify the complete operator.

## Primary Evidence and Access Boundaries

- Burdet et al. (2001), DOI 10.1038/35106566: complete article prose and methods
  read in the primary paper PDF. Nine participants; learning analysis used five
  naive participants. Horizontal shoulder/elbow reaching with trunk harness
  and wrist splint; robot-created divergent field. Stiffness was measured
  over 120--180 ms after perturbation onset, so do not label the measured
  endpoint response purely intrinsic tissue stiffness. Supports task-dependent
  impedance geometry, not a universal golf gradient or clinical protection.
- Hogan (1985), Part I, DOI 10.1115/1.3140702: author-hosted PDF retrieved;
  abstract and opening framework read. It explicitly combines real-time
  controller and hardware and controls interaction in addition to movement.
  This is not the existing Hogan:1985 bibliography entry (a different paper).
  Continue the derivation/source figure review before final synthesis.
- Hogan (1984): local primary paper opening/model rationale read. Coactivation
  and impedance can be relevant while muscle activation still has a cost.
- Pruszynski et al. (2011), DOI 10.1038/nature10436: publisher abstract read;
  human stimulation and monkey recordings support cortical involvement in
  rapid multi-joint feedback. Full text is not yet verified; the old cached
  brain-sources/pruszynski2011.txt is a CAPTCHA response, not article evidence.
- Papaioannou and Dimitriou (2021), DOI 10.1126/sciadv.abe0401: primary abstract
  read; preparatory spindle-afferent and stretch-response changes support
  task dependence. Do not claim direct human gamma-motor-neuron recording.
  Repository PDF returned 403; PMC returned CAPTCHA. Full article pending.

Access failures are recorded rather than treated as successful reading. The
cached Nature PDF attempt is HTML, not a valid paper. No scientific assertion
is supported by that file. Primary paper figure QA and independent examples
remain next steps.

## Delivery Context

Shaft PR #4335 has normal squash auto-merge enabled; substantive tests and E2E
are still running on cbd611369542cb3c63a1b4bf171936e8b665867c. Replay only passive
commits after that parent onto the eventual protected shaft squash before push.

Muscle PR #4332 is published through descendant a81f99c06c34d3a98ad215a26218537861e49d1a.
Its deploy run 34433303512 succeeded. Exact live artifact 10135966540 was
inspected record by record: 956 records, 239 routes and 239 axe routes; all
HTTP 200/pass, zero inspection failures, axe findings, retries or transients.
The original muscle-only deployment was cancelled; this descendant includes
only fleet policy changes beyond the protected muscle source. Do not describe
the cancelled run as successful.
