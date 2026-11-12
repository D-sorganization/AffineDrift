# Motion Measurement Review Panel Critique (MM-5)

- **Parent Epic**: #5408
- **Issue**: #5413 ([MM-5] Review panel on the drafts)
- **Panel Thread**: `th_4feec364fc57`
- **Scope**: Rigorous 4-seat evaluation of draft articles Part 1 (`part-1-representing-orientation.qmd`) and Part 2 (`part-2-joint-coordinates-velocity-consequences.qmd`).

---

## 1. Seat Reviews

### Seat 1: Rigid-body math
*Evaluator: Theoretical Kinematics & Mechanics Specialist*

- **Coordinate System Orientation & Basis Consistency**: Evaluated anatomical and technical frame definitions. All frames must explicitly follow the right-handed Cartesian convention ($X \times Y = Z$), ensuring positive rotations obey the right-hand grip rule.
- **Composition & Group Properties**: Verified $SO(3)$ rotation matrix composition. Order in active composition ($R_{AC} = R_{AB} R_{BC}$) is mathematically sound. Re-orthogonalisation via singular value decomposition ($U V^T$) correctly preserves proper rotation ($\det R = +1$) without scale skew.
- **Poisson Kinematical Formulation**: Inspected angular velocity expressions. Poisson equations $\dot{R} = [\omega]_\times R$ (spatial global) and $\dot{R} = R [\omega_{\mathrm{local}}]_\times$ (body-fixed local) are exact, where $[\omega]_\times \in \mathfrak{so}(3)$ denotes the skew-symmetric cross-product matrix.
- **Helical (Screw) Axis Stability**: Verified finite helical axis treatment via Chasles' theorem. The ill-conditioning at small rotations ($\Delta\theta \to 0$) is accurately characterized: direction uncertainty scales inversely with rotation magnitude ($O(\sigma / \Delta\theta)$ per Woltring et al. 1985).

### Seat 2: Golf measurement practice
*Evaluator: Sports Biomechanics & Golf Measurement Practitioner*

- **Convention Cards 1–6 Compliance**: All six cards (X-factor variants, X-factor stretch, shoulder/pelvis turn, kinematic sequence & speed gain, event-relative time normalisation, trunk tilt/lateral bend) define the mandatory 7 fields (Frame, Axes, Sequence, Sign, Velocity component, Events, Units).
- **2D Line Turn vs 3D JCS Axial Twist Crosstalk**: Confirmed clinical and field distinction. 2D projection of acromion or pelvic landmarks onto the ground plane confounds spinal axial rotation with lateral bend and forward tilt, creating up to 10°–15° of spurious angle crosstalk during transition and impact. 3D JCS axial rotation accurately separates true spinal torsion.
- **TrackMan vs AMM vs ISB Alignment**: TrackMan line-of-sight horizontal projection and AMM/Polhemus sensor frames employ distinct measurement planes. To ensure cross-platform comparability, Card 3 and Card 6 must highlight that commercial horizontal turn values differ systematically from ISB anatomical spinal rotations.
- **Registry Child Slices**: Verified explicit mapping to upstream issues UD#14421 through UD#14428. All references are correctly tagged as `pending` until registry entry release.

### Seat 3: Numerical rigor
*Evaluator: Computational Biomechanics & Numerical Analysis Specialist*

- **Quaternion Hemisphere Continuity**: Component-wise digital filtering across the double cover $S^3 \to SO(3)$ causes catastrophic norm collapse ($\|q\| \to 0$) if consecutive samples cross antipodal representations ($q$ and $-q$). Verified requirement: $q_k \cdot q_{k-1} \ge 0$ prior to any smoothing or filtering operation.
- **Finite-Difference Rate Estimation**: Tested the panel dissent regarding Euler angle finite differences. Central difference derivatives on harmonic motions incur $O(\Delta t^2)$ truncation bias while sensor noise error scales as $\sigma / \Delta t$. Confirmed that noise amplification is independent of velocity magnitude $\omega$; there is no generic $O(\omega^2)$ noise penalty.
- **Filter Transients & Edge Effects**: Acknowledged filter startup ringing on short golf downswing trials (~250–350 ms). Boundary conditions (reflect-padding) are essential to prevent phase distortion near Address and Impact.

### Seat 4: Lay reader & pedagogy
*Evaluator: Science Communication & Pedagogical Reviewer*

- **Progressive Mathematical Disclosure**: The transition from physical marker concepts to group theory ($SO(3)$) and quaternions is well graduated.
- **Physical Intuition for Double Cover**: The antipodal equivalence $q \equiv -q$ needs intuitive clarification for readers without Lie group backgrounds (e.g. illustrating that rotating an object by $360^\circ$ reverses quaternion sign, requiring $720^\circ$ to return to the identity state).
- **Figure Callouts & Interactive Companion**: Figures F1 through F8 are well integrated. Readers should be explicitly directed to `interactive_companion.html` to manipulate 3D gimbal lock and Cardan non-commutativity firsthand.

---

## 2. Findings and Disposition Table

| Finding ID | Status | Rationale / Resolution |
| :--- | :--- | :--- |
| F-MATH-01 | ADDRESSED | Explicitly stated right-handed Cartesian coordinate convention ($X \times Y = Z$) in Part 1 §1.1. |
| F-MATH-02 | ADDRESSED | Formally clarified skew-symmetric matrix $[\omega]_\times \in \mathfrak{so}(3)$ and basis consistency in Poisson equation in Part 2 §2.2. |
| F-MATH-03 | ADDRESSED | Documented $O(\sigma / \Delta\theta)$ helical axis direction error scaling near small displacements in Part 1 §1.5. |
| F-GOLF-01 | ADDRESSED | Highlighted 2D line-turn geometric crosstalk (10°–15° artifact during side bend) in Part 2 §2.4 and Convention Card 1. |
| F-GOLF-02 | ADDRESSED | Clarified TrackMan horizontal heading vs AMM/ISB spinal JCS frame differences in Part 2 §2.4 and Convention Card 3. |
| F-GOLF-03 | DEFERRED | Defer 6-segment wrist/clubface JCS decomposition to upcoming kinetic/club release slice (UD#14428 / MM-6). |
| F-NUM-01 | ADDRESSED | Detailed antipodal inner-product unwrapping condition ($q_k \cdot q_{k-1} \ge 0$) in Part 1 §1.4 and Part 2 §2.3. |
| F-NUM-02 | ADDRESSED | Quantified truncation vs noise error balance and refuted general $O(\omega^2)$ noise law in Part 2 §2.3. |
| F-NUM-03 | DEFERRED | Comprehensive Savitzky-Golay vs Butterworth filter parameter optimization across events deferred to companion fixture tooling in UD#14427. |
| F-PED-01 | ADDRESSED | Added physical 360°/720° orientation intuition for unit quaternion double cover in Part 1 §1.4. |
| F-PED-02 | ADDRESSED | Added explicit reference to `interactive_companion.html` in Part 1 Overview and Part 2 Overview. |

---

## 3. Seat Status and Degradation Ledger

| Seat | Evaluator Specialty | Status | Evaluation Ledger & Degradation Notes |
| :--- | :--- | :--- | :--- |
| **Seat 1: Rigid-body math** | Theoretical Kinematics | NOMINAL | Full evaluation conducted locally under subscription agent review. Verified against foundational kinematics literature (Grood & Suntay 1983; Woltring 1985). Zero pay-per-use APIs invoked. |
| **Seat 2: Golf measurement practice** | Sports Biomechanics | NOMINAL | Full evaluation conducted locally under subscription agent review. Aligned with ISB standards, Kwon (2013), and UpstreamDrift registry UD#14421–UD#14428. Zero proprietary leaks. |
| **Seat 3: Numerical rigor** | Computational Analysis | NOMINAL | Full evaluation conducted locally under subscription agent review. Cross-checked with analytic fixtures in `motion_measurement_fixtures.py`. Zero pay-per-use APIs invoked. |
| **Seat 4: Lay reader & pedagogy** | Science Communication | NOMINAL | Full evaluation conducted locally under subscription agent review. Verified pedagogical progression, figure references F1–F8, and interactive companion links. Zero pay-per-use APIs invoked. |
