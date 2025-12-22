# Technical Review: Wrist as Universal Joint Model

## Date: 2025-11-25

## Executive Summary

This document reviews the current wrist-as-universal-joint model implementation and identifies critical issues with the torque transmission calculations. The current model makes simplifying assumptions that do not accurately reflect the behavior of real universal (Hooke/Cardan) joints.

## Current Model Review

### Files Analyzed

1. `Grip_Angle_Torque_Transmission.py` (907 lines) - PyQt6 GUI
2. `Wrist_Universal_Claude.tex` (556 lines) - Main LaTeX article
3. `Grip_Angle_Torque_Transmission_Streamlit.py` (318 lines) - Web version

### Current Assumptions

The existing implementation makes the following assumptions:

1. **Perfect Linear Transmission**

   - `τ_α = τ_input × sin(θ)`
   - `τ_γ = τ_input × cos(θ)`
   - This assumes torque transmission is purely a function of grip angle with no dynamic variation

2. **Static Grip Angle Only**

   - The angle `θ` represents grip angle (how the club sits in the hand)
   - No distinction between grip angle and wrist joint angle during motion
   - The wrist angle is assumed to be perfectly aligned with the grip angle

3. **Constant Transmission Ratio**

   - The model assumes torque transmission ratio is constant regardless of wrist position
   - No variation as the wrist moves through flexion/extension or ulnar/radial deviation

4. **Energy Conservation via Vector Decomposition**
   - `|τ_total|² = |τ_α|² + |τ_γ|²` (Pythagorean theorem)
   - This is correct for static vector decomposition but incomplete for dynamic universal joints

## Critical Issues Identified

### Issue 1: Missing Universal Joint Transmission Characteristics

**Problem**: Real universal joints (Hooke/Cardan joints) have **variable transmission ratios** that depend on the joint angle.

**Correct Universal Joint Kinematics**:

For a universal joint with bend angle `δ` (angle between input and output shaft centerlines):

**Angular Velocity Ratio**:

```
ω_out(φ) = ω_in × cos(δ) / (1 - sin²(δ) × sin²(φ))^0.5
```

Where `φ` is the instantaneous rotation angle of the input shaft.

This can also be written as:

```
ω_out(φ) = ω_in × cos(δ) / sqrt(1 - sin²(δ) × sin²(φ))
```

**Key Characteristics**:

- The output shaft speed **varies cyclically** even if input speed is constant
- Maximum speed: `ω_max = ω_in / cos(δ)` at φ = 0°, 180°
- Minimum speed: `ω_min = ω_in × cos(δ)` at φ = 90°, 270°
- Two cycles per revolution

**Torque Transmission** (from power conservation P = τω):

```
τ_out(φ) = τ_in × ω_in / ω_out(φ)
τ_out(φ) = τ_in × sqrt(1 - sin²(δ) × sin²(φ)) / cos(δ)
```

**Implications**:

- Torque transmission is **NOT constant**
- It varies with the wrist angle (φ) throughout the motion
- At certain angles, torque amplification occurs; at others, torque reduction

### Issue 2: Confusion Between Grip Angle and Wrist Angle

**Problem**: The current model uses a single angle `θ` without distinguishing:

1. **Grip Angle (θ_grip)**: How the club is oriented in the hand (static)

   - 0° = club aligned with fingers (finger grip)
   - 90° = club aligned with palm (palm grip)
   - This determines which club axes align with which wrist axes

2. **Wrist Flexion Angle (φ)**: The dynamic angle of wrist flexion/extension during motion

   - Changes throughout the swing
   - Affects the universal joint transmission ratio

3. **Wrist Deviation Angle (ψ)**: The dynamic angle of radial/ulnar deviation
   - Also changes during the swing
   - Creates additional universal joint effects

**Current Implementation**: Treats `θ` as if it's both grip angle AND wrist angle, which is incorrect.

**Correct Approach**: These should be separate parameters:

- **θ_grip**: Fixed based on how golfer grips club (user-selected)
- **φ(t)**: Dynamic wrist flexion angle (varies during swing)
- **ψ(t)**: Dynamic wrist deviation angle (varies during swing)

### Issue 3: Oversimplified Torque Decomposition

**Problem**: The current trigonometric decomposition:

```python
torque_alpha = input_torque * sin(theta)
torque_gamma = input_torque * cos(theta)
```

This is valid for **static force/torque decomposition** but doesn't account for:

1. **Dynamic transmission variations** due to changing wrist angles
2. **Coupled motion** between wrist axes in a universal joint
3. **Phase differences** between input and output rotation
4. **Non-linear inertial effects** when acceleration varies

### Issue 4: Missing Constraint Torque Dynamics

**Problem**: While the LaTeX article correctly discusses constraint torques, the Python implementation doesn't actually model them properly.

**What's Missing**:

1. The constraint torque about the forearm axis should vary with:

   - Applied torques on actuated axes (flexion/extension, radial/ulnar)
   - Angular velocities of all segments
   - Joint configuration (wrist angle)
   - System inertias

2. The constraint torque should be **calculated** from the dynamics, not just **decomposed** trigonometrically

**Correct Formulation** (from LaTeX article):

```
τ_constraint = J^T(q) × λ
```

Where:

- J = constraint Jacobian (function of joint angles)
- λ = Lagrange multipliers (solved from equations of motion)

## Proposed Corrections

### 1. Separate Grip Angle from Wrist Angle

**New Parameter Structure**:

```python
# Fixed grip parameter (user selects)
theta_grip = 45  # degrees, 0 = fingers, 90 = palm

# Dynamic wrist angles (vary during swing)
phi_wrist_flexion(t) = ...  # flexion/extension angle
psi_wrist_deviation(t) = ...  # radial/ulnar deviation angle

# Combined wrist angle for universal joint calculation
delta_total(t) = sqrt(phi²(t) + psi²(t))  # total bend angle
```

### 2. Implement Universal Joint Transmission Model

**For a given wrist angle φ and grip angle θ**:

```python
def universal_joint_transmission_ratio(phi, delta):
    """
    Calculate transmission ratio for universal joint.

    Parameters:
    phi: Instantaneous rotation angle (radians)
    delta: Bend angle between input/output shafts (radians)

    Returns:
    omega_ratio: ω_out / ω_in
    tau_ratio: τ_out / τ_in
    """
    # Angular velocity ratio
    omega_ratio = np.cos(delta) / np.sqrt(1 - np.sin(delta)**2 * np.sin(phi)**2)

    # Torque ratio (inverse of velocity ratio, from power conservation)
    tau_ratio = 1.0 / omega_ratio

    return omega_ratio, tau_ratio
```

### 3. Model Torque Distribution Based on Grip Angle

**Grip angle determines axis alignment**:

```python
def distribute_torque_by_grip_angle(torque_forearm, theta_grip, phi_wrist):
    """
    Distribute forearm torque to club axes based on grip angle
    and calculate transmission through wrist universal joint.

    Parameters:
    torque_forearm: Torque about forearm axis (input)
    theta_grip: Grip angle (how club sits in hand)
    phi_wrist: Wrist flexion angle (current joint angle)

    Returns:
    torque_shaft_axis: Torque transmitted to club shaft axis
    torque_face_axis: Torque transmitted to club face axis
    """
    # Calculate effective bend angle based on grip configuration
    delta_effective = calculate_effective_bend_angle(theta_grip, phi_wrist)

    # Get universal joint transmission ratio
    omega_ratio, tau_ratio = universal_joint_transmission_ratio(
        phi_wrist, delta_effective
    )

    # Torque transmitted through universal joint
    torque_transmitted = torque_forearm * tau_ratio

    # Distribute to club axes based on grip angle
    torque_shaft = torque_transmitted * np.sin(np.radians(theta_grip))
    torque_face = torque_transmitted * np.cos(np.radians(theta_grip))

    return torque_shaft, torque_face, tau_ratio
```

### 4. Add Wrist Angle Sweep Visualization

**New Plot Type**: For a selected grip angle, show how transmission varies with wrist angle:

```python
# User selects grip angle: theta_grip = 30°
# Plot torque transmission ratio vs. wrist flexion angle

phi_range = np.linspace(-45, 45, 100)  # -45° to +45° flexion
tau_ratios = []
alpha_accel_ratios = []

for phi in phi_range:
    omega_ratio, tau_ratio = universal_joint_transmission_ratio(
        np.radians(phi), np.radians(theta_grip)
    )
    tau_ratios.append(tau_ratio)
    # Acceleration ratio includes both transmission and inertia effects
    alpha_accel_ratios.append(tau_ratio / I_alpha)

plt.plot(phi_range, tau_ratios, label='Torque Transmission Ratio')
plt.plot(phi_range, alpha_accel_ratios, label='Acceleration Ratio')
plt.xlabel('Wrist Flexion Angle (degrees)')
plt.ylabel('Transmission Ratio')
```

## Refined Physical Model

### Complete Model Structure

```
Input: Forearm rotation torque τ_forearm(t)
       ↓
    [Wrist Universal Joint with angles φ(t), ψ(t)]
       ↓ (transmission ratio varies with wrist angle)
Transmitted: τ_transmitted(t) = τ_forearm(t) × R(φ,ψ)
       ↓
    [Distribution based on grip angle θ_grip]
       ↓
    τ_shaft = τ_transmitted × sin(θ_grip)
    τ_face = τ_transmitted × cos(θ_grip)
       ↓
    [Divide by moments of inertia]
       ↓
    α_shaft = τ_shaft / I_shaft
    α_face = τ_face / I_face
```

Where:

- **R(φ,ψ)** = Universal joint transmission ratio (varies with wrist angles)
- **θ_grip** = Static grip angle (how club is held)
- **I_shaft, I_face** = Moments of inertia about respective axes

## Recommended Implementation Plan

### Phase 1: Enhanced Model (Current Focus)

1. Add wrist angle as a separate dynamic parameter
2. Implement universal joint transmission calculations
3. Create visualization of transmission ratio vs. wrist angle
4. Maintain grip angle as a separate static parameter

### Phase 2: Full Dynamic Model (Future)

1. Model time-varying wrist angles φ(t), ψ(t) during swing
2. Calculate constraint torques from equations of motion
3. Include Coriolis and centrifugal terms
4. Validate against motion capture data

### Phase 3: Optimization Studies (Future)

1. Optimize grip angle for different swing objectives
2. Study trade-offs between speed and consistency
3. Investigate coupling between wrist motion and club motion
4. Develop training recommendations

## Mathematical Corrections for LaTeX Article

The LaTeX article should be updated to include:

1. **Explicit universal joint transmission equations**
2. **Distinction between grip angle and wrist angle**
3. **Cyclical variation in torque transmission**
4. **Phase relationships between input and output rotation**
5. **Implications for timing and coordination**

## Key Insights from Corrected Model

1. **Torque transmission is NOT constant** - it varies with wrist angle throughout the swing

2. **Grip angle determines which club axis receives varying transmission**

   - Finger grip (θ→0°): Variations go to face axis (high inertia)
   - Palm grip (θ→90°): Variations go to shaft axis (low inertia)

3. **Wrist angle variation creates cyclic torque modulation**

   - Can amplify or attenuate torque transmission
   - Creates timing challenges for coordination

4. **Universal joint characteristics explain observed phenomena**
   - Why perfect alignment between arm and club planes is difficult
   - Why grip style affects face angle control
   - Why wrist action timing is critical

## References

1. **Universal Joint Mechanics**:

   - Seherr-Thoss, H. C., Schmelz, F., & Aucktor, E. (2006). _Universal Joints and Driveshafts_. Springer.
   - Chapter 2: Kinematics and dynamics of Cardan joints

2. **Biomechanics of Wrist Joint**:

   - Crisco, J. J., et al. (2011). "In vivo radiocarpal kinematics and the dart thrower's motion." _Journal of Bone and Joint Surgery_.

3. **Constraint Force Analysis**:

   - Featherstone, R. (2014). _Rigid Body Dynamics Algorithms_. Springer.
   - Chapter 5: Constrained dynamics

4. **Golf Biomechanics**:
   - Nesbit, S. M., & Serrano, M. (2005). "Work and power analysis of the golf swing." _Journal of Sports Science & Medicine_, 4(4), 520.

## Conclusion

The current model provides valuable insights into grip angle effects but oversimplifies the dynamics of torque transmission through the wrist universal joint. By separating grip angle from wrist angle and properly modeling universal joint transmission characteristics, we can:

1. More accurately predict torque and acceleration transmission
2. Better understand the timing challenges of the golf swing
3. Provide more actionable insights for technique optimization
4. Create more realistic training simulations

The proposed enhancements maintain the intuitive appeal of the current model while adding the necessary physical accuracy to make quantitative predictions.

---

**Next Steps**:

1. Implement enhanced Python model with separate grip/wrist angles
2. Add universal joint transmission calculations
3. Create new visualization showing transmission vs. wrist angle
4. Update LaTeX documentation with corrected mathematics
5. Validate against known universal joint behavior
