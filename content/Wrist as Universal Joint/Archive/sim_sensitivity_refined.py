# sim_sensitivity_refined.py
"""
Refined simulation for sensitivity to grip location on wrist mechanics.
Augmented with improved structure, visualization, parameterization, and documentation.
"""
import csv

import matplotlib.pyplot as plt
import numpy as np

# Constants and parameters
WRIST_LENGTH = 0.18  # meters (typical wrist length)
GRIP_POSITIONS = np.linspace(0.02, WRIST_LENGTH - 0.02, 50)  # avoid endpoints
FORCE_MAGNITUDE = 50  # Newtons (example force applied)
FORCE_ANGLE_DEG = 90  # degrees (perpendicular to forearm)
MASS_HAND = 0.5  # kg (approximate mass of hand)
MASS_FOREARM = 1.2  # kg (approximate mass of forearm)

# Function to calculate torque at wrist due to force at grip location
def calculate_torque(grip_pos, force_magnitude, force_angle_deg):
    """
    Calculate torque at wrist for a given grip position and force.
    grip_pos: distance from wrist joint (meters)
    force_magnitude: magnitude of force applied (Newtons)
    force_angle_deg: angle of force relative to forearm (degrees)
    Returns: torque (Nm)
    """
    force_angle_rad = np.deg2rad(force_angle_deg)
    # Only perpendicular component contributes to torque
    torque = grip_pos * force_magnitude * np.sin(force_angle_rad)
    return torque

# Function to calculate sensitivity (derivative of torque w.r.t grip position)
def calculate_sensitivity(force_magnitude, force_angle_deg):
    """
    Sensitivity of torque to grip position (dT/dx).
    """
    force_angle_rad = np.deg2rad(force_angle_deg)
    sensitivity = force_magnitude * np.sin(force_angle_rad)
    return sensitivity

# Calculate torques and sensitivities for all grip positions
torques = [calculate_torque(x, FORCE_MAGNITUDE, FORCE_ANGLE_DEG) for x in GRIP_POSITIONS]
sensitivity = calculate_sensitivity(FORCE_MAGNITUDE, FORCE_ANGLE_DEG)

# Augmented: Calculate effect of hand and forearm mass (inertia)
def calculate_inertia_effect(grip_pos, mass_hand, mass_forearm):
    """
    Estimate inertia at the wrist due to hand and forearm mass.
    Returns: moment of inertia (kg*m^2)
    """
    # Simple model: I = m*r^2 for hand, plus forearm (assume center at midpoint)
    I_hand = mass_hand * grip_pos**2
    I_forearm = mass_forearm * (grip_pos/2)**2
    return I_hand + I_forearm

inertia_effects = [calculate_inertia_effect(x, MASS_HAND, MASS_FOREARM) for x in GRIP_POSITIONS]

# Visualization
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(GRIP_POSITIONS, torques, label='Torque at Wrist')
plt.xlabel('Grip Position from Wrist (m)')
plt.ylabel('Torque (Nm)')
plt.title('Torque vs. Grip Position')
plt.grid(True)
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(GRIP_POSITIONS, inertia_effects, label='Inertia Effect', color='orange')
plt.xlabel('Grip Position from Wrist (m)')
plt.ylabel('Moment of Inertia (kg*m^2)')
plt.title('Inertia Effect vs. Grip Position')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

# Augmented: Print summary statistics
print(f"Sensitivity of torque to grip position: {sensitivity:.2f} Nm/m")
print(f"Max torque: {max(torques):.2f} Nm at grip position {GRIP_POSITIONS[np.argmax(torques)]:.2f} m")
print(f"Max inertia effect: {max(inertia_effects):.4f} kg*m^2 at grip position {GRIP_POSITIONS[np.argmax(inertia_effects)]:.2f} m")

# Augmented: Allow parameter sweep for force angle
FORCE_ANGLES = np.linspace(60, 120, 5)  # degrees
plt.figure(figsize=(8, 5))
for angle in FORCE_ANGLES:
    torques_angle = [calculate_torque(x, FORCE_MAGNITUDE, angle) for x in GRIP_POSITIONS]
    plt.plot(GRIP_POSITIONS, torques_angle, label=f'Angle {angle:.0f}°')
plt.xlabel('Grip Position from Wrist (m)')
plt.ylabel('Torque (Nm)')
plt.title('Torque vs. Grip Position for Various Force Angles')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Augmented: Save results to CSV for further analysis


with open('sim_sensitivity_results.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Grip Position (m)', 'Torque (Nm)', 'Inertia Effect (kg*m^2)'])
    for x, t, i in zip(GRIP_POSITIONS, torques, inertia_effects, strict=True):
        writer.writerow([x, t, i])

print("Results saved to sim_sensitivity_results.csv")
