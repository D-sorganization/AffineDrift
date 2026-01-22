# Grip Angle Torque Transmission Simulator

Interactive tool for analyzing how grip angle affects torque transmission and angular acceleration in golf swing biomechanics.

## Files

- **`grip_angle_simulator.html`** - JavaScript/HTML5 standalone version (runs on GitHub Pages)
- **`Grip_Angle_Torque_Transmission_Streamlit.py`** - Streamlit version (deploy to Streamlit Cloud)
- **`requirements.txt`** - Python dependencies for Streamlit
- **`EMBEDDING_GUIDE.md`** - Complete instructions for embedding both versions
- **`EMBED_INSTRUCTIONS.md`** - Quick reference for embedding
- **`embed_example.html`** - Example HTML snippet for embedding

## Features

- Adjustable club properties (clubhead weight, shaft weight, length, CG distance)
- Real-time moment of inertia calculations
- Grip angle sliders (0° to 90°)
- Multiple noise input types (golf-like random, burst, step, sinusoidal)
- Dual plots: transmitted torque and angular acceleration
- Side-by-side comparison of different grip angles
- Beautiful visualizations with Plotly.js (JavaScript) or Matplotlib (Streamlit)

## Quick Start

### JavaScript Version (Recommended for GitHub Pages)

Simply link to or embed `grip_angle_simulator.html` in any HTML page.

### Streamlit Version

1. Deploy to [Streamlit Cloud](https://streamlit.io/cloud)
2. Set main file: `Grip_Angle_Torque_Transmission_Streamlit.py`
3. Embed via iframe using the URL provided by Streamlit Cloud

See `EMBEDDING_GUIDE.md` for detailed instructions.

## Article

This tool is featured in: [Wrists Behave as Universal Joints](../../docs/articles/wrist-universal-joint.html)
