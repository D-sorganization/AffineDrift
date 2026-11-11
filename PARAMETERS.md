This document serves as the single source of truth for parameter definitions across _The Physics of Golf_ (Ch 1-31) and _The Geometry of Motion_ (Vol 0-1).

| Parameter                  | Symbol     | Unit | Definition                                                                                                              | Range/Example            | Context/Chapter |
| -------------------------- | ---------- | ---- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------ | --------------- |
| Mass                       | $m$ or $M$ | kg   | Mass of the clubhead or relevant body segment                                                                           | 0.2 - 0.35 kg (clubhead) | Ch 1-5, Vol 0   |
| Length                     | $L$        | m    | Length of the club shaft                                                                                                | 0.9 - 1.2 m              | Ch 2, Vol 1     |
| Center of Gravity          | $CoG$      | m    | Distance from clubhead center to CoG                                                                                    | 0.01 - 0.05 m            | Ch 4, Vol 1     |
| Coefficient of Restitution | $COR$      | -    | Ratio of relative velocity after impact to before impact                                                                | 0.78 - 0.83              | Ch 10-12        |
| Drag–Curve Ratio           | $DgCR$     | -    | Restitution-based ratio $(1 - COR)/(1 + COR)$ (see NOTATION.md). Not to be confused with the Drift–Control Ratio (DCR). | 0 - 1                    | Ch 10-12        |
| Force                      | $F$        | N    | Applied force                                                                                                           | 100 - 1000 N             | Ch 1-31         |
| Torque                     | $\tau$     | N·m  | Applied torque                                                                                                          | 10 - 150 N·m             | Ch 1-31         |

## UpstreamDrift Runtime Defaults (Pin `625a16e68`)

Values below come from UpstreamDrift `src/shared/python/core/physics_constants.py` and the modules named in [UpstreamDrift Physics Models](../articles/upstreamdrift-physics-models.html). They are **program defaults**, not automatic site replacements for derivations in the textbook.

| Quantity | Symbol (site) | UpstreamDrift value | Unit | Provenance string in code | Primary module |
| --- | --- | --- | --- | --- | --- |
| Gravity | $g$ | 9.80665 | m/s² | NIST CODATA 2018 | `physics_constants` |
| Ball mass | $m$ | 0.04593 | kg | USGA Rule 5-1 | `physics_constants` |
| Ball radius | $R$ | 0.021335 | m | USGA Rule 5-2 (derived) | `physics_constants` |
| Ball $I$ | $I$ | $(2/5)mR^2$ | kg·m² | Solid sphere | `physics_constants` |
| Sea-level air density | $\rho$ | 1.225 | kg/m³ | ISA | `physics_constants` / `atmosphere` |
| Dynamic viscosity | — | $1.789\times 10^{-5}$ | Pa·s | ISO 2533 | `physics_constants` |
| Driver COR | $e_n$ | 0.83 | — | USGA/R&A CT limit | `physics_constants` |
| Putter / green COR | — | 0.78 | — | Uncited contact default | `physics_constants` |
| Contact time | — | 0.0005 | s | High-speed video (typical) | `physics_constants` |
| Head MOI | $I_H$ | $4.5\times 10^{-4}$ | kg·m² | Typical driver specs | `physics_constants` |
| Face friction (impact) | $\mu$ | 0.4 | — | `ImpactParameters` default | `impact_model/types` |
| Spin decay rate | — | 0.05 | 1/s | Trackman Data (string) | `physics_constants` |
| Lift cap (Python registry) | — | 0.155 | — | TrackMan calibration | `flight_models` |
| Lift cap (Rust kernel) | — | 0.26 | — | Module constant | `aerodynamics.rs` |
| Hole radius | $R_h$ | 0.054 | m | USGA cup | `putting_dynamics/solver` |
| Centre capture speed | — | ~1.64 | m/s | Chord bound (code) | `putting_dynamics/solver` |
| Stimp release speed | $v_s$ | 1.83 | m/s | USGA convention | `putting_dynamics/friction` |
| Flat-track ramp speed | — | ~1.911 | m/s | Closed form $b=0$ | `putting_dynamics/stimpmeter` |
| Sliding friction (putt) | $\mu_k$ | 0.40 | — | Default | `putting_dynamics/friction` |
| Static hold (putt) | $\mu_s$ | 0.08 | — | Default | `putting_dynamics/friction` |
| Roll stop threshold | — | 0.005 | m/s | Numerical | `putting_dynamics/friction` |

## Usage

- **Consistency**: All numerical examples and derivations must align with these symbols and ranges.
- **Reference**: Cross-reference this table when introducing new parameters in articles or textbook chapters.
