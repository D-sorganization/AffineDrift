import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. Physics Parameters & Constants
# ==========================================
# Inertia Properties (kg * m^2)
I_alpha = 0.2500  # Inertia of Swing Plane (Whole club rotation)
I_beta = 0.0005  # Inertia of Shaft Axis (Twisting the head)

# Simulation Inputs
torque_noise = 5.0  # Magnitude of passive constraint torque (N*m)
dt = 0.05  # Duration of the release window (seconds)

# Grip Angles to simulate (0 = Fingers, 90 = Palm)
# We simulate a continuous range for the plot
angles_deg = np.linspace(0, 90, 100)
angles_rad = np.radians(angles_deg)

# ==========================================
# 2. The Simulation Loop (Continuous)
# ==========================================


def simulate_impact(angle_rad, total_torque):
    """
    Projects the total constraint torque onto the Shaft (Beta)
    and Swing Plane (Alpha) axes based on grip angle.
    Returns the resulting angular displacement in degrees.
    """
    # 1. Project Torque
    # Sin(angle) projects onto Shaft Axis (Palm grip maximizes this)
    tau_beta = total_torque * np.sin(angle_rad)
    # Cos(angle) projects onto Swing Plane (Finger grip maximizes this)
    tau_alpha = total_torque * np.cos(angle_rad)

    # 2. Calculate Angular Acceleration (a = tau / I)
    accel_beta = tau_beta / I_beta
    accel_alpha = tau_alpha / I_alpha

    # 3. Calculate Displacement over time dt (d = 0.5 * a * t^2)
    # Result in Radians
    disp_beta_rad = 0.5 * accel_beta * (dt**2)
    disp_alpha_rad = 0.5 * accel_alpha * (dt**2)

    return np.degrees(disp_beta_rad), np.degrees(disp_alpha_rad)


# Run simulation
face_errors = []
path_deviations = []

for ang in angles_rad:
    f_err, p_dev = simulate_impact(ang, torque_noise)
    face_errors.append(f_err)
    path_deviations.append(p_dev)

# ==========================================
# 3. Data Visualization
# ==========================================

plt.style.use("seaborn-v0_8-whitegrid")
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Face Angle Error (Red)
color = "tab:red"
ax1.set_xlabel("Grip Angle (Degrees)\n0° = Deep Fingers | 90° = Full Palm", fontsize=12)
ax1.set_ylabel("Face Angle Error (Degrees)", color=color, fontsize=12)
(line1,) = ax1.plot(
    angles_deg, face_errors, color=color, linewidth=3, label="Face Angle Error (Dispersion)"
)
ax1.tick_params(axis="y", labelcolor=color)
ax1.set_ylim(0, 16)

# Create a second y-axis for Path Deviation (Green)
ax2 = ax1.twinx()
color = "tab:blue"
ax2.set_ylabel("Swing Path Deviation (Degrees)", color=color, fontsize=12)
(line2,) = ax2.plot(
    angles_deg,
    path_deviations,
    color=color,
    linewidth=3,
    linestyle="--",
    label="Path Deviation (Speed/Line)",
)
ax2.tick_params(axis="y", labelcolor=color)
ax2.set_ylim(0, 16)  # Match scales for visual comparison

# Title and Annotations
plt.title(
    f"Grip Routing Sensitivity: Impact of {torque_noise}Nm Constraint Torque", fontsize=14, pad=20
)
plt.axvline(x=15, color="gray", linestyle=":", alpha=0.5)
plt.text(16, 14, "Standard Grip\nRange", color="gray")

# Combined Legend
lines = [line1, line2]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc="upper left", frameon=True)

# Save
plt.tight_layout()
plt.savefig("grip_sensitivity_analysis.png", dpi=300)
plt.show()

# ==========================================
# 4. Generate Data Table for LaTeX
# ==========================================
# Extract specific points for the table
key_points = [0, 15, 30, 45, 90]
print("--- LaTeX Table Data ---")
print("Angle | Tau_Shaft | Accel_Face | Error_Deg")
for k in key_points:
    rad = np.radians(k)
    tau_s = torque_noise * np.sin(rad)
    acc = tau_s / I_beta
    disp_deg, _ = simulate_impact(rad, torque_noise)
    print(f"{k:2d}    | {tau_s:6.2f}    | {acc:6.0f}     | {disp_deg:5.1f}")
