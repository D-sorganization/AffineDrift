# Inline Improvement Suggestions

## 1. Addressing "The Flaccid Drift Contradiction"

**Target File:** `articles/theory-part1.qmd`
**Section:** The Underactuated Equation of Motion

**Current Text:**
$$
\dots + G(q_{\text{sys}}) + \begin{bmatrix} 0 \\ K_s \eta + C_s \dot{\eta} \end{bmatrix} = \begin{bmatrix} \tau \\ 0 \end{bmatrix}.
$$

**Suggested Improvement:**
Replace the equation block with:
$$
\begin{bmatrix} M_{qq} & M_{q\eta} \\ M_{\eta q} & M_{\eta\eta} \end{bmatrix}
\begin{bmatrix} \ddot{q} \\ \ddot{\eta} \end{bmatrix}
+ C(q_{\text{sys}}, \dot{q}_{\text{sys}}) \dot{q}_{\text{sys}}
+ G(q_{\text{sys}})
+ \begin{bmatrix} \tau_{\text{pas}}(q, \dot{q}) \\ K_s \eta + C_s \dot{\eta} \end{bmatrix}
=
\begin{bmatrix} \tau_{\text{act}} \\ 0 \end{bmatrix}.
$$

**Add the following definition immediately after:**
> where $\tau_{\text{pas}}(q, \dot{q})$ represents the passive impedance (stiffness and damping) of the joints/muscles, treated here as part of the drift field $f(x)$. This ensures the Zero Torque Counterfactual ($u=0$) represents a "Frozen Strategy" rather than a flaccid collapse.

---

## 2. Addressing "Double Pendulum Energy Blindness"

**Target File:** `articles/drift-components-wrench-double-pendulum.qmd`
**Section:** 6. Energy Transfer Decomposition

**Current Text:**
This decomposition allows us to answer: **"Is the club gaining energy because I am pulling on it (passive/geometric transfer) or because I am twisting it (active transfer)?"**

**Suggested Improvement:**
Add this Callout block immediately after the bolded question:

::: {.callout-warning}
## Limitation: Rigid vs Flexible Energy Transfer
This rigid-body power analysis captures kinetic energy transfer but ignores **elastic potential energy**. In the full flexible shaft model (Part I), active torque often does work to deform the shaft (increasing $V_{\text{elastic}}$), effectively "banking" energy that is later released passively. The rigid model here illustrates the *mechanism* of transfer but underestimates the *capacity* for delayed release.
:::
