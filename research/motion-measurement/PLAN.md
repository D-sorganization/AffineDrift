# MM-1: Motion Measurement Article Plan

Slice 1 of epic #5408 (issue #5409). This is a plan, not an article. It adds no
`articles/` or `books/` content and publishes nothing. Slices 2 to 7 follow the
ranking in the epic.

## Scope and Posture

- Audience: a technically literate reader who has not met the rotation reference.
- Reuse, do not duplicate: [`articles/rotation-representations-reference.qmd`](../../articles/rotation-representations-reference.qmd)
  already covers matrices, Euler angles, gimbal lock, axis-angle, exponential
  coordinates, quaternions, the double cover and the golf bridge. The new
  article links to its sections and only adds what it lacks (see "Gap
  Analysis").
- The finished article stays `draft: true` until the owner signs off (slice 7).
- Examples are synthetic or analytic. No unreleased UpstreamDrift capture data
  appears in any figure, table or fixture.
- No metric is presented as predicting performance, and no representation or
  convention is presented as universally correct.

## Gap Analysis Against the Existing Reference

| Topic                                          | Existing reference | New article adds            |
| ---------------------------------------------- | ------------------ | --------------------------- |
| Rotation matrix, Euler, axis-angle, quaternion | Covered            | Link only                   |
| Gimbal lock, double cover                      | Covered            | Link only                   |
| Measured frames from markers or IMUs           | Not covered        | Part 1 section 1.1          |
| Cardan sequences vs. joint coordinate systems  | Partly             | Part 2 section 2.1          |
| Screw axis and Chasles' theorem                | Not covered        | Part 1 section 1.5          |
| Angular velocity from sampled orientation      | Short              | Part 2 section 2.2          |
| Noise, filtering, sign continuity              | Short              | Part 2 section 2.3          |
| X-factor and kinematic sequence consequences   | Bridge only        | Part 2 sections 2.4 and 2.5 |

## Convention Card (Required for Every Metric)

Every metric discussed carries one line stating: frame, axes, rotation
sequence, sign convention, velocity component (global, segment-local or
about an instantaneous axis), event definitions, units. Convention confusion
is the central risk named by the panel; the card is the mitigation and is
checked in review (slice 5).

## Part 1: Representing Orientation

| Section                        | Learning goals                                                                                                            | Reuse                           | Figure |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ------ |
| 1.1 Frames and measurement     | Say what a segment frame is, how markers or sensors define one, and why two labs can measure "the same" angle differently | New                             | F1     |
| 1.2 Cardan and Euler sequences | Read and write a sequence; predict that different sequences give different numbers for the same motion                    | Link: Euler angles              | F2     |
| 1.3 Matrices and composition   | Compose and invert rotations; know order matters                                                                          | Link: rotation matrices         | none   |
| 1.4 Axis-angle and quaternions | Convert between forms; explain `q` and `-q`                                                                               | Link: quaternions, double cover | F3     |
| 1.5 Screw axis                 | State Chasles' theorem; know why the helical axis is ill-conditioned for small rotations                                  | New                             | F4     |

## Part 2: Joint Coordinates, Velocity and Consequences

| Section                      | Learning goals                                                                                                                    | Figure |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 2.1 Joint coordinate systems | Explain the Grood-Suntay construction and the ISB recommendation; see that a JCS is a particular Cardan sequence                  | F5     |
| 2.2 Angular velocity         | Distinguish global and local angular velocity; compute it from sampled orientations without differentiating Euler angles          | F6     |
| 2.3 Noise and filtering      | Show how sign flips and non-uniform smoothing corrupt velocity; state precisely what is and is not known (see "Claims to Settle") | F7     |
| 2.4 X-factor                 | Compare line-turn, plane-projection and Cardan variants and why published values differ                                           | F8     |
| 2.5 Kinematic sequence       | Define peak timing and speed gain, and say which angular velocity component is used                                               | F8     |

Figure plan (all static, produced from tested analytic fixtures in slice 2):
F1 segment frames, F2 sequence dependence, F3 quaternion sign and path,
F4 helical axis vs. rotation size, F5 JCS axes, F6 global vs. local angular
velocity, F7 filter ringing and sign unwrapping, F8 X-factor variant spread
on one synthetic motion. A small interactive companion (F1/F2) is slice 3.

## Registry Mapping (UpstreamDrift Metric Definitions, UD#14421)

The articles may only describe a metric as "defined in UpstreamDrift" when the
registry entry exists. UD#14421 is open and gated; until children land, the
status is `pending`. Child ids are from the epic body.

| Metric discussed                                                           | Where in this plan | Registry slice   | Status  |
| -------------------------------------------------------------------------- | ------------------ | ---------------- | ------- |
| X-factor variants (line turn, JCS axial, position proxy, legacy Euler yaw) | 2.4                | UD#14423 (GM-1b) | pending |
| X-factor stretch (Cheetham 2001 angle difference vs. UD whole-trial rate)  | 2.4                | UD#14426 (GM-3)  | pending |
| Shoulder and pelvis turn conventions                                       | 2.4                | UD#14424 (GM-1c) | pending |
| Kinematic sequence, speed gain (ratio vs. difference)                      | 2.5                | UD#14426 (GM-3)  | pending |
| Event-relative time normalisation                                          | 2.5                | UD#14427 (GM-4)  | pending |
| Trunk tilt and lateral bend at events                                      | 2.4                | UD#14428 (GM-5)  | pending |
| Registry schema, versioning, citations field                               | all                | UD#14422 (GM-1a) | pending |

Ground-reaction force, centre of pressure and free-moment metrics are out of
scope for this article (kinetics, not orientation measurement).

## Claims to Settle (Unverified, Do Not State as Fact)

| Claim                                                              | Source                                    | Resolution plan                                                                                                                             |
| ------------------------------------------------------------------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Euler-angle finite differences amplify noise as O(omega^2)         | Panel dissent (Argon)                     | Editor disputes a general law. Slice 2 measures error vs. noise, sample rate and scheme on analytic motions; state only what the test shows |
| Component-wise quaternion filtering spikes                         | Panel dissent                             | Test both: with sign-continuity unwrapping and without; report the difference                                                               |
| Helical-axis error is inversely proportional to rotation magnitude | Woltring et al. 1985 (abstract, verified) | Cite directly; demonstrate in F4                                                                                                            |
| Cardan-method X-factor differs significantly from plane methods    | Kwon 2013 (abstract, verified)            | Cite; reproduce the qualitative spread in F8 on synthetic motion only                                                                       |
| IMU drift and sensor fusion behaviour                              | No source chosen                          | Either choose and verify a primary source in slice 4 or drop the topic                                                                      |

## Citation Rules

All references are in [`REFERENCES.md`](REFERENCES.md) with a verification
status and the date checked. Rules: a reference is `verified` only after a
primary listing (publisher or PubMed) was seen; panel citations that failed
verification are corrected or dropped there, not silently reused.

## Slice Plan

1. This plan, references and registry mapping (this PR).
2. Analytic fixtures and calculations, tests first.
3. Figures F1 to F8 and the interactive companion.
4. Draft Part 1 and Part 2 (`draft: true`).
5. Review panel: math, measurement, readability.
6. Quarto render with zero warnings and resolving citations.
7. Owner sign-off and publication (gated; `do-not-merge` until then).

Each slice is one PR under 500 lines on `main`, no stacking.
