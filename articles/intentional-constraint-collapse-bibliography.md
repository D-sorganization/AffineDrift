# Intentional Constraint Collapse at Impact
# Bibliography

## Concept Map

- **Constraint Jacobian**: The linear mapping between joint velocities and constraint violations.
- **Nullspace**: The subspace of joint configurations or velocities that do not affect the primary task (clubhead motion).
- **Impedance Control**: Regulating the dynamic relationship between force and motion (stiffness/damping).
- **Redundancy**: Having more degrees of freedom than required for the task.

## References

bibliography:
  - id: hogan1985
    title: "The mechanics of multi-joint posture and movement control"
    authors: "Hogan, N."
    year: 1985
    venue: "Biological Cybernetics"
    scholar_link: "https://scholar.google.com/scholar?q=Hogan+mechanics+multi-joint+posture"

  - id: latash2010
    title: "Neurophysiological Basis of Motor Control"
    authors: "Latash, M. L."
    year: 2010
    venue: "Human Kinetics"
    scholar_link: "https://scholar.google.com/scholar?q=Latash+Neurophysiological+Basis+Motor+Control"

  - id: yoshikawa1990
    title: "Foundations of Robotics: Analysis and Control"
    authors: "Yoshikawa, T."
    year: 1990
    venue: "MIT Press"
    scholar_link: "https://scholar.google.com/scholar?q=Yoshikawa+Foundations+of+Robotics"

## Reading Paths

### Fast ramp (Start here)
1.  [hogan1985] - Foundational text on impedance control in biological systems.

### Deep technical (The math)
1.  [yoshikawa1990] - Standard reference for redundancy and manipulability.

### Implementation (How to simulate)
1.  [latash2010] - Detailed discussion on muscle synergies and redundancy.
