# Figures Inventory and Parity Audit: The Physics of Golf

This document provides the formal audit and inventory of all figures across the LaTeX book sources and their Quarto website mirrors, tracking figure types, labels, captions, and parity gaps.

## Summary Metrics

| Metric | Value |
|---|---|
| **Total Chapters Audited** | 34 |
| **Chapters with Figures** | 29 |
| **Total LaTeX Figures** | 31 |
| **TikZ Figures** | 31 |
| **Raster / Includegraphics Figures** | 0 |
| **LaTeX Figure Labels** | 31 |
| **LaTeX Prose Figure Refs** | 3 |
| **Total Quarto Figures** | 0 |
| **Quarto Figure Defs (Divs / Imgs / Cells)** | 0 |
| **Quarto Prose Figure Mentions** | 5 |
| **Missing Figures in Quarto** | **31** |

## Chapter Parity Matrix

| Chapter Stem | Title | LaTeX Figs | TikZ | Quarto Figs | Parity Status |
|---|---|---|---|---|---|
| `ch01_why_physics` | Why Physics Matters in Golf | 1 | 1 | 0 | ❌ Missing 1 |
| `ch02_language_of_motion` | The Language of Motion | 1 | 1 | 0 | ❌ Missing 1 |
| `ch03_double_pendulum` | The Double Pendulum: Golf's Simplest Useful Model | 1 | 1 | 0 | ❌ Missing 1 |
| `ch04_forces_and_torques` | Forces and Torques: Where They Come From | 1 | 1 | 0 | ❌ Missing 1 |
| `ch05_affine_structure` | The Affine Structure: Drift and Control | 1 | 1 | 0 | ❌ Missing 1 |
| `ch06_zero_torque_counterfactual` | The Zero-Torque Counterfactual | 1 | 1 | 0 | ❌ Missing 1 |
| `ch07_constraint_forces` | Constraint Forces: The Hidden Engines of the Swing | 1 | 1 | 0 | ❌ Missing 1 |
| `ch08_triple_pendulum` | The Triple Pendulum: Adding the Wrists | 1 | 1 | 0 | ❌ Missing 1 |
| `ch09_parallel_mechanisms` | Parallel Mechanisms and Loop Constraints | 1 | 1 | 0 | ❌ Missing 1 |
| `ch09b_passive_stabilization` | Passive Stabilization in Parallel Loops | 2 | 2 | 0 | ❌ Missing 2 |
| `ch10_energy_transfer` | Energy Transfer: How Power Flows Through the Kinetic Chain | 1 | 1 | 0 | ❌ Missing 1 |
| `ch11_flexible_shaft` | The Flexible Shaft: Elastic Energy and the Catapult Effect | 2 | 2 | 0 | ❌ Missing 2 |
| `ch12_fascia` | Fascia and Connective Tissue: Separating Myth From Mechanics | 1 | 1 | 0 | ❌ Missing 1 |
| `ch13_interdisciplinary` | Where Disciplines Collide: An Interdisciplinary Perspective | 1 | 1 | 0 | ❌ Missing 1 |
| `ch14_complete_swing` | The Complete Golf Swing: Putting It All Together | 1 | 1 | 0 | ❌ Missing 1 |
| `ch15_ground_reaction_forces` | Ground Reaction Forces: The Silent Foundation | 0 | 0 | 0 | ✅ Parity |
| `ch16_muscle_to_joint_torques` | From Muscle Forces to Joint Torques | 1 | 1 | 0 | ❌ Missing 1 |
| `ch17_muscle_force_generation` | Muscle Force Generation: The Biological Engine | 1 | 1 | 0 | ❌ Missing 1 |
| `ch18_inverse_dynamics_parallel` | Inverse Dynamics and the Parallel Loop Problem | 1 | 1 | 0 | ❌ Missing 1 |
| `ch19_aerodynamic_drag` | Aerodynamic Drag: The Force You Cannot Ignore | 1 | 1 | 0 | ❌ Missing 1 |
| `ch20_soft_tissue_pliable` | Soft Tissue and Pliable Systems: Beyond the Rigid Body | 1 | 1 | 0 | ❌ Missing 1 |
| `ch21_spine_modeling` | Modeling the Spine: The Most Complex Joint in the Body | 1 | 1 | 0 | ❌ Missing 1 |
| `ch22_anatomy_joint_modeling` | Anatomy and Joint Modeling: Choosing the Right Idealization | 1 | 1 | 0 | ❌ Missing 1 |
| `ch23_dof_urdf_models` | Degrees of Freedom and Robot Models of the Human Body | 1 | 1 | 0 | ❌ Missing 1 |
| `ch24_motor_control_brain` | Motor Control I: The Brain as Controller | 1 | 1 | 0 | ❌ Missing 1 |
| `ch25_motor_learning` | Motor Control II: Learning the Swing | 1 | 1 | 0 | ❌ Missing 1 |
| `ch26_remarkable_brain` | Motor Control III: The Computational Brain | 0 | 0 | 0 | ✅ Parity |
| `ch27_passive_distributed_control` | Passive and Distributed Control: A Self-Organizing Swing Model | 0 | 0 | 0 | ✅ Parity |
| `ch28_impact_collision` | Impact: The Collision That Matters | 1 | 1 | 0 | ❌ Missing 1 |
| `ch29_joint_damping_friction` | Damping, Friction, and Energy Dissipation in the Kinematic Chain | 1 | 1 | 0 | ❌ Missing 1 |
| `ch30_kinetic_chain` | The Kinetic Chain: Sequential Energy Flow in the Golf Swing | 1 | 1 | 0 | ❌ Missing 1 |
| `ch30b_induced_acceleration` | Induced Acceleration Analysis: Quantifying Who Moves What | 0 | 0 | 0 | ✅ Parity |
| `ch31_swing_plane_launch` | Swing Plane, Clubface Control, and Launch Optimization | 1 | 1 | 0 | ❌ Missing 1 |
| `ch32_putting` | The Physics of Putting | 0 | 0 | 0 | ✅ Parity |

## Complete Figures Inventory

| Chapter | Fig # | Label | Type | Caption Summary |
|---|---|---|---|---|
| `ch01_why_physics` | 1 | `fig:ch01_drift_control_schematic` | TikZ Diagram | Schematic of Drift and Control Forces in the Golf Swing. Drift Forces (Blue) Include Gravi... |
| `ch02_language_of_motion` | 1 | `fig:ch02_arm_diagram` | TikZ Diagram | Double Pendulum Model of the Arm in Generalized Coordinates. The Shoulder Angle $\theta_1$... |
| `ch03_double_pendulum` | 1 | `fig:ch03_double_pendulum` | TikZ Diagram | Double Pendulum Model of the Golf Swing. Link 1 (Upper Arm, Blue) Rotates About the Should... |
| `ch04_forces_and_torques` | 1 | `fig:ch04_force_decomposition` | TikZ Diagram | The Five Sources of Torque in the Manipulator Equation. The Passive Forces (Inertial, Velo... |
| `ch05_affine_structure` | 1 | `fig:ch05_drift_vector_field` | TikZ Diagram | Qualitative drift vector field in a 2D slice of state space (shoulder angle $\theta_1$ and... |
| `ch06_zero_torque_counterfactual` | 1 | `fig:ch06_ztcf_timeline` | TikZ Diagram | Schematic Comparison of ZTCF and Actual Torque Trajectories During the Swing. The ZTCF Tor... |
| `ch07_constraint_forces` | 1 | `fig:constraint_forces_hinge` | TikZ Diagram | Constraint Forces at a Hinge Joint. The constraint force $\bm{F}_c$ acts at the joint, per... |
| `ch08_triple_pendulum` | 1 | `fig:triple_pendulum_diagram` | TikZ Diagram | Triple Pendulum Model: The Three-Link Kinetic Chain. Segment 1 (Upper Arm, Blue) Rotates a... |
| `ch09_parallel_mechanisms` | 1 | `fig:serial_vs_parallel` | TikZ Diagram | Serial vs. Parallel Mechanisms. A Serial Chain (Left) Has a Single Path From Base to End E... |
| `ch09b_passive_stabilization` | 1 | `fig:energy_landscape` | TikZ Diagram | Attractor-Fluctuation Energy Landscape. The Body Begins in a Stable Well at the Address Po... |
| `ch09b_passive_stabilization` | 2 | `fig:phase_transitions` | TikZ Diagram | Phase Transitions in Stiffness During the Golf Swing. The Body Begins at Address With High... |
| `ch10_energy_transfer` | 1 | `fig:energy-sankey` | TikZ Diagram | Energy Flow From Sources (Muscles, Gravity) Through Body Segments to the Club. Constraint ... |
| `ch11_flexible_shaft` | 1 | `fig:shaft_bending` | TikZ Diagram | Shaft Bending Modes: Fundamental Bending Creates Elastic Energy Storage. |
| `ch11_flexible_shaft` | 2 | `fig:ch11:ztcf_comparison` | TikZ Diagram | Qualitative Comparison of Rigid vs.\ Flexible Shaft ZTCF Trajectories. The Flexible Shaft ... |
| `ch12_fascia` | 1 | `fig:fascia_layers` | TikZ Diagram | Fascia Tissue Composition: Layers of Connective Tissue With Structural Proteins. |
| `ch13_interdisciplinary` | 1 | `fig:ch13_interdisciplinary_map` | TikZ Diagram | The Affine Control Framework Provides a Common Language for Multiple Scientific Discipline... |
| `ch14_complete_swing` | 1 | `fig:ch14_complete_model` | TikZ Diagram | Structure of the complete golf swing model. The drift field $f(\state)$ comprises gravity,... |
| `ch16_muscle_to_joint_torques` | 1 | `fig:muscle-jacobian` | TikZ Diagram | The Muscle Jacobian Maps Muscle Force Space to Joint Torque Space. Because Muscles Are Red... |
| `ch17_muscle_force_generation` | 1 | `fig:hill-muscle-model` | TikZ Diagram | Hill-Type Muscle Model. The Contractile Element (CE) Is Sarcomere Machinery That Produces ... |
| `ch18_inverse_dynamics_parallel` | 1 | `fig:inverse_dynamics_flow` | TikZ Diagram | Inverse Dynamics Workflow: From Measured Motion to Inferred Joint Torques via Differentiat... |
| `ch19_aerodynamic_drag` | 1 | `fig:drag_force` | TikZ Diagram | Aerodynamic Drag Force Opposing Motion: Magnitude Scales as Velocity Squared. |
| `ch20_soft_tissue_pliable` | 1 | `fig:soft_tissue_model` | TikZ Diagram | Two-Mass Model: Rigid Core (Bone) Coupled to Soft Shell (Tissue). |
| `ch21_spine_modeling` | 1 | `fig:spine_segment` | TikZ Diagram | Spinal Segment: Two Vertebrae Separated by Intervertebral Disc, Stabilized by Ligaments. |
| `ch22_anatomy_joint_modeling` | 1 | `fig:joint_primitives` | TikZ Diagram | Joint Primitives: Revolute (1R) One Axis, Universal (2R) Two Axes, Spherical (3R) Three Ax... |
| `ch23_dof_urdf_models` | 1 | `fig:urdf_tree` | TikZ Diagram | URDF Kinematic Tree: Rigid Bodies Connected by Joints Defining the Kinematic Chain. |
| `ch24_motor_control_brain` | 1 | `fig:ch24_hierarchy` | TikZ Diagram | Motor Control Hierarchy in the Brain. Top-Down Commands Flow From Prefrontal Cortex (Goal ... |
| `ch25_motor_learning` | 1 | `fig:ch25_learning_stages` | TikZ Diagram | Motor Learning Stages. Performance Variability (Error Rate, Inconsistency) Decreases Over ... |
| `ch28_impact_collision` | 1 | `fig:impact_collision` | TikZ Diagram | Club-Ball Impact Collision Showing Clubhead Velocity $v_c$ Before Impact, Normal Force $N$... |
| `ch29_joint_damping_friction` | 1 | `fig:damping_model` | TikZ Diagram | Linear Spring-Dashpot (Mass-Spring-Damper) Model of a Joint With Stiffness $k$, Damping Co... |
| `ch30_kinetic_chain` | 1 | `fig:ch30_kinetic_chain_timing` | TikZ Diagram | Kinetic Chain Sequencing: Proximal-to-Distal Timing of Segment Velocities. Each Segment's ... |
| `ch31_swing_plane_launch` | 1 | `fig:swing_plane_geometry` | TikZ Diagram | Swing Plane Geometry Showing the Tilted Plane Containing the Club Path at Impact, the Atta... |

## Strategic Recommendations for Quarto Figure Rendering

1. **TikZ to SVG Build-Time Pipeline**: Because all 31 figures are `tikzpicture` environments, an automated offline pipeline (e.g. `pdflatex` + `dvisvgm` or `standalone` LaTeX compiler) can render high-fidelity SVGs into `articles/The_Physics_of_Golf/quarto/figures/` without introducing runtime browser dependencies.
2. **Executable Matplotlib / OJS Option**: Select conceptual plots (e.g. `ch06` ZTCF comparison, `ch11` shaft bending, `ch29` mass-spring-damper) can optionally be upgraded to interactive executable cells in future enhancements.
3. **Cross-Reference Hygiene**: Update Quarto cross-references to use `@fig-<label>` matching LaTeX `fig:<label>` identifiers.
