import matplotlib.pyplot as plt
import numpy as np

# --- 1. Assumptions and Constants ---
# Mass properties of a standard driver
mass_head = 0.200  # kg
length_club = 1.15 # meters (approx 45 inches)
radius_gyration_head = 0.04 # meters (approximate distance of CG from shaft axis)

# Inertia Calculations
# I_alpha: Swinging the whole club (Model as point mass at end of rod)
I_alpha = mass_head * (length_club ** 2)

# I_beta: Rotating the shaft (Model as point mass rotating off-axis + shaft intrinsic)
# Note: Standard Head MOI is ~5000 g*cm^2 = 0.0005 kg*m^2.
# We will use a conservative range.
I_beta = 0.0005

# Constraint Torque Parameters
# We simulate "noise" torque occurring over a short impact window (downswing release)
torque_range = np.linspace(0, 10, 100) # 0 to 10 Nm of constraint torque
dt = 0.05 # 50ms release window

# --- 2. Physics Engine ---

def calculate_angular_displacement(torque, inertia, time):
    """
    d = 0.5 * alpha * t^2
    alpha = torque / inertia
    """
    alpha = torque / inertia
    displacement_radians = 0.5 * alpha * (time ** 2)
    return np.degrees(displacement_radians)

# Calculate Errors
error_finger_grip = calculate_angular_displacement(torque_range, I_alpha, dt) # Displaces swing path (Speed/Direction)
error_palm_grip = calculate_angular_displacement(torque_range, I_beta, dt)    # Displaces Face Angle (Spin/Slice)

# --- 3. Visualization ---

plt.figure(figsize=(10, 6))

# Plot Finger Grip (Alpha Axis)
plt.plot(torque_range, error_finger_grip, label=f'Finger Grip (Routing to Swing Plane)\nInertia: {I_alpha:.3f} kg·m²', color='green', linewidth=2)

# Plot Palm Grip (Beta Axis)
# Note: The error is so high we might need a log scale or a secondary axis,
# but for the article, showing the massive gap is the point.
plt.plot(torque_range, error_palm_grip, label=f'Palm Grip (Routing to Shaft Axis)\nInertia: {I_beta:.4f} kg·m²', color='red', linewidth=2)

# Formatting
plt.title('The "Grip Routing" Effect: Sensitivity to Constraint Torques', fontsize=14)
plt.xlabel('Passive Constraint Torque (N·m)', fontsize=12)
plt.ylabel('Angular Displacement over 50ms (Degrees)', fontsize=12)
plt.grid(True, which='both', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Annotation for the "Mic Drop" moment
plt.annotate(f'Face twists ~{error_palm_grip[50]:.1f}°\nwith 5Nm torque!',
             xy=(5, error_palm_grip[50]),
             xytext=(6, error_palm_grip[50]-5),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.annotate(f'Path varies only ~{error_finger_grip[50]:.2f}°',
             xy=(5, error_finger_grip[50]),
             xytext=(5, error_finger_grip[50]+10),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.tight_layout()
plt.show()

# --- 4. Print Data for Table ---
print(f"{'Metric':<25} | {'Finger Grip (Alpha)':<20} | {'Palm Grip (Beta)':<20}")
print("-" * 70)
print(f"{'Inertia (kg·m²)':<25} | {I_alpha:<20.4f} | {I_beta:<20.5f}")
print(f"{'Torque Applied':<25} | 5.0 N·m              | 5.0 N·m")
print(f"{'Resulting Displacement':<25} | {error_finger_grip[50]:.2f} degrees         | {error_palm_grip[50]:.2f} degrees")
