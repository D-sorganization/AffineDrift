# Website Management Guide

**Quick Reference for Managing AffineDrift Content**

This guide provides simple instructions for common content management tasks. For technical details, see [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md).

## Table of Contents

1. [Quick Edit Workflow](#quick-edit-workflow)
2. [Updating Homepage Content](#updating-homepage-content)
3. [Managing Resources](#managing-resources)
4. [Adding Mathematical Equations](#adding-mathematical-equations)
5. [Changing Design Elements](#changing-design-elements)
6. [SEO and Metadata](#seo-and-metadata)
7. [Best Practices](#best-practices)

---

## Quick Edit Workflow

### For Small Changes

1. **Navigate to the file on GitHub**
2. **Click the pencil icon** (Edit this file)
3. **Make your changes**
4. **Scroll down to "Commit changes"**
5. **Write a brief description** (e.g., "Update mission statement")
6. **Click "Commit changes"**

Changes will automatically deploy in 2-3 minutes!

### For Larger Changes

1. **Clone or pull the repository**:

   ```bash
   git pull origin main
   ```

2. **Make changes locally** in your editor

3. **Test locally**:

   ```bash
   python -m http.server 8000
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

---

## Updating Homepage Content

### Changing the Featured Quote

**File:** `index.html`
**Location:** Lines 37-40

```html
<blockquote class="featured-quote">
  <p>"What we do now echoes in eternity"</p>
  <cite>— Marcus Aurelius</cite>
</blockquote>
```

Simply replace the text and author name.

### Updating Mission Statement

**File:** `index.html`
**Location:** Lines 48-59 (Mission section)

```html
<p class="mission-text">AffineDrift is dedicated to exploring...</p>
```

Edit the paragraph content directly.

### Modifying Theory Explanations

**File:** `index.html`
**Location:** Lines 64-116 (Theory section)

Key areas to edit:

- Introduction paragraphs
- Mathematical equations (see [Adding Mathematical Equations](#adding-mathematical-equations))
- Property cards

Example - editing a property card:

```html
<div class="property-card">
  <h4>Property Name</h4>
  <p>Description of the property</p>
</div>
```

### Updating Website Goals

**File:** `index.html`
**Location:** Lines 173-198 (Goals section)

```html
<div class="goal-card">
  <div class="goal-number">01</div>
  <h3>Goal Title</h3>
  <p>Goal description</p>
</div>
```

To add a new goal, copy an entire `<div class="goal-card">...</div>` block and modify it.

---

## Managing Resources

### Adding a Video Resource

**File:** `resources.html`
**Location:** Resource grid sections

```html
<div class="resource-card video-card">
  <div class="resource-header">
    <span class="resource-type">YouTube</span>
    <h3>Video Title Here</h3>
  </div>
  <p class="resource-description">
    Brief description of what this video covers and why it's useful.
  </p>
  <div class="resource-tags">
    <span class="tag">Control Theory</span>
    <span class="tag">Beginner</span>
  </div>
  <p class="resource-note">Optional note or call-to-action</p>
</div>
```

**Resource Types:**

- `YouTube` - For video content
- `Course` - For online courses
- `Software` - For tools and programs
- `Tool` - For utilities
- `Paper` - For academic papers

**Tags:**

- `Control Theory`, `Differential Geometry`, `Biomechanics`, `Golf`
- `Fundamentals`, `Advanced`, `Beginner`
- `Open Source`, `Free`, `Commercial`
- `Python`, `MATLAB`, `MIT`

### Adding Academic Papers/Books

**File:** `resources.html`
**Location:** Academic Resources section (lines ~100-160)

```html
<li>
  <strong>"Book or Paper Title"</strong> by Author Name
  <p class="resource-detail">Brief description of content and relevance</p>
</li>
```

### Adding External Links

**File:** `resources.html`
**Location:** Links section

```html
<div class="link-card">
  <h3>Category Name</h3>
  <ul class="link-list">
    <li>
      <a href="https://example.com" target="_blank" rel="noopener"
        >Link Title</a
      >
    </li>
    <li>
      <a href="https://example2.com" target="_blank" rel="noopener"
        >Another Link</a
      >
    </li>
  </ul>
</div>
```

**Important:** Always include:

- `target="_blank"` - Opens in new tab
- `rel="noopener"` - Security best practice

### Creating a New Resource Category

1. Copy an entire `<div class="resource-grid">...</div>` section
2. Change the section heading
3. Add your resource cards
4. Place between existing sections

---

## Adding Mathematical Equations

### Using MathJax

AffineDrift uses MathJax for beautiful mathematical notation. Use LaTeX syntax:

### Display Equations (Centered, Large)

```html
<div class="equation">
  $$\dot{x}(t) = f_0(x) + \sum_{i=1}^{m} u_i(t) \cdot f_i(x)$$
</div>
```

### Inline Equations (Within Text)

```html
<p>
  The state space $x \in \mathbb{R}^n$ represents all possible configurations.
</p>
```

### Common LaTeX Symbols

| Symbol             | LaTeX Code        | Example             |
| ------------------ | ----------------- | ------------------- |
| Dot notation       | `\dot{x}`         | $\dot{x}$         |
| Partial derivative | `\partial`        | $\partial$        |
| Integral           | `\int`            | $\int$            |
| Sum                | `\sum_{i=1}^{n}`  | $\sum_{i=1}^{n}$ |
| Greek letters      | `\alpha`, `\beta` | $\alpha, \beta$   |
| Vectors            | `\vec{v}`         | $\vec{v}$         |
| Real numbers       | `\mathbb{R}`      | $\mathbb{R}$      |
| Subscript          | `x_i`             | $x_i$             |
| Superscript        | `x^2`             | $x^2$             |
| Fraction           | `\frac{a}{b}`     | $\frac{a}{b}$     |

### Equation Explanation Block

```html
<div class="equation-explanation">
  <p>where:</p>
  <ul>
    <li>\(x \in \mathbb{R}^n\) is the state vector</li>
    <li>\(u_i\) are the control inputs</li>
  </ul>
</div>
```

### Testing Equations

1. Make changes locally
2. Open in browser
3. Wait for MathJax to render (1-2 seconds)
4. If equations don't show, check:
   - Internet connection (MathJax loads from CDN)
   - LaTeX syntax errors
   - Browser console for errors

**Resources:**

- [LaTeX Math Symbols Reference](https://www.cmor-faculty.rice.edu/~heinken/latex/symbols.pdf)
- [MathJax Documentation](https://docs.mathjax.org/)

---

## Changing Design Elements

### Colors

**File:** `styles.css`
**Location:** Lines 12-30 (`:root` section)

```css
:root {
  --primary-dark: #1a1a2e;
  --primary-blue: #0f4c75;
  --accent-blue: #3282b8;
  --light-blue: #bbe1fa;
  --math-gold: #d4af37;
}
```

Change the hex color codes to update colors site-wide.

**Finding Colors:**

- [Adobe Color](https://color.adobe.com/)
- [Coolors](https://coolors.co/)
- [HTML Color Codes](https://htmlcolorcodes.com/)

### Fonts

**File:** `styles.css`
**Location:** Lines 32-46

```css
body {
  font-family: "Charter", "Georgia", "Times New Roman", serif;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  font-family: "Computer Modern", "Latin Modern", "Palatino", serif;
}
```

To use Google Fonts:

1. Visit [Google Fonts](https://fonts.google.com/)
2. Select a font
3. Copy the `<link>` tag to `<head>` in HTML
4. Update `font-family` in CSS

### Spacing and Sizing

Common adjustments in `styles.css`:

```css
/* Section padding */
section {
  padding: 5rem 0; /* Adjust this value */
}

/* Font sizes */
.site-title {
  font-size: 4rem; /* Adjust heading size */
}

/* Container width */
.container {
  max-width: 1200px; /* Adjust content width */
}
```

---

## SEO and Metadata

### Page Title and Description

**File:** `index.html` (and other HTML files)
**Location:** `<head>` section

```html
<head>
  <title>AffineDrift - Affine Control Theory & Golf Swing Dynamics</title>
  <meta
    name="description"
    content="Mathematical modeling of the golf swing as an affine controllable system"
  />
  <meta
    name="keywords"
    content="affine control, golf swing, biomechanics, control theory"
  />
</head>
```

**Best Practices:**

- Title: 50-60 characters
- Description: 150-160 characters
- Keywords: 5-10 relevant terms

### Social Media Previews

Add Open Graph tags to `<head>`:

```html
<meta property="og:title" content="AffineDrift - Golf Swing Control Theory" />
<meta
  property="og:description"
  content="Exploring the mathematics of the golf swing"
/>
<meta property="og:image" content="https://affinedrift.com/preview-image.jpg" />
<meta property="og:url" content="https://affinedrift.com" />
```

### Favicon

Add a favicon (website icon in browser tab):

1. Create a 32x32 or 64x64 pixel PNG image
2. Save as `favicon.png` in root directory
3. Add to `<head>`:

```html
<link rel="icon" type="image/png" href="favicon.png" />
```

---

## Best Practices

### Content Guidelines

1. **Be Consistent**

   - Use the same tone throughout
   - Maintain formatting patterns
   - Follow existing structure

2. **Write for Your Audience**

   - Explain technical terms
   - Provide context for equations
   - Link to additional resources

3. **Keep It Accessible**
   - Use descriptive link text (not "click here")
   - Add alt text to images
   - Maintain color contrast
   - Test with screen readers

### File Organization

1. **Naming Conventions**

   - Use lowercase
   - Use hyphens, not spaces: `new-page.html`
   - Be descriptive: `golf-biomechanics-resources.html`

2. **Folder Structure** (if adding images/assets)

   ```
   AffineDrift/
   ├── index.html
   ├── styles.css
   ├── images/
   │   ├── logo.png
   │   └── diagrams/
   │       └── control-system.svg
   └── documents/
       └── research-papers.pdf
   ```

3. **Image Optimization**
   - Compress images before uploading
   - Use appropriate formats:
     - JPEG for photos
     - PNG for graphics with transparency
     - SVG for diagrams and logos
   - Tools: [TinyPNG](https://tinypng.com/), [Squoosh](https://squoosh.app/)

### Version Control

1. **Commit Messages**

   - Be descriptive: "Add new section on Lie brackets in control theory"
   - Not vague: "Update stuff"

2. **Commit Frequently**

   - Small, logical commits
   - Easier to revert if needed
   - Better project history

3. **Branch for Experiments**
   ```bash
   git checkout -b experimental-feature
   # Make changes
   git commit -m "Test new layout"
   # If good, merge to main
   git checkout main
   git merge experimental-feature
   ```

### Testing Checklist

Before pushing changes:

- [ ] Test in multiple browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile (use DevTools responsive mode)
- [ ] Check all links work
- [ ] Verify equations render correctly
- [ ] Check for spelling/grammar errors
- [ ] Validate HTML and CSS
- [ ] Review git diff to see what changed

### Performance

1. **Keep Files Small**

   - Minify CSS/JS for production (optional)
   - Compress images
   - Limit use of large fonts

2. **Lazy Load Images** (if adding many images)

   ```html
   <img src="image.jpg" loading="lazy" alt="Description" />
   ```

3. **Use CDN for Libraries**
   - MathJax, fonts loaded from CDN
   - Faster than hosting locally

---

## Quick Reference Commands

### Git Commands

```bash
# Check status
git status

# Pull latest changes
git pull origin main

# Stage all changes
git add .

# Commit with message
git commit -m "Your message here"

# Push to GitHub
git push origin main

# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

### Local Testing

```bash
# Python server
python -m http.server 8000

# Python 3 specific
python3 -m http.server 8000

# Node.js http-server (if installed)
npx http-server -p 8000
```

---

## Troubleshooting Quick Fixes

### Changes Not Showing on Live Site

1. Wait 2-3 minutes after push
2. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
3. Check GitHub Actions tab for deployment status
4. Clear browser cache

### Broken Layout

1. Check browser console (F12) for errors
2. Validate HTML and CSS
3. Look for missing closing tags
4. Check for typos in class names

### Equations Not Rendering

1. Check internet connection
2. Look for LaTeX syntax errors
3. Ensure MathJax script is in `<head>`
4. Wait a few seconds for rendering

---

## Need Help?

- **Development questions**: See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- **HTML/CSS/JS reference**: [MDN Web Docs](https://developer.mozilla.org/)
- **Git help**: [Git Documentation](https://git-scm.com/doc)
- **MathJax**: [MathJax Documentation](https://docs.mathjax.org/)

---

**Remember**: Always test locally before pushing to production. When in doubt, commit your current work before making experimental changes!

Happy editing! ✨
