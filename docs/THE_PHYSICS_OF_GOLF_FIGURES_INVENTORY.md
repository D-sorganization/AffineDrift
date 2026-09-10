# Figures Inventory and Parity Audit: The Physics of Golf

This document provides the formal audit and inventory of all figures across the LaTeX book sources and their Quarto website mirrors, tracking figure types, labels, captions, and parity gaps.

## Summary Metrics

| Metric | Value |
|---|---|
| **Total Chapters Audited** | 34 |
| **Chapters with Figures** | 28 |
| **Total LaTeX Figures** | 37 |
| **TikZ Figures** | 15 |
| **Raster / Includegraphics Figures** | 22 |
| **LaTeX Figure Labels** | 37 |
| **LaTeX Prose Figure Refs** | 3 |
| **Total Quarto Figures** | 23 |
| **Quarto Figure Defs (Divs / Imgs / Cells)** | 23 |
| **Quarto Prose Figure Mentions** | 20 |
| **Missing Figures in Quarto** | **14** |

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
| `ch09_parallel_mechanisms` | Parallel Mechanisms\\and Loop Constraints | 1 | 0 | 1 | ✅ Parity |
| `ch09b_passive_stabilization` | Passive Stabilization in Parallel Loops | 0 | 0 | 0 | ✅ Parity |
| `ch10_energy_transfer` | Energy Transfer: How Power Flows\\Through the Kinetic Chain | 2 | 0 | 2 | ✅ Parity |
| `ch11_flexible_shaft` | The Flexible Shaft: Elastic Energy and the Catapult Effect | 2 | 0 | 2 | ✅ Parity |
| `ch12_fascia` | Fascia and Connective Tissue: Separating Myth From Mechanics | 1 | 1 | 0 | ❌ Missing 1 |
| `ch13_interdisciplinary` | Where Disciplines Collide:\\An Interdisciplinary Perspective | 2 | 0 | 2 | ✅ Parity |
| `ch14_complete_swing` | The Complete Golf Swing: Putting It All Together | 2 | 0 | 2 | ✅ Parity |
| `ch15_ground_reaction_forces` | Ground Reaction Forces: The Silent Foundation | 0 | 0 | 0 | ✅ Parity |
| `ch16_muscle_to_joint_torques` | From Muscle Forces to Joint Torques | 1 | 1 | 0 | ❌ Missing 1 |
| `ch17_muscle_force_generation` | Muscle Force Generation:\\The Biological Engine | 2 | 0 | 2 | ✅ Parity |
| `ch18_inverse_dynamics_parallel` | Inverse Dynamics and\\the Parallel Loop Problem | 1 | 0 | 1 | ✅ Parity |
| `ch19_aerodynamic_drag` | Aerodynamic Loads\\in Swing and Flight | 1 | 0 | 1 | ✅ Parity |
| `ch20_soft_tissue_pliable` | Soft Tissue and Pliable Systems:\\Beyond the Rigid Body | 2 | 0 | 2 | ✅ Parity |
| `ch21_spine_modeling` | Modeling the Spine: Motion, Load, and Evidence | 1 | 0 | 1 | ✅ Parity |
| `ch22_anatomy_joint_modeling` | Anatomy and Joint Modeling: Choosing the Right Idealization | 1 | 1 | 0 | ❌ Missing 1 |
| `ch23_dof_urdf_models` | Degrees of Freedom\\and Robot Models\\of the Human Body | 1 | 1 | 1 | ✅ Parity |
| `ch24_motor_control_brain` | Motor Control I: The Brain as Controller | 1 | 1 | 0 | ❌ Missing 1 |
| `ch25_motor_learning` | Motor Control II:\\Learning the Swing | 2 | 0 | 2 | ✅ Parity |
| `ch26_remarkable_brain` | Motor Control III:\\The Computational Brain | 2 | 0 | 2 | ✅ Parity |
| `ch27_passive_distributed_control` | Passive and Distributed Control: A Self-Organizing Swing Model | 0 | 0 | 0 | ✅ Parity |
| `ch28_impact_collision` | Impact: The Collision That Matters | 1 | 1 | 0 | ❌ Missing 1 |
| `ch29_joint_damping_friction` | Damping, Friction, and Energy Dissipation in the Kinematic Chain | 1 | 1 | 0 | ❌ Missing 1 |
| `ch30_kinetic_chain` | The Kinetic Chain: Motion, Work, and Control in the Golf Swing | 0 | 0 | 0 | ✅ Parity |
| `ch30b_induced_acceleration` | Induced Acceleration Analysis: Quantifying Who Moves What | 0 | 0 | 0 | ✅ Parity |
| `ch31_swing_plane_launch` | Swing Plane, Clubface Control and Launch Optimization | 2 | 0 | 2 | ✅ Parity |
| `ch32_putting` | The Physics of Putting | 0 | 0 | 0 | ✅ Parity |

## Complete Figures Inventory

| Chapter | Fig # | Label | Type | Caption Summary |
|---|---|---|---|---|
| `ch01_why_physics` | 1 | `fig:ch01_drift_control_schematic` | TikZ Diagram | Schematic of Drift and Control Forces in the Golf Swing. Drift Forces (Blue) Include Gravi... |
| `ch02_language_of_motion` | 1 | `fig:ch02_arm_diagram` | TikZ Diagram | Double Pendulum Model of the Arm in Generalized Coordinates. The Shoulder Angle $\theta_1$... |
| `ch03_double_pendulum` | 1 | `fig:ch03_double_pendulum` | TikZ Diagram | Double Pendulum Model of the Golf Swing. Link 1 (Upper Arm, Blue) Rotates About the Should... |
| `ch04_forces_and_torques` | 1 | `fig:ch04_force_decomposition` | TikZ Diagram | The Five Sources of Torque in the Manipulator Equation. The Passive Forces (Inertial, Velo... |
| `ch05_affine_structure` | 1 | `fig:ch05_drift_vector_field` | TikZ Diagram | Qualitative drift vector field in a 2D slice of state space (shoulder angle $\theta_1$ and... |
| `ch06_zero_torque_counterfactual` | 1 | `fig:ch06_ztcf_timeline` | TikZ Diagram | Schematic model comparison of a declared drift-equivalent generalized quantity (red) and a... |
| `ch07_constraint_forces` | 1 | `fig:constraint_forces_hinge` | TikZ Diagram | Constraint Forces at a Hinge Joint. The constraint force $\bm{F}_c$ acts at the joint, per... |
| `ch08_triple_pendulum` | 1 | `fig:triple_pendulum_diagram` | TikZ Diagram | Triple Pendulum Model: The Three-Link Kinetic Chain. Segment 1 (Upper Arm, Blue) Rotates a... |
| `ch09_parallel_mechanisms` | 1 | `fig:parallel_mechanical_graph` | Includegraphics | Actual Closed Paths and the Connecting Spine Path. Arms and Legs Represent Jointed Paths; ... |
| `ch10_energy_transfer` | 1 | `fig:energy-sankey` | Includegraphics | Both Sides of the Internal Boundary Must Balance. Hinge-Force Power Cancels Between Bodies... |
| `ch10_energy_transfer` | 2 | `fig:energy_passive_transfer` | Includegraphics | An Explicit Passive Mechanism Redistributes Energy in Both Directions. The Outer Rod Gains... |
| `ch11_flexible_shaft` | 1 | `fig:shaft_bending` | Includegraphics | A Tip-Normalized Static Cantilever Shape and Its Slope. This Is an Admissible Approximatio... |
| `ch11_flexible_shaft` | 2 | `fig:ch11:ztcf_comparison` | Includegraphics | Position and Velocity Under the Declared Prescribed Base. The Flexible Response Includes C... |
| `ch12_fascia` | 1 | `fig:fascia_layers` | TikZ Diagram | Fascia Tissue Composition: Layers of Connective Tissue With Structural Proteins. |
| `ch13_interdisciplinary` | 1 | `fig:ch13_interdisciplinary_map` | Includegraphics | Connected Models Link Commands, Motion, Impact and Outcome. Measurements Observe Selected ... |
| `ch13_interdisciplinary` | 2 | `fig:interdisciplinary_collision_energy` | Includegraphics | Restitution Does Not Equal Energy Transfer. The Free Two-Mass Teaching Model Uses a 0.200 ... |
| `ch14_complete_swing` | 1 | `fig:ch14_complete_model` | Includegraphics | Preparation, Coupled Evolution, Delivery, and Outcome. Measurements and Model Assumptions ... |
| `ch14_complete_swing` | 2 | `fig:complete_mode` | Includegraphics | Displacement, Velocity, and Elastic Power Peak at Different Times. This Free Harmonic Mode... |
| `ch16_muscle_to_joint_torques` | 1 | `fig:muscle-jacobian` | TikZ Diagram | The Muscle Jacobian Maps Muscle Force Space to Joint Torque Space. Because Muscles Are Red... |
| `ch17_muscle_force_generation` | 1 | `fig:muscle-force-curves` | Includegraphics | Declared Teaching Curves: Active and Passive Length Multipliers, and the Joined Velocity L... |
| `ch17_muscle_force_generation` | 2 | `fig:hill-muscle-model` | Includegraphics | Force and Energy Connections in the Teaching Model. Active and Passive Fiber Forces Add Be... |
| `ch18_inverse_dynamics_parallel` | 1 | `fig:inverse_dynamics_flow` | Includegraphics | From Measurements and Declared Mechanics to Identified Loads and Further Research Question... |
| `ch19_aerodynamic_drag` | 1 | `fig:drag_force` | Includegraphics | Illustrative Zero-Input Pendulum Motion and Energy With and Without Quadratic Drag. Each C... |
| `ch20_soft_tissue_pliable` | 1 | `fig:soft_tissue_model` | Includegraphics | Boundary Conditions and Damping Determine Tissue Response. Both Plots Use a Fixed or Presc... |
| `ch20_soft_tissue_pliable` | 2 | `fig:soft_tissue_pressure` | Includegraphics | Pressure Acts Normal to a Surface. A Hemispherical Cap Has an Axial Resultant Based on Its... |
| `ch21_spine_modeling` | 1 | `fig:spine_segment` | Includegraphics | From Motion to Tissue Response: Each Stage Requires Its Own Evidence. A Single Measured Sh... |
| `ch22_anatomy_joint_modeling` | 1 | `fig:joint_primitives` | TikZ Diagram | Joint Primitives: Revolute (1R) One Axis, Universal (2R) Two Axes, Spherical (3R) Three Ax... |
| `ch23_dof_urdf_models` | 1 | `fig:urdf_tree` | TikZ Diagram | Upper-Body Tree and Two-Hand Closure. Numbers Indicate Compound-Joint Freedoms; the Dashed... |
| `ch24_motor_control_brain` | 1 | `fig:ch24_hierarchy` | TikZ Diagram | Motor Control Hierarchy in the Brain. Top-Down Commands Flow From Prefrontal Cortex (Goal ... |
| `ch25_motor_learning` | 1 | `fig:ch25_coordination_covariance` | Includegraphics | Manufactured Covariance Ellipses for the Task $y=q_1+q_2$. Greater Joint Variation Can Coe... |
| `ch25_motor_learning` | 2 | `fig:ch25_learning_stages` | Includegraphics | Manufactured Trial Updates With $a=1$, $r=4$ and $m_0=0$. Gains of 0.25 and 1.5 Converge; ... |
| `ch26_remarkable_brain` | 1 | `fig:brain_correction_window` | Includegraphics | Remaining Time Changes the Same Command's Effect. The Declared Rotor Model Compares Instan... |
| `ch26_remarkable_brain` | 2 | `fig:brain_control_loop` | Includegraphics | Preparation, Mechanics, Estimation, Feedback and Learning Interact. Within-Trial Responses... |
| `ch28_impact_collision` | 1 | `fig:impact_collision` | TikZ Diagram | Isolated One-Dimensional Impact Before and After Contact. Momentum and Relative-Speed Rest... |
| `ch29_joint_damping_friction` | 1 | `fig:damping_model` | TikZ Diagram | Parallel Spring and Damper Acting on a Translating Mass. Both Elements Share the Same Disp... |
| `ch31_swing_plane_launch` | 1 | `fig:swing_plane_geometry` | Includegraphics | Fixed-Plane Geometry Links Path and Attack Angle. Curves Use the Declared Positive-Left Fr... |
| `ch31_swing_plane_launch` | 2 | `fig:swing_launch_optimum` | Includegraphics | A Manufactured Launch Surface Shows Coupling and Curvature. The Elliptical One-Yard Loss R... |

## Strategic Recommendations for Quarto Figure Rendering

1. **TikZ to SVG Build-Time Pipeline**: Because all 31 figures are `tikzpicture` environments, an automated offline pipeline (e.g. `pdflatex` + `dvisvgm` or `standalone` LaTeX compiler) can render high-fidelity SVGs into `articles/The_Physics_of_Golf/quarto/figures/` without introducing runtime browser dependencies.
2. **Executable Matplotlib / OJS Option**: Select conceptual plots (e.g. `ch06` ZTCF comparison, `ch11` shaft bending, `ch29` mass-spring-damper) can optionally be upgraded to interactive executable cells in future enhancements.
3. **Cross-Reference Hygiene**: Update Quarto cross-references to use `@fig-<label>` matching LaTeX `fig:<label>` identifiers.
