# Anatomy and Joint Modeling Review

## Scope and Current Acceptance

Issue [#4412](https://github.com/D-sorganization/AffineDrift/issues/4412) continues
the Physics review #4054 under corpus #4021 and epic #4009. Both Chapter 22
sources were inspected, including their differing injury language, taxonomy,
anatomical sections, summary and seven exercises. This is an intermediate
correction record, not completed chapter acceptance. The current commit corrects
the joint taxonomy and independent kinematic examples. The biological sections,
model-selection advice, injury interpretation, exercises and full print/web
validation remain to be corrected and verified.

## Why the Review Was Reopened

At base `bc22952d`, the route was marked reviewed with no findings and only
the QMD source as evidence, bound to `4f372cd4326fc94c82500334af22b407b098febd`.
That source still equated a scalar with a vector in the hinge constraints,
misstated the universal-joint constraint, and claimed its perpendicular axes
could align and lock. The body-count explanation also disagreed between print
and web. These are direct counterexamples to complete scientific acceptance.
Issues #4054, #4021 and #4009 were reopened; #4412 is a native child of #4054.
The chapter route returns to deferred while its substantive review is incomplete.
Other routes are not reclassified without inspection.

## Joint Geometry and Mechanical Interpretation

- Define frames at joint origins and distinguish their coincidence from the
  movement of segment centers of mass. A revolute joint aligns two body-fixed
  unit axes: three written alignment components have differential rank two.
- A prismatic joint must suppress two transverse translations. One unspecified
  perpendicular dot product is insufficient.
- Unit quaternion component count is not rotational mobility. An Euler chart
  singularity does not remove a spherical joint's physical rotational freedom.
- The universal joint imposes orthogonality of one axis fixed in each body.
  Its angular-velocity columns stay orthonormal in the explicit two-angle
  parameterization. A fixed-normal preservation equation rejects legitimate
  motion. Driveshaft transmission geometry, task Jacobians and local joint
  freedom must not be conflated.
- Derive generalized moment by virtual power, using the current rate map.
  Ideal reaction moments can carry load while doing no relative work.
- Count the fixed-base weld or merge the base with ground. A missing weld
  explains the extra six freedoms; planarity is not the error. For loops, use
  independent closure rank and distinguish infinitesimal mobility at a singular
  configuration from realizable finite motion.

The independent tests use finite rotation increments, differential constraint
rank, power pairing, Euler chart rank and an axial point-displacement example.
The initial regression run failed in both editions, with six mathematical
checks passing. After correction all eight checks pass. These checks support
the stated equations; they do not prove human joint fidelity or clinical risk.

## Outstanding Findings

1. Replace categorical knee fidelity/optimization claims and unsupported error
   percentages with task-specific sensitivity and identifiability reasoning.
2. Correct coupled shoulder topology, moving centers, scapulohumeral rhythm and
   the distinction between humerothoracic and glenohumeral measurements.
3. Correct dart-throwing direction, forearm rotation, stiffness coupling and
   the distinction between club orientation in space and grip slip.
4. Reconcile hip measurement/FAI framing, elbow carrying-angle inference and
   ankle/foot contact and elastic-energy interpretation.
5. Replace the false per-arm/full-body count and give a complete topology.
6. Remove unsupported clinical thresholds, phase-specific universal spinal
   loads, inferred eccentric recruitment and DCR-based injury explanation.
   Explain what measurements and models can actually identify.
7. Rework all seven exercises with adequate data and explicit worked answers.
8. Verify citations, inspect complete rendered chapter in print/web, bind the
   completed review to source and evidence commits, and pass protected checks.

## Sources Read and Reading Limits

- Lynch and Park, [Modern Robotics, section 2.2 video transcript](https://modernrobotics.northwestern.edu/nu-gm-book-resource/2-2-degrees-of-freedom-of-a-robot/):
  joint freedom and independent constraints. The detailed frame/rate/power
  derivations above are independently reconstructed and numerically checked.
- Crisco et al. (2005), [publisher abstract via PubMed](https://pubmed.ncbi.nlm.nih.gov/16322624/):
  radial extension toward ulnar flexion and measured carpal kinematics; does
  not establish a universally strongest wrist motion or a golf coaching rule.
- McClure et al. (2001), [abstract](https://pubmed.ncbi.nlm.nih.gov/11408911/):
  eight volunteers, bone-pin scapular measurements and three-dimensional motion
  during arm elevation. This is not a golf-specific rhythm calibration.
- Seth et al. (2016), [abstract](https://pubmed.ncbi.nlm.nih.gov/26734761/):
  scapulothoracic joint modeling. Full PMC retrieval returned a challenge page;
  full-paper reading is not claimed at this checkpoint.
- Seth et al. (2019), [abstract](https://pubmed.ncbi.nlm.nih.gov/31780916/):
  coupling scapular movement to humeral movement can change modeled muscle
  work attribution. Full-paper methods and results remain to be read.

The knee, hip and clinical sources found during discovery remain candidates
until their actual abstracts or full text are inspected. Search snippets alone
do not qualify a numerical or clinical statement.

## Publication Checkpoint From the Previous Session

PR #4377 is merged at `32010d08d9980896c51f0c93ac875f23eb818556`.
Its exact Deploy Website run `34730740904` completed successfully. Live artifact
`10309497076` is available but has not yet been inspected in this resumed
session; earlier delivery-log entries must not claim that inspection.
