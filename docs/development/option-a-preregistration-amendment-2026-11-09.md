# Option A Preregistration Amendment — 2026-11-09

Parent: #5550; Slice 1: #5551; approval: Dieter t1565u; panel: th_58d367193440.
This dated amendment freezes the following definitions before IC-family generation
or A-4 analysis, supplementing the #5207 correction-authority analysis contract.

1. **Task Coordinate:** $p_k = \operatorname{FK}_{\mathrm{tip}}(q_k)$ is the
   distal-tip position in metres, computed by forward kinematics from the joint
   configuration $q_k$ contained in fixture state $x_k$.
2. **Drift Term:** $d_k = x_{k+1} - (A_k x_k + B_k u_k)$, where $x_{k+1}$ is the
   measured next fixture state. This is the measured one-step state residual,
   not an independently identified model-form error; it retains state-space units.
3. **Lead Time:** $t_{\mathrm{failure}} - t_{\mathrm{flag}}$, in seconds on the
   same fixture clock: positive when the flag precedes failure, zero at coincidence,
   negative when it follows. An absent event leaves lead time unavailable.
4. **Scientific Scope:** The vendored `src/affine_control/option_a_trace.py` trace
   is rad-space (`STATE_DIM=4`, `recovery_threshold_rad`), not metre-space.
   The affine recoverability bound is a rad-space result under its declared model
   assumptions; this amendment supplies no new proof. The metre-space task
   pass/fail label is a separate, unguaranteed readout. Nonlinear forward kinematics
   does not transfer that bound to metres; no metre-space guarantee is claimed.

Claims are simulation-only and limited to one fixture, one task, and one
perturbation direction; no generalizable correction-authority claim is authorized.
Assessment Board sign-off remains required before any public claim.
This amendment authorizes no analysis or validator implementation; subsequent
slices retain their prior-merge gates. All fleet holds remain in force.
