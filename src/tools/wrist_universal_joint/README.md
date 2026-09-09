# Cardan and Torque Projection Demonstration

Explore the phase-dependent speed and ideal delivered-torque ratios of a
supported Cardan shaft. A separate synthetic projection resolves the delivered
torque into two components and applies illustrative scalar inertia responses.
This does not calculate human wrist reactions, integrate a golf swing or rank
grip quality. The historical hand sketch is not the Cardan geometry.

## Model Boundaries

- The demo angle supplies both the shaft bend and the projection angle by
  choice. The input phase is not anatomical wrist flexion or deviation.
- Fixed supported shafts and negligible joint storage/losses condition the
  reciprocal torque ratio. A requested 90-degree bend is evaluated at 89 degrees.
- Time traces multiply an input signal by a fixed-phase gain; they do not
  integrate shaft phase or clubface motion.
- Alpha uses a point-head/thin-rod transverse grip inertia. Gamma is an
  illustrative half of alpha, not a measured shaft-axis inertia.
- Torque component amplitudes are not shares of energy. Acceleration gains
  have units (rad/s²)/(N·m); transmission ratios are dimensionless.

## Files

| File                      | Purpose                                                        |
| ------------------------- | -------------------------------------------------------------- |
| torque_calculator.py      | Cardan ratio, illustrative inertia and projection calculations |
| plots.py                  | Matplotlib traces and phase sweep                              |
| streamlit_app.py          | Optional Streamlit interface                                   |
| qt_window.py              | Qt interface used by the legacy enhanced-model launcher        |
| grip_angle_simulator.html | Browser interface with Plotly charts                           |
| requirements.txt          | Optional Python dependencies                                   |

## Run and Embed

See the [embedding guide](EMBEDDING_GUIDE.md) for the actual paths and runtime
requirements. The browser page uses an external Plotly script; it is not
dependency-free or guaranteed to work offline.

## Technical Context

Read [Constraint Torques at the Wrist](https://affinedrift.com/articles/wrist-universal-joint.html)
and the [companion derivation](../../../content/wrist-as-universal-joint/MATHEMATICAL_DERIVATION.md)
before interpreting the demo. Independent derivative and full-turn tests check
the ratio; they do not validate a human grip hypothesis.
