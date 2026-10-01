# Ground-Reaction Boundaries and Archived Matching Evidence

Issue #4730 is a child of epic #4009. This pass reads and corrects complete
companion Chapter 16 and its ground-ledger figure. Other chapters retain their
previous scopes. Provider revision `a1a613999eb0c744da96caa040941955eb210a21`
is immutable; no provider source or simulation was changed or executed.

## Mechanical Corrections

The chapter declares the body-plus-club boundary, distinguishes internal hand
wrenches from external ground and gravity, and uses a fixed inertial origin for
angular momentum closure. Ground power includes force and moment paired with
the matching rigid-body velocities. Deforming contact requires local material
velocity; migration of a pressure resultant is not contact work. Kinetic-energy
growth can release existing gravitational or elastic storage.

The six-axis plate convention transports moments to a specified surface before
COP calculation and retains the surface-normal free moment. The finite-base
archive's world-y pitch moment is a different quantity. Pressure measurements
do not directly supply shear or muscle forces. A net wrench leaves bilateral
allocation unresolved, while separate plates measure aggregate foot wrenches;
two feet alone do not imply a rank-deficient forward problem.

The constrained-reaction equation states positive-definite mass, full row rank,
conditioning, fixed contact rows and load conventions. Ground ZVCF zeros both
velocity and declared controls; zero velocity with control retained has its own
name. ZTCF and ZVCF overlap. Nonlinear COP ratios must be calculated after each
counterfactual wrench, and the total plate wrench does not independently measure
each modeled component.

## Archived Numerical Findings

Independent NumPy recomputation from the pinned NPZ verifies the work and load
relative errors, primary zero matches, and post-hoc cohort. The work metric is
a symmetric relative difference capped at two for nonnegative inputs. The old
claim of roughly twice the dissipated energy was false: the actual ratios range
from 13.44 to 3519.40, with no active work floor. The 200% tolerance endpoint is
vacuous and does not estimate the smallest tolerance that yields a match.

Only 202 of 384 summaries meet the 5% load criterion. None also meets total-work
matching. The load quantity is the maximum single-station force norm over the
interval (`_record_horizon`), not summed hand force. The 60 alternative-work matches occur at 4/10/25/50 ms in counts
48/8/4/0, with 20 positive and 40 negative speed differences. The 48 finer-step
50 ms comparisons all favor coupled support by 0.028--0.177 m/s, but use a
different cohort and estimand. Numerical backends, timesteps and horizons do not
constitute independent human samples.

The primary matching failure remains the primary result. A total trajectory
contrast under a declared model intervention is still meaningful within that
model: dissipation is partly downstream of the support change. It does not
establish an equal-work benefit, human causation, optimal coordination or impact
performance. Reachable pinned history introduces atlas code and results together;
a separate prospective registration was not verified, so the chapter says
declared primary criterion. Numerical/refinement gates are distinguished from
the failed matching screen. Initialization comparisons identify exactly which
coordinates are equilibrated and which preload is omitted.

The earlier noncentral vector-dashpot issue UpstreamDrift #11195 does not apply
automatically. This archive's distributed grip selects central tension-only
fibers through `articulated_slack_contact.py`; force is collinear with endpoint
separation, and the pair moment vanishes. Shared contact laws and integration
still limit the independence of native-operator parity.

## Primary Reading Scope

- Han et al. (2019): publisher/PubMed metadata and complete abstract, not full
  paper. Supports sample, clubs, instrumentation and association language.
  <https://pubmed.ncbi.nlm.nih.gov/31042142/>
- Ball and Best (2007): PubMed metadata and complete abstract, not full paper.
  Supports 62 golfers and direction-of-hit COP clusters, not exhaustive 2D styles.
  <https://pubmed.ncbi.nlm.nih.gov/17454544/>
- Watson et al. (2026): full-text methods, study tables, discussion and limitations
  inspected for the review's own synthesis. Its descriptions of individual
  studies were not substituted for reading those originals. The chapter uses
  only the bounded synthesis of 24 studies, mostly cross-sectional designs,
  methodological variation and unresolved intervention/reliability questions.
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC13198453/>
- Pinned provider Chapters 03c and 06ca read completely; atlas, sensitivity and
  diagnostic JSON read; relevant matching, integration, ground and distributed
  contact implementation inspected. Exact file hashes and independent archive
  recomputation are in `ground-conversation-archive-checks.json`.

Two agy Gemini 3.8 Flash High supplied-text inventories assisted claim discovery.
They had no tools, network or editing authority. The lead rejected automatic
two-foot rank-deficiency claims and claims that every contact problem is an
LCP/QP, and independently checked the accepted mechanical/numerical findings.

## Publication Status

Scientific corrections, 40 focused checks, all twelve content gates and final
PDF/browser inspection are complete. The 213-page PDF has all nine chapter pages
plus contents and the next-chapter boundary inspected. Four viewport/theme cases
pass with zero serious/critical axe findings. All 57 unchanged prior publication
dependencies are verified; only Chapter16, the rebuilt PDF and bounded legacy ground assertions changed
within that prior set. The legacy test previously required the inaccurate
blanket fairness claim; it now checks both estimands and the post-hoc horizon
boundary. Full repository validation and protected delivery remain pending.
No whole-book or live-deployment certification is implied.
