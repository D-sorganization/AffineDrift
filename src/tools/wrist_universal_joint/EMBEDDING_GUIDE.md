# Embedding Guide: Grip Angle Torque Transmission Simulator

You now have **two beautiful versions** of the simulator that can be embedded in your GitHub Pages site!

## 🎨 Version 1: JavaScript/HTML5 (Standalone - Recommended for GitHub Pages)

**File:** `grip_angle_simulator.html`

### Features:

- ✅ Runs entirely on GitHub Pages (no external hosting needed)
- ✅ Beautiful modern UI with gradient backgrounds
- ✅ Interactive Plotly.js charts (professional, publication-quality)
- ✅ Real-time Canvas-based schematic visualization
- ✅ Fully responsive design
- ✅ Fast loading, no dependencies
- ✅ Works offline

### How to Embed:

#### Option A: Direct Link (Easiest)

Simply link to the file from any page:

```html
<a
  href="content/Wrist as Universal Joint/grip_angle_simulator.html"
  class="button"
  target="_blank"
>
  🏌️ Launch Grip Angle Simulator
</a>
```

#### Option B: Embed in Page (Iframe)

Add to any HTML page (e.g., `modelling.html`):

```html
<section id="grip-angle-simulator" class="interactive-section">
  <div class="container">
    <h2>Grip Angle Torque Transmission Simulator</h2>
    <p>
      Interactive tool to visualize how grip angle affects torque transmission
      and angular acceleration.
    </p>

    <iframe
      src="content/Wrist as Universal Joint/grip_angle_simulator.html"
      height="1000"
      width="100%"
      frameborder="0"
      scrolling="auto"
      style="border: 1px solid #ddd; border-radius: 8px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);"
    >
    </iframe>
  </div>
</section>
```

#### Option C: Full Page Integration

Copy the content from `grip_angle_simulator.html` and integrate it directly into your page HTML.

### Advantages:

- No external dependencies
- Works completely offline
- Fast loading
- Full control over styling
- No hosting costs

---

## ☁️ Version 2: Streamlit (Cloud-Hosted)

**File:** `Grip_Angle_Torque_Transmission_Streamlit.py`

### Features:

- ✅ Professional Streamlit interface
- ✅ Easy to update (just edit Python file)
- ✅ Automatic updates when code changes
- ✅ Built-in responsive design
- ✅ Shareable link

### Setup Steps:

1. **Create `requirements.txt`** (already created):

   ```
   streamlit>=1.28.0
   numpy>=1.24.0
   matplotlib>=3.7.0
   ```

2. **Deploy to Streamlit Cloud:**

   - Go to [streamlit.io/cloud](https://streamlit.io/cloud)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `content/Wrist as Universal Joint/Grip_Angle_Torque_Transmission_Streamlit.py`
   - Deploy!

3. **Get your URL** (e.g., `https://your-app.streamlit.app`)

4. **Embed in HTML:**

```html
<iframe
  src="https://your-app.streamlit.app/?embed=true"
  height="900"
  width="100%"
  frameborder="0"
  style="border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);"
>
</iframe>
```

### Advantages:

- Easy Python-based updates
- Automatic deployment
- Professional hosting
- Shareable standalone link

---

## 🎯 Recommended Approach

**For GitHub Pages:** Use the **JavaScript/HTML5 version** (`grip_angle_simulator.html`)

- No external dependencies
- Works entirely on your site
- Fast and reliable
- Beautiful modern design

**For sharing/updates:** Use **Streamlit version**

- Easy to update Python code
- Shareable link
- Good for rapid iterations

---

## 📝 Adding to Your Site

### Quick Integration Example

Add this to `modelling.html` or create a new page:

```html
<!doctype html>
<html lang="en">
  <head>
    <!-- Your existing head content -->
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <!-- Your existing header/nav -->

    <section id="simulator" class="interactive-section">
      <div class="container">
        <h2>Grip Angle Torque Transmission Simulator</h2>
        <p>
          Explore how grip angle affects torque transmission and club motion.
        </p>

        <!-- JavaScript Version (Recommended) -->
        <iframe
          src="content/Wrist as Universal Joint/grip_angle_simulator.html"
          height="1000"
          width="100%"
          frameborder="0"
          style="border: 1px solid #ddd; border-radius: 8px; margin: 20px 0;"
        >
        </iframe>

        <!-- OR Streamlit Version (if deployed) -->
        <!--
            <iframe 
                src="https://your-app.streamlit.app/?embed=true" 
                height="900" 
                width="100%" 
                frameborder="0"
                style="border: 1px solid #ddd; border-radius: 8px;">
            </iframe>
            -->
      </div>
    </section>

    <!-- Your existing footer -->
  </body>
</html>
```

### CSS Styling (add to `styles.css`) {#css-styling-add-to-styles-css}

```css
.interactive-section {
  padding: 4rem 0;
  background: #f8f9fa;
}

.interactive-section iframe {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  min-height: 1000px;
}

@media (max-width: 768px) {
  .interactive-section iframe {
    height: 1200px; /* Taller on mobile */
  }
}
```

---

## 🚀 Next Steps

1. **Test the JavaScript version locally:**

   - Open `grip_angle_simulator.html` in your browser
   - Verify all features work

2. **Commit and push:**

   ```bash
   git add content/Wrist\ as\ Universal\ Joint/grip_angle_simulator.html
   git commit -m "Add interactive grip angle simulator (JavaScript version)"
   git push
   ```

3. **Add to your site:**

   - Edit `modelling.html` or create new page
   - Add the iframe code above
   - Commit and push

4. **Optional - Deploy Streamlit version:**
   - Follow Streamlit Cloud setup
   - Get your URL
   - Add as alternative embed option

---

## ✨ Features Comparison

| Feature       | JavaScript Version | Streamlit Version |
| ------------- | ------------------ | ----------------- |
| Hosting       | GitHub Pages       | Streamlit Cloud   |
| Dependencies  | None (CDN)         | Python packages   |
| Updates       | Edit HTML/JS       | Edit Python       |
| Performance   | Very Fast          | Fast              |
| Offline       | ✅ Yes             | ❌ No             |
| Customization | Full Control       | Limited           |
| Mobile        | ✅ Responsive      | ✅ Responsive     |

Both versions include:

- ✅ Club properties input (weight, length, CG)
- ✅ Real-time inertia calculations
- ✅ Grip angle sliders (0°-90°)
- ✅ Multiple noise types
- ✅ Torque and acceleration plots
- ✅ Side-by-side comparison
- ✅ Beautiful visualizations
- ✅ Transmission analysis

---

Enjoy your shiny new interactive simulator! 🎉
