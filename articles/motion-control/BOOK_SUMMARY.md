# Control Is Motion — Complete Textbook

> **Status: archival LaTeX source (not rendered to the website).**
> This directory holds the standalone LaTeX/PDF manuscript of _Control Is Motion_.
> On the AffineDrift HTML site this material is superseded by **Volume II ("Control
> Is Motion") of _The Geometry of Motion_** (see
> `../The_Geometry_of_Motion/quarto/volume2_content.qmd`), which is the maintained,
> rendered edition. There are no `.qmd` files here, so nothing in this directory is
> picked up by the site render glob (`articles/**/*.qmd`) or linked from navigation.
> Keep editorial changes in the Geometry of Motion Volume II source; this manuscript
> is retained for provenance and the compiled `Control_Is_Motion_Complete.pdf`.

## Book Overview

**Title:** Control Is Motion  
**Subtitle:** Geometry, Feasible Dynamics, and Robust Outcomes

The manuscript develops trajectory-based nonlinear control for systems whose
objectives are defined along motions and at events (contacts, guards), not only
at equilibria. The golf swing is a recurring motivating example; claims are
scoped to stated models, contact laws, and feedback assumptions.

## Key Themes

- **Motion, targets, and timing:** Useful outcomes depend on how a feasible
  trajectory is generated and timed, not on tracking a single static setpoint.
- **Geometry of paths:** Arc length, curvature, and manifold structure separate
  path shape from timing where the model allows.
- **Orbital and transverse stability:** Stability of a motion can be studied on a
  moving orbit; this complements classical Lyapunov analysis rather than
  replacing it.
- **Underactuation and passive dynamics:** Passive coupling and zero dynamics are
  modeled explicitly; they are analysis tools, not automatic design advantages.
- **Scoped certificates:** Funnels, tubes, and optimization statements carry
  explicit assumptions; the golf case study is a protocol, not a finished
  musculoskeletal identification or certificate.

## Chapter Summary

### Chapter 1: Motion, Targets, and Timing

- Defines moving-target systems and the "control is motion" organizing perspective
- Contrasts trajectory objectives with setpoint control without discarding classical tools
- Introduces golf delivery, timing, and impact outputs as the primary example

### Chapter 2: Curves in State Space

- Trajectories as geometric curves; path–timing separation where valid
- Curvature, torsion, and Frenet–Serret descriptions
- Limits on arc-length derivatives and speed-dependent corrections

### Chapter 3: Configuration Manifolds

- Configuration manifolds, Lie groups, and SO(3) attitude kinematics
- Metrics from kinetic energy; constraints as submanifolds
- Frame consistency for velocity errors and feedforward transport

### Chapter 4: Orbital Stability and Transverse Linearization

- Orbital versus time-stamped tracking stability
- Transverse linearization and moving Poincaré sections (sufficient conditions)
- Floquet tools; cautions on timing shifts and invented amplification profiles

### Chapter 5: Underactuation and Passive Dynamics

- Underactuated structure, zero dynamics, and sequential energy transfer
- Golf-relevant whip and release mechanisms with explicit modeling limits
- Chow–Rashevskii and small-time local controllability caveats

### Chapter 6: Trajectory Optimization

- Moving-target optimal control and direct transcription ideas
- Multi-phase costs and implementable trajectory extraction

### Chapter 7: Funnel Synthesis

- Tubes, barrier conditions, and event-based impact certificates
- Explicit limits on optimality claims and disturbance/saturation interaction

### Chapter 8: Phase-Variable Control

- Virtual constraints, hybrid zero dynamics, and phase oscillators
- Applications to rhythmic motion and timing coordination

### Chapter 9: Stochastic Trajectories and Motor Variability

- Signal-dependent noise and minimum-variance ideas in trajectory design
- Covariance and robustness considerations for moving systems

### Chapter 10: Learning to Move

- Iterative learning and policy adaptation while preserving stability margins
- Skill development framed as trajectory improvement, not guaranteed optimality

### Chapter 11: Case Study: The Complete Golf Swing

- End-to-end modeling and verification protocol for address through follow-through
- **Does not** report a solved musculoskeletal optimization, an experimentally
  identified golfer, or a computed nonlinear golf-swing certificate (see chapter
  text for disclaimers)

## Build Notes

- Canonical concatenated source: `Control_Is_Motion_Complete.tex` (tracked).
- Optional chapter concatenation: `python3 compile_book.py` from this directory
  (repo-relative paths; does not overwrite this summary).
- PDF builds: `latexmk` on `Control_Is_Motion_Complete.tex` when a local TeX stack
  is available.

## Target Audience

Graduate students and researchers in robotics, control, and biomechanics who need
geometric language for trajectories, contacts, and underactuated motion—with claims
stated at the level of explicit models.
