# Embedding Grip Angle Torque Transmission in GitHub Pages

## Option 1: Streamlit (Recommended - Easiest)

### Step 1: Host on Streamlit Cloud (Free)

1. **Create a requirements.txt file:**
```txt
streamlit>=1.28.0
numpy>=1.24.0
matplotlib>=3.7.0
```

2. **Push to GitHub** (if not already there)

3. **Go to [streamlit.io/cloud](https://streamlit.io/cloud)**
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `content/Wrist as Universal Joint/Grip_Angle_Torque_Transmission_Streamlit.py`
   - Deploy!

4. **Get your Streamlit URL** (e.g., `https://your-app.streamlit.app`)

### Step 2: Embed in Your HTML Page

Add this to any HTML page (e.g., `modelling.html` or create a new page):

```html
<section id="grip-angle-simulator" class="interactive-section">
    <div class="container">
        <h2>Grip Angle Torque Transmission Simulator</h2>
        <p>Interactive tool to visualize how grip angle affects torque transmission and angular acceleration.</p>

        <!-- Embed Streamlit app -->
        <iframe
            src="https://your-app.streamlit.app/?embed=true"
            height="800"
            width="100%"
            frameborder="0"
            scrolling="auto"
            style="border: 1px solid #ddd; border-radius: 8px; margin: 20px 0;">
        </iframe>

        <p class="note">
            <small>Note: This interactive simulator requires JavaScript to be enabled.</small>
        </p>
    </div>
</section>
```

### Step 3: Add CSS (in styles.css) {#step-3-add-css-in-styles-css}

```css
.interactive-section {
    padding: 4rem 0;
    background: #f8f9fa;
}

.interactive-section iframe {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    min-height: 800px;
}

@media (max-width: 768px) {
    .interactive-section iframe {
        height: 1000px; /* Taller on mobile */
    }
}
```

## Option 2: JavaScript/HTML5 Version (Runs Directly on GitHub Pages)

If you prefer a version that runs entirely on GitHub Pages without external hosting, I can create a pure JavaScript/HTML5 Canvas version. This would:
- Work completely offline
- No external dependencies
- Faster loading
- But requires rewriting the logic in JavaScript

Would you like me to create this version?

## Option 3: Plotly Dash (More Complex)

Plotly Dash offers more control but requires more setup. Similar to Streamlit but with more customization options.

## Quick Start: Streamlit Embedding

1. **Deploy to Streamlit Cloud** (5 minutes)
2. **Copy the iframe code above**
3. **Paste into your HTML page**
4. **Done!**

The Streamlit version I created includes all the same features:
- Club properties input
- Grip angle sliders
- Noise type selection
- Torque and acceleration plots
- Side-by-side comparison
- All calculations and physics
