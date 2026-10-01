# Arm–Wrist Preload Technical Review

Issue #4753 extends epic #4009 and corpus review #4021. The full source of
`ch14_arms_wrists_preload.qmd` was read and corrected. This is a supplemental
chapter review, not completion of the whole companion or a new review of every
linked monograph. The 48 prior companion findings are preserved separately in
`preload-prior-review.json`.

## Scientific Corrections

1. **Matched Moment and Wrench.** The pinned allocation solver subtracts drift
   before computing the control contribution. Its target is the club angular
   acceleration increment multiplied by inertia, not the full wrench. Contact
   RMS also uses control increments. Fixed-state linearity preserves the scalar
   target under convex mixing but does not establish contact or strength
   feasibility. Unweighted generalized-torque norm is not physiological effort.
   Wrist actuation also changes constraint forces. A synthetic two-contact
   counterexample holds moment at 8 N m while changing resultant force by 20 N.
2. **Commands, State, and Figure.** The old figure used 8/-2 N m preparation
   instead of the registered 10/-4 and plotted only command steps while claiming
   transmission histories. It now reads the exact archived NPZ at the pinned
   provider revision, displaying transmitted torque and correct dashed commands.
   Both histories start relaxed, evolve for 180 ms, then continue without reset.
   The half-width, stiffness, time constants, lag equation, torque law, and
   distinction from a coupled anatomical simulation are explicit.
3. **Tracking Score and Delays.** Recomputing the stored traces reproduces
   absolute net error integrals 0.07171505681942013 and 0.1954089217169282 N m s
   over 120 ms. They are neither work nor signed angular impulse. The 0.1 ms
   grid's zero occupancies (11.5/22 ms) differ from first attainment of 10% target
   in the new direction (15.7/31.1 ms). Sampling brackets are not confidence
   intervals or total numerical-error bounds. Finite preparation is close to,
   but distinct from, equilibrium initialization.
4. **Conditional Negative Control.** Zero dead zone, common time constant, equal
   initial sums, and equal future net commands imply identical net responses by
   the summed linear ODE. An independent unequal-time-constant example violates
   equality. Lag remains when the gap is removed. The registered grid's result
   is conditional on its specified family and score, not a physiological law.
5. **Stiffness and Identification.** Opposing preloaded elements can have zero
   net torque and positive restoring stiffness. Preload is a load, not a
   stiffness measurement. The typed-slack audit's local within-class rank does
   not prove global, practical, or between-class identifiability. The 0.0196
   normalized output separation is not a statistical detection threshold.
6. **Causal Comparisons.** Scalar task, full wrench, trajectory, and terminal
   matching are distinct constraints. Configuration alone omits velocity and
   memory; state interventions can alter energy and momentum. Equal full state
   and future inputs imply equal deterministic motion by uniqueness and do not
   independently establish mediation. Null results require an established
   manipulation, adequate precision, and a declared useful-effect threshold.
7. **Human Evidence.** Corrected the first author of the 1995 scapular study to
   Kao. The publisher/PubMed abstracts of Kao et al. and Robinson et al. were
   checked; full papers were not reviewed. Their EMG results do not identify the
   proposed bilateral wrench allocation, and nonsignificance is not equivalence.

## Evidence and Derivations

Provider revision: `85cce4d3307bb7ad3953d9fc6e583e370803515c` in UpstreamDrift.
The provider receipt records SHA-256 hashes for the read chapter, source module,
JSON results, and exact NPZ copy. The archived simulation was not rerun. Six
local tests recompute its published metrics, check the replacement figure, and
exercise independent moment/wrench, time-constant, and stiffness counterexamples.
The figure regression failed before implementation because no transmitted trace
was plotted, then passed after the replacement.

Primary literature checked:

- [Kao et al. (1995), Scapular EMG](https://pubmed.ncbi.nlm.nih.gov/7726345/),
  DOI 10.1177/036354659502300104: abstract and bibliographic identity only.
- [Robinson et al. (2023), Wrist EMG and Kinematics](https://pubmed.ncbi.nlm.nih.gov/37983261/),
  DOI 10.1080/02640414.2023.2285121: abstract and bibliographic identity only.

## Delegation and Adjudication

Supplied-text agy Gemini 3.8 Flash jobs handled the source inventory, provider
code inventory, numerical-test draft, and notation review. Lead decisions and
validation remain authoritative. The code inventory's universal claim that
proximal control inevitably creates a nonzero resultant was rejected; neither
that nor universally greater contact force follows from the code. The numerical
draft's absolute-magnitude delay test omitted the new-direction condition and
would count the initial opposing torque; the implemented check includes sign.
Its claim that delay must always exceed zero occupancy was also rejected as a
general statement. Recorded inequalities apply to these specific traces.

## Publication Checkpoint

The 220-page companion PDF was regenerated with canonical/public byte parity.
All revised Chapter14 pages89–96 (PDF page indices counted from1), plus pages88
and97 at the boundaries, were visually inspected. The final figure legend does
not obscure the traces. All four display equations fit the mobile viewport;
57 chapter math expressions render without errors or page overflow. Four
mobile/desktop light/dark cases pass, with zero serious/critical axe violations.

All63 affected tests pass. Twelve publication gates,654-source title audit,
repository Ruff/Black835 and CI-scoped mypy94 pass. The broader regression is
running on the stable final publication; no final outcome is asserted here.
Five supplied-text Flash jobs completed, including the turnover checklist.
