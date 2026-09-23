# Bibliographic Analysis: Force and Mobility Ellipsoids in the Golf Swing

## A) Concept Map

- **Geometric Analysis**

  - **Manipulability Ellipsoid**: Geometric representation of kinematic capability ($\dot{x} = J\dot{q}$).
  - **Force Ellipsoid**: Geometric representation of static force transmission ($\tau = J^\top F$).
  - **Singular Value Decomposition (SVD)**: Mathematical tool to extract principal axes ($\sigma_i$) of the Jacobian.
  - **Duality**: The power pairing ($F^\top v = Q_F^\top \dot{q}$); reciprocal ellipsoid radii additionally require dual normalized budgets. Duality does not mean orthogonality.

- **Multibody Dynamics**

  - **Jacobian Matrix ($J$)**: The linear mapping from joint space velocities to task space velocities.
  - **Kinematic Singularity**: Configurations where rank($J$) drops, losing mobility in certain directions.
  - **Double Pendulum**: Canonical planar linkage model for the golf swing.
  - **Constraint Surfaces**: Restrictions on permitted velocities; ideal reactions do no work on those velocities. Reaction feasibility and structural load limits require additional models.

- **Biomechanics**
  - **Mechanical Advantage**: Leverage ratios changing with configuration.
  - **Effective Inertia**: The apparent mass felt at the end-effector.
  - **Intersegmental Dynamics**: Coupling between proximal (torso/arm) and distal (club) segments.

## B) Bibliography (YAML)

This is a reading-candidate catalog, not a claim that every full text was
reviewed. `related_ids` are editorial topic connections. No outgoing citation
edges are asserted without checking the cited work's reference list.
The verified source access for this correction is listed after the catalog.

```yaml
- id: yoshikawa1985manipulability
  title: "Manipulability of robotic mechanisms"
  authors:
    - "Tsuneo Yoshikawa"
  year: 1985
  venue: "The International Journal of Robotics Research"
  scholar_link: "https://scholar.google.com/scholar?q=Manipulability+of+robotic+mechanisms+Yoshikawa"
  clusters: ["robotics", "kinematics", "geometric analysis"]
  concepts: ["manipulability ellipsoid", "jacobian", "singularity"]
  related_ids: ["chiu1988task", "salisbury1982articulated"]
  references_out_ids: []

- id: salisbury1982articulated
  title: "Articulated hands: Force control and kinematic issues"
  authors:
    - "J. Kenneth Salisbury"
    - "John J. Craig"
  year: 1982
  venue: "The International Journal of Robotics Research"
  scholar_link: "https://scholar.google.com/scholar?q=Articulated+hands+Force+control+and+kinematic+issues+Salisbury"
  clusters: ["robotics", "force control"]
  concepts: ["force ellipsoid", "grasping", "jacobian transpose"]
  related_ids: ["yoshikawa1985manipulability"]
  references_out_ids: []

- id: chiu1988task
  title: "Task compatibility of manipulator postures"
  authors:
    - "Stephen L. Chiu"
  year: 1988
  venue: "The International Journal of Robotics Research"
  scholar_link: "https://scholar.google.com/scholar?q=Task+compatibility+of+manipulator+postures+Chiu"
  clusters: ["robotics", "optimization"]
  concepts: ["task compatibility", "velocity ellipsoid", "force ellipsoid"]
  related_ids: ["yoshikawa1985manipulability"]
  references_out_ids: []

- id: khatib1987unified
  title: "A unified approach for motion and force control of robot manipulators: The operational space formulation"
  authors:
    - "Oussama Khatib"
  year: 1987
  venue: "IEEE Journal of Robotics and Automation"
  scholar_link: "https://scholar.google.com/scholar?q=A+unified+approach+for+motion+and+force+control+of+robot+manipulators+Khatib"
  clusters: ["robotics", "control"]
  concepts: ["operational space", "effective inertia", "kinetic energy matrix"]
  related_ids: ["hogan1985impedance"]
  references_out_ids: []

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:
    - "Kevin M. Lynch"
    - "Frank C. Park"
  year: 2017
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Mechanics+Planning+and+Control+Lynch"
  clusters: ["robotics", "textbook"]
  concepts: ["geometric jacobian", "screw theory", "manipulability"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors:
    - "Richard M. Murray"
    - "Zexiang Li"
    - "S. Shankar Sastry"
  year: 1994
  venue: "CRC Press"
  scholar_link: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
  clusters: ["robotics", "mathematical foundations"]
  concepts: ["twist", "wrench", "adjoint map"]
  related_ids: ["lynch2017modern"]
  references_out_ids: []

- id: sprigings2000insight
  title: "An insight into the importance of wrist torque in driving the golf ball: a simulation study"
  authors:
    - "Eric J. Sprigings"
    - "Robert J. Neal"
  year: 2000
  venue: "Journal of Applied Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=An+insight+into+the+importance+of+wrist+torque+Sprigings"
  clusters: ["golf biomechanics", "simulation"]
  concepts: ["double pendulum", "wrist torque", "kinetics"]
  related_ids: ["nesbit2005work", "mackenzie2009three"]
  references_out_ids: []

- id: nesbit2005work
  title: "Work and power analysis of the golf swing"
  authors:
    - "Steven M. Nesbit"
    - "Monika Serrano"
  year: 2005
  venue: "Journal of Sports Science and Medicine"
  scholar_link: "https://scholar.google.com/scholar?q=Work+and+power+analysis+of+the+golf+swing+Nesbit"
  clusters: ["golf biomechanics", "energetics"]
  concepts: ["power transfer", "joint kinetics", "energy flow"]
  related_ids: ["sprigings2000insight"]
  references_out_ids: []

- id: hogan1985impedance
  title: "Impedance control: An approach to manipulation"
  authors:
    - "Neville Hogan"
  year: 1985
  venue: "Journal of Dynamic Systems, Measurement, and Control"
  scholar_link: "https://scholar.google.com/scholar?q=Impedance+control+An+approach+to+manipulation+Hogan"
  clusters: ["robotics", "motor control"]
  concepts: ["impedance", "stiffness ellipsoid", "interaction"]
  related_ids: ["khatib1987unified"]
  references_out_ids: []

- id: zatsiorsky2002kinetics
  title: "Kinetics of Human Motion"
  authors:
    - "Vladimir M. Zatsiorsky"
  year: 2002
  venue: "Human Kinetics"
  scholar_link: "https://scholar.google.com/scholar?q=Kinetics+of+Human+Motion+Zatsiorsky"
  clusters: ["biomechanics", "textbook"]
  concepts: ["muscle mechanics", "joint moments", "transformation matrices"]
  related_ids: ["winter2009biomechanics"]
  references_out_ids: []

- id: strang2016introduction
  title: "Introduction to Linear Algebra"
  authors:
    - "Gilbert Strang"
  year: 2016
  venue: "Wellesley-Cambridge Press"
  scholar_link: "https://scholar.google.com/scholar?q=Introduction+to+Linear+Algebra+Strang"
  clusters: ["mathematics", "linear algebra"]
  concepts: ["singular value decomposition", "eigenvalues", "matrix rank"]
  related_ids: []
  references_out_ids: []

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors:
    - "Roy Featherstone"
  year: 2008
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters: ["dynamics", "algorithms"]
  concepts: ["spatial algebra", "articulated body inertia", "hybrid dynamics"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

- id: corke2017robotics
  title: "Robotics, Vision and Control: Fundamental Algorithms in MATLAB"
  authors:
    - "Peter Corke"
  year: 2017
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Robotics+Vision+and+Control+Corke"
  clusters: ["robotics", "software"]
  concepts: ["manipulability", "jacobian", "matlab implementation"]
  related_ids: ["lynch2017modern"]
  references_out_ids: []
```

## C) Verified Sources and Reading Sequence

The correction consulted the publisher's Modern Robotics transcripts for
[statics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-2-statics-of-open-chains/),
[manipulability](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-4-manipulability/),
[task-space dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-6-dynamics-in-the-task-space/)
and [constrained dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-7-constrained-dynamics/).
These establish the starting conventions; the article's weighted budgets,
rank-deficient cases and numerical counterexamples are explicit derivations.
The task-dynamics transcript assumes a square invertible Jacobian; the
rectangular extension must retain internal dynamics and bias terms.

Read the statics and manipulability treatments together, keeping the chosen
rate and load budgets visible. Then use task and constrained dynamics to see
why inertia and contact change acceleration without changing the underlying
power identity. Compliance needs a constitutive law as well as geometry.

The [NumPy SVD documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)
specifies full and reduced matrix shapes. The published example uses the full
task basis so that a tall matrix does not hide ambient null directions. Its
relative numerical threshold is a declared approximation, not a physical
singularity test. Independent regression checks cover rectangular and zero
maps, scaling, power pairing and mechanical counterexamples.

The [journal's Nesbit and Serrano record](https://www.jssm.org/hfabst.php?id=jssm-04-520.xml)
confirms both authors of the 2005 work-and-power paper. Only its metadata and
abstract were checked for this correction; no new empirical golf conclusion
is inferred from that access. The other catalog items are further-reading
candidates, not substitutes for verified sources or measured human capacities.
