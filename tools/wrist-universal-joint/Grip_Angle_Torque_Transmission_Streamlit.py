"""
Streamlit Web App: Grip Angle Torque Transmission & Acceleration Analysis
-----------------------------------------------------------------------
This is a web-based version of the PyQt6 GUI that can be embedded in GitHub Pages.
Host this on Streamlit Cloud (free) and embed via iframe in your HTML pages.
"""
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.patches import Ellipse, Rectangle

# Page config
st.set_page_config(
    page_title="Grip Angle Torque Transmission",
    page_icon="🏌️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
NOISE_TYPES = ['Golf-like Random', 'Burst', 'Step', 'Sinusoidal']
DEFAULT_CLUBHEAD_WEIGHT = 200.0  # grams
DEFAULT_SHAFT_WEIGHT = 100.0  # grams
DEFAULT_CLUB_LENGTH = 1.0  # meters
DEFAULT_CLUBHEAD_CG_DISTANCE = 0.85  # meters

def calculate_moments_of_inertia(clubhead_weight_g, shaft_weight_g, club_length_m, cg_distance_m):
    """Calculate moments of inertia for golf club about two axes."""
    m_head = clubhead_weight_g / 1000.0  # kg
    m_shaft = shaft_weight_g / 1000.0  # kg

    I_shaft_alpha = (1/3) * m_shaft * club_length_m**2
    I_head_alpha = m_head * cg_distance_m**2
    I_alpha = I_shaft_alpha + I_head_alpha
    I_gamma = 2.0 * I_alpha

    return I_alpha, I_gamma

def calculate_acceleration(torque, moment_of_inertia):
    """Calculate angular acceleration from torque: α = τ / I"""
    if moment_of_inertia < 1e-6:
        return np.zeros_like(torque)
    return torque / moment_of_inertia

def generate_noise(noise_type, length=500):
    """Generate noise signal based on type."""
    t = np.linspace(0, 1, length)
    if noise_type == 'Golf-like Random':
        noise = np.random.normal(0, 1, len(t))
        noise += np.exp(-50*(t-0.5)**2)*8*np.random.randn(len(t))
        noise = np.convolve(noise, np.ones(10)/10, mode='same')
    elif noise_type == 'Burst':
        noise = np.zeros_like(t)
        noise[200:300] = np.random.normal(0, 2, 100)
    elif noise_type == 'Step':
        noise = np.zeros_like(t)
        noise[250:] = 3
    elif noise_type == 'Sinusoidal':
        noise = np.sin(8 * np.pi * t)
    else:
        noise = np.random.normal(0, 1, len(t))
    return t, noise

def create_plots(grip_angle_deg, noise_type, show_input, show_alpha, show_gamma,
                 I_alpha, I_gamma, show_torque, show_acceleration, t, noise):
    """Create torque and acceleration plots."""
    theta_rad = np.deg2rad(grip_angle_deg)

    # Calculate torques
    torque_alpha = noise * np.sin(theta_rad)
    torque_gamma = noise * np.cos(theta_rad)

    # Calculate accelerations
    accel_alpha = calculate_acceleration(torque_alpha, I_alpha)
    accel_gamma = calculate_acceleration(torque_gamma, I_gamma)

    # Create figure with subplots
    if show_torque and show_acceleration:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    elif show_torque:
        fig, ax1 = plt.subplots(1, 1, figsize=(10, 5))
        ax2 = None
    elif show_acceleration:
        fig, ax2 = plt.subplots(1, 1, figsize=(10, 5))
        ax1 = None
    else:
        return None

    # Torque plot
    if show_torque and ax1 is not None:
        if show_input:
            ax1.plot(t, noise, label='Input Torque', color='gray', alpha=0.7, linewidth=1.5)
        if show_alpha:
            ax1.plot(t, torque_alpha, label='Torque α (sin θ)', color='red', linewidth=2)
        if show_gamma:
            ax1.plot(t, torque_gamma, label='Torque γ (cos θ)', color='blue', linewidth=2)
        ax1.set_title(f'Transmitted Torque (Grip Angle {grip_angle_deg:.0f}°)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Torque (N·m)', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left', fontsize=9)

        # Add schematic
        try:
            inset_ax = ax1.inset_axes([0.65, 0.65, 0.32, 0.32])
            shaft_y = 0.15
            inset_ax.plot([0, 1], [shaft_y, shaft_y], 'k-', lw=6)

            # Clubhead
            clubhead = Rectangle((0.0, shaft_y + 0.05), 0.1, 0.12,
                               facecolor='silver', alpha=0.8, edgecolor='gray', linewidth=1.5)
            inset_ax.add_patch(clubhead)

            # Hand
            hand_center = (0.75, shaft_y)
            hand = Ellipse(hand_center, 0.25, 0.12, angle=grip_angle_deg,
                          facecolor='tan', alpha=0.7, edgecolor='saddlebrown', linewidth=1.5)
            inset_ax.add_patch(hand)

            # Fingers
            finger_dir_x = -np.cos(theta_rad)
            finger_dir_y = -np.sin(theta_rad)
            perp_to_hand_x = -np.sin(theta_rad)
            perp_to_hand_y = np.cos(theta_rad)
            finger_spacing = 0.04
            finger_positions = [-1.5, -0.5, 0.5, 1.5]

            for pos in finger_positions:
                base_x = hand_center[0] + pos * finger_spacing * perp_to_hand_x
                base_y = hand_center[1] + pos * finger_spacing * perp_to_hand_y
                tip_x = base_x + 0.15 * finger_dir_x
                tip_y = base_y + 0.15 * finger_dir_y
                finger_mid_x = (base_x + tip_x) / 2
                finger_mid_y = (base_y + tip_y) / 2
                finger_angle = np.rad2deg(np.arctan2(finger_dir_y, finger_dir_x))
                finger = Ellipse((finger_mid_x, finger_mid_y), 0.15, 0.02,
                               angle=finger_angle, facecolor='tan', alpha=0.8,
                               edgecolor='saddlebrown', linewidth=0.5)
                inset_ax.add_patch(finger)

            # Angle arc
            arc_radius = 0.18
            arc_theta = np.linspace(0, theta_rad, 30)
            arc_center_x = hand_center[0] - 0.1
            arc_center_y = shaft_y
            arc_x = arc_center_x + arc_radius * np.cos(arc_theta)
            arc_y = arc_center_y + arc_radius * np.sin(arc_theta)
            inset_ax.plot(arc_x, arc_y, 'g-', lw=2)
            inset_ax.arrow(arc_center_x, arc_center_y, 0.18, 0,
                          head_width=0.02, head_length=0.03, fc='k', ec='k')
            inset_ax.arrow(arc_center_x, arc_center_y, 0.18*np.cos(theta_rad), 0.18*np.sin(theta_rad),
                          head_width=0.02, head_length=0.03, fc='r', ec='r')
            label_x = arc_center_x + arc_radius * np.cos(theta_rad/2)
            label_y = arc_center_y + arc_radius * np.sin(theta_rad/2)
            inset_ax.text(label_x, label_y+0.03, r"$\theta$", color='g', fontsize=14, ha='center')
            inset_ax.set_xlim(0, 1)
            inset_ax.set_ylim(-0.1, 0.4)
            inset_ax.axis('off')
            inset_ax.set_title(r"Schematic: $\theta$", fontsize=10)
        except Exception:
            pass

    # Acceleration plot
    if show_acceleration and ax2 is not None:
        if show_alpha:
            ax2.plot(t, accel_alpha, label='Accel α (rad/s²)', color='red', linewidth=2, linestyle='--')
        if show_gamma:
            ax2.plot(t, accel_gamma, label='Accel γ (rad/s²)', color='blue', linewidth=2, linestyle='--')
        ax2.set_title(f'Angular Acceleration (Iα={I_alpha:.4f} kg·m², Iγ={I_gamma:.4f} kg·m²)',
                     fontsize=12, fontweight='bold')
        ax2.set_xlabel('Time (s)', fontsize=10)
        ax2.set_ylabel('Acceleration (rad/s²)', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper left', fontsize=9)

    plt.tight_layout()
    return fig

# Page config with custom styling
st.markdown("""
<style>
    .main {
        padding: 2rem 1rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3282b8 0%, #0f4c75 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    h1 {
        background: linear-gradient(135deg, #0f4c75 0%, #3282b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""", unsafe_allow_html=True)

# Main app
st.title("🏌️ Grip Angle Torque Transmission & Acceleration Analysis")
st.markdown("""
<div style='background: #f0f4f8; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #3282b8;'>
    <p style='margin: 0; font-size: 1.1em;'>
    This interactive tool visualizes how grip angle modulates transmission of forearm axis torque noise
    to the club's shaft axis (local alpha) and high inertia axis (local gamma), and calculates the
    resulting angular acceleration based on club inertial properties.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.header("Club Properties")
    clubhead_weight = st.number_input("Clubhead Weight (g)", 50.0, 500.0, DEFAULT_CLUBHEAD_WEIGHT, 1.0)
    shaft_weight = st.number_input("Shaft Weight (g)", 30.0, 200.0, DEFAULT_SHAFT_WEIGHT, 1.0)
    club_length = st.number_input("Club Length (m)", 0.5, 1.5, DEFAULT_CLUB_LENGTH, 0.01)
    cg_distance = st.number_input("CG Distance (m)", 0.3, 1.2, DEFAULT_CLUBHEAD_CG_DISTANCE, 0.01)

    I_alpha, I_gamma = calculate_moments_of_inertia(clubhead_weight, shaft_weight, club_length, cg_distance)
    st.markdown(f"""
    <div class='metric-card'>
        <h3 style='margin: 0 0 0.5rem 0; color: white;'>Moments of Inertia</h3>
        <p style='margin: 0; font-size: 1.2em;'><strong>Iα = {I_alpha:.4f} kg·m²</strong></p>
        <p style='margin: 0; font-size: 1.2em;'><strong>Iγ = {I_gamma:.4f} kg·m²</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.header("Grip Angle")
    grip_angle = st.slider("Grip Angle (degrees)", 0, 90, 45, 1)
    st.markdown("**0°** = Shaft axis  |  **90°** = High inertia axis")

    st.header("Noise Input")
    noise_type = st.selectbox("Noise Type", NOISE_TYPES)

    st.header("Display Options")
    show_torque = st.checkbox("Show Torque Plots", True)
    show_acceleration = st.checkbox("Show Acceleration Plots", True)
    show_input = st.checkbox("Show Input Torque", True)
    show_alpha = st.checkbox("Show Alpha Components", True)
    show_gamma = st.checkbox("Show Gamma Components", True)

# Generate noise
t, noise = generate_noise(noise_type)

# Create and display plots
col1, col2 = st.columns(2)

with col1:
    st.subheader("Plot 1")
    fig1 = create_plots(grip_angle, noise_type, show_input, show_alpha, show_gamma,
                       I_alpha, I_gamma, show_torque, show_acceleration, t, noise)
    if fig1:
        st.pyplot(fig1)
        plt.close(fig1)

with col2:
    st.subheader("Plot 2 (Comparison)")
    grip_angle2 = st.slider("Grip Angle 2 (degrees)", 0, 90, 90, 1, key="angle2")
    fig2 = create_plots(grip_angle2, noise_type, show_input, show_alpha, show_gamma,
                       I_alpha, I_gamma, show_torque, show_acceleration, t, noise)
    if fig2:
        st.pyplot(fig2)
        plt.close(fig2)

# Info panel
st.markdown("---")
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown(f"""
    **Grip Angle 1: {grip_angle}°**
    - Component Magnitudes: Alpha = {np.abs(np.sin(np.deg2rad(grip_angle)))*100:.1f}%, Gamma = {np.abs(np.cos(np.deg2rad(grip_angle)))*100:.1f}%
    - Power Distribution: Alpha = {np.sin(np.deg2rad(grip_angle))**2*100:.1f}%, Gamma = {np.cos(np.deg2rad(grip_angle))**2*100:.1f}%
    """)

with col_info2:
    st.markdown(f"""
    **Grip Angle 2: {grip_angle2}°**
    - Component Magnitudes: Alpha = {np.abs(np.sin(np.deg2rad(grip_angle2)))*100:.1f}%, Gamma = {np.abs(np.cos(np.deg2rad(grip_angle2)))*100:.1f}%
    - Power Distribution: Alpha = {np.sin(np.deg2rad(grip_angle2))**2*100:.1f}%, Gamma = {np.cos(np.deg2rad(grip_angle2))**2*100:.1f}%
    """)

# Footer
st.markdown("---")
with st.expander("📐 Calculations & Assumptions"):
    st.markdown("""
    ### Transmission Functions
    - **Local Alpha (shaft axis):** sin(θ)
    - **Local Gamma (high inertia axis):** cos(θ)

    ### Angular Acceleration
    - **α = τ / I** (Newton's second law for rotation)
    - Higher inertia means lower acceleration for the same torque

    ### Assumptions
    - Rigid body model
    - Universal joint at wrist
    - Orthogonal axes
    - Linear transmission
    - Constant grip angle
    - No energy loss
    """)

