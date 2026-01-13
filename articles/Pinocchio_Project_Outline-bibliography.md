# A Comprehensive Roadmap for Building a Full-Body, Physics-Grounded, IK/Dynamics-Driven Golfer Simulation Toolkit

# Bibliography

## Concept Map

- **Canonical Model Specification**: A single source of truth (YAML) for kinematics and dynamics that generates backend-specific formats (URDF, MJCF).
- **Control-Affine Dynamics**: Modeling the system as $\dot{x} = f(x) + g(x)u$ to enable counterfactual analysis.
- **Inverse Kinematics (IK)**: Solving for joint configurations given task-space goals (e.g., clubhead trajectory) using differential IK (Pink).
- **Inverse Dynamics (ID)**: Computing required joint torques to achieve a given motion (Pinocchio).
- **Counterfactual Physics**:
  - **Zero Torque Counterfactual (ZTCF)**: Simulating motion with $u=0$ to isolate passive drift.
  - **Zero Velocity Counterfactual (ZVCF)**: Isolating configuration-dependent forces.
- **Holonomic Constraints**: Modeling closed chains (e.g., two hands on a club) as rigid constraints.
- **Multibody Simulation**: Integrating equations of motion with contact and constraints (MuJoCo, Pinocchio).

## References

bibliography:

- id: carpentier2019pinocchio
  title: "Pinocchio: An efficient and rigid multi-body dynamics library"
  authors:

  - Carpentier, J.
  - Saurel, G.
  - Buondonno, G.
  - Mirabel, J.
  - Lamiraux, F.
  - Stasse, O.
  - Mansard, N.
    year: 2019
    venue: "IEEE International Conference on Robotics and Automation (ICRA)"
    scholar_link: "https://scholar.google.com/scholar?q=Pinocchio+Carpentier+ICRA+2019"
    clusters: ["robotics", "software", "simulation"]
    concepts: ["rigid body dynamics", "recursive algorithms", "C++"]
    related_ids: ["featherstone2008rigid", "caron2024pink"]
    references_out_ids: ["featherstone2008rigid", "mansard2018unified"]

- id: todorov2012mujoco
  title: "MuJoCo: A physics engine for model-based control"
  authors:

  - Todorov, E.
  - Erez, T.
  - Tassa, Y.
    year: 2012
    venue: "IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)"
    scholar_link: "https://scholar.google.com/scholar?q=MuJoCo+physics+engine+Todorov"
    clusters: ["simulation", "robotics", "control"]
    concepts: ["contact dynamics", "soft constraints", "physics engine"]
    related_ids: ["carpentier2019pinocchio"]
    references_out_ids: ["tassa2012synthesis", "erez2015simulation"]

- id: caron2024pink
  title: "Pink: Python inverse kinematics for articulated robot models"
  authors:

  - Caron, S.
    year: 2024
    venue: "GitHub Repository"
    scholar_link: "https://scholar.google.com/scholar?q=Stephane+Caron+Pink+inverse+kinematics"
    clusters: ["robotics", "software", "kinematics"]
    concepts: ["differential IK", "task-space control", "quadratic programming"]
    related_ids: ["carpentier2019pinocchio", "kanoun2011kinematic"]
    references_out_ids: ["kanoun2011kinematic", "escande2014hierarchical"]

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors:

  - Featherstone, R.
    year: 2008
    venue: "Springer"
    scholar_link: "https://scholar.google.com/scholar?q=Featherstone+Rigid+Body+Dynamics+Algorithms"
    clusters: ["robotics", "mechanics"]
    concepts: ["spatial algebra", "recursive newton-euler", "articulated body algorithm"]
    related_ids: ["carpentier2019pinocchio", "lynch2017modern"]
    references_out_ids: ["jain2010robot", "murray1994mathematical"]

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:

  - Lynch, K. M.
  - Park, F. C.
    year: 2017
    venue: "Cambridge University Press"
    scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Lynch+Park"
    clusters: ["robotics", "mechanics"]
    concepts: ["screw theory", "product of exponentials", "lagrangian dynamics"]
    related_ids: ["murray1994mathematical"]
    references_out_ids: ["bullo2005geometric", "spong2005robot"]

- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors:

  - Murray, R. M.
  - Li, Z.
  - Sastry, S. S.
    year: 1994
    venue: "CRC Press"
    scholar_link: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
    clusters: ["robotics", "mechanics", "math"]
    concepts: ["lie groups", "manipulator dynamics", "holonomic constraints"]
    related_ids: ["lynch2017modern"]
    references_out_ids: ["khatib1987unified", "siciliano2016springer"]

- id: khatib1987unified
  title: "A unified approach for motion and force control of robot manipulators"
  authors:

  - Khatib, O.
    year: 1987
    venue: "IEEE Journal of Robotics and Automation"
    scholar_link: "https://scholar.google.com/scholar?q=Khatib+unified+approach+motion+force+control"
    clusters: ["robotics", "control"]
    concepts: ["operational space", "force control", "null space"]
    related_ids: ["siciliano1990kinematic"]
    references_out_ids: ["nakanishi2008operational", "aghili2005unified"]

- id: siciliano1990kinematic
  title: "Kinematic Control of Redundant Robot Manipulators: A Tutorial"
  authors:

  - Siciliano, B.
    year: 1990
    venue: "Journal of Intelligent and Robotic Systems"
    scholar_link: "https://scholar.google.com/scholar?q=Siciliano+Kinematic+Control+Redundant"
    clusters: ["robotics", "kinematics"]
    concepts: ["redundancy", "pseudoinverse", "null space projection"]
    related_ids: ["khatib1987unified"]
    references_out_ids: ["chiaverini1997singularity", "nakamura1991advanced"]

- id: geppetto_viewer
  title: "Geppetto Viewer: A graphical interface for Pinocchio"
  authors:

  - Mirabel, J.
  - et al.
    year: 2016
    venue: "GitHub Repository (LAAS-CNRS)"
    scholar_link: "https://scholar.google.com/scholar?q=Geppetto+viewer+LAAS+CNRS"
    clusters: ["software", "visualization"]
    concepts: ["robot visualization", "scene graph", "interactive robotics"]
    related_ids: ["carpentier2019pinocchio"]
    references_out_ids: []

- id: meshcat_python
  title: "MeshCat-Python: WebGL-based 3D visualizer for Python"
  authors:

  - Deits, R.
    year: 2019
    venue: "GitHub Repository"
    scholar_link: "https://scholar.google.com/scholar?q=MeshCat+Python+Robin+Deits"
    clusters: ["software", "visualization"]
    concepts: ["webgl", "visualization", "jupyter integration"]
    related_ids: ["todorov2012mujoco"]
    references_out_ids: []

- id: mackenzie2009three
  title: "A three-dimensional forward dynamics model of the golf swing"
  authors:

  - MacKenzie, S. J.
  - Sprigings, E. J.
    year: 2009
    venue: "Sports Engineering"
    scholar_link: "https://scholar.google.com/scholar?q=MacKenzie+Sprigings+2009+golf+swing"
    clusters: ["golf", "biomechanics"]
    concepts: ["forward dynamics", "muscle torque", "optimization"]
    related_ids: ["nesbit2005three"]
    references_out_ids: []

- id: shabana2020dynamics
  title: "Dynamics of Multibody Systems"
  authors:

  - Shabana, A. A.
    year: 2020
    venue: "Cambridge University Press"
    scholar_link: "https://scholar.google.com/scholar?q=Dynamics+of+Multibody+Systems+Shabana"
    clusters: ["multibody dynamics", "mechanics"]
    concepts: ["flexible bodies", "constrained dynamics", "lagrangian mechanics"]
    related_ids: ["featherstone2008rigid"]
    references_out_ids: []

- id: isidori1995nonlinear
  title: "Nonlinear Control Systems"
  authors:
  - Isidori, A.
    year: 1995
    venue: "Springer"
    scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Control+Systems+Isidori"
    clusters: ["control theory", "math"]
    concepts: ["affine systems", "lie brackets", "feedback linearization"]
    related_ids: ["murray1994mathematical"]
    references_out_ids: ["nijmeijer1990nonlinear", "sastry1999nonlinear"]

## Reading Paths

### Path 1: Fast ramp (Software & Tools)

1.  **Pinocchio (Carpentier et al., 2019)** - The core library for rigid body dynamics algorithms.
2.  **MuJoCo (Todorov et al., 2012)** - The physics engine for contact and realistic simulation.
3.  **Pink (Caron, 2024)** - The differential inverse kinematics solver for task-based motion.
4.  **MeshCat (Deits, 2019)** - The tool for lightweight, browser-based 3D visualization.
5.  **Modern Robotics (Lynch & Park, 2017)** - Chapter 8 (Dynamics of Open Chains) provides the theoretical basis for these tools.

### Path 2: Deep technical (Dynamics & Algorithms)

1.  **Rigid Body Dynamics Algorithms (Featherstone, 2008)** - The bible for the recursive algorithms (RNEA, ABA) implemented in Pinocchio.
2.  **Dynamics of Multibody Systems (Shabana, 2020)** - Essential for understanding constrained systems and flexible bodies.
3.  **Kinematic Control of Redundant Robot Manipulators (Siciliano, 1990)** - Fundamental for understanding null-space resolution in IK.
4.  **A Unified Approach... (Khatib, 1987)** - The operational space formulation which underpins modern force control.
5.  **Nonlinear Control Systems (Isidori, 1995)** - Theory for the affine control structure ($\dot{x} = f(x) + g(x)u$) and drift fields.
6.  **Mathematical Introduction to Robotic Manipulation (Murray et al., 1994)** - Rigorous treatment of geometric mechanics.

### Path 3: Implementation (Golf Biomechanics)

1.  **MacKenzie & Sprigings (2009)** - The baseline 3D forward dynamics model to replicate.
2.  **Pinocchio Documentation** - Tutorials on loading URDFs and computing Jacobians.
3.  **Pink Documentation** - Examples of solving IK for humanoid robots.
4.  **MuJoCo Documentation** - Guides on defining MJCF models and equality constraints.
5.  **Geppetto Viewer** - Using the viewer to validate joint frames and kinematics visually.
