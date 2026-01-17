# AffineDrift Development Guide

**A Comprehensive Guide for Beginners Building Static Websites**

This guide will teach you everything you need to know to build, modify, and maintain the AffineDrift website, even if you've never built a website before.

## Table of Contents

1. [Understanding the Basics](#understanding-the-basics)
2. [Project Structure](#project-structure)
3. [HTML Fundamentals](#html-fundamentals)
4. [CSS Styling](#css-styling)
5. [JavaScript Interactivity](#javascript-interactivity)
6. [Development Workflow](#development-workflow)
7. [Testing Your Changes](#testing-your-changes)
8. [Git and Version Control](#git-and-version-control)
9. [Deployment](#deployment)
10. [Common Tasks](#common-tasks)
11. [Troubleshooting](#troubleshooting)
12. [Resources](#resources)

---

## Understanding the Basics

### What is a Static Website?

A static website is made up of files that are sent directly to the user's browser without any server-side processing. AffineDrift uses three core technologies:

- **HTML** (HyperText Markup Language): Structures the content
- **CSS** (Cascading Style Sheets): Styles and layouts the content
- **JavaScript**: Adds interactivity and dynamic behavior

### Why Static Sites?

- **Simple**: No databases or complex backend
- **Fast**: Files are served directly
- **Secure**: No server-side code to exploit
- **Free Hosting**: GitHub Pages hosts static sites for free
- **Version Controlled**: Every change is tracked in Git

---

## Project Structure

```
AffineDrift/
├── index.html              # Homepage (main entry point)
├── resources.html          # Resources page
├── styles.css              # All styling in one file
├── script.js               # Interactive JavaScript
├── README.md               # Project overview
├── DEVELOPMENT_GUIDE.md    # This file
├── WEBSITE_MANAGEMENT.md   # Content management guide
└── .github/
    └── workflows/
        └── deploy.yml      # Automated deployment
```

### File Descriptions

- **index.html**: The main page users see when they visit your site
- **resources.html**: A separate page for curated resources
- **styles.css**: Contains all visual styling (colors, fonts, layouts)
- **script.js**: Handles smooth scrolling, animations, and interactions
- **README.md**: Overview for anyone visiting the GitHub repository

---

## HTML Fundamentals

### Basic Structure

Every HTML page follows this structure:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Page Title</title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <!-- Your content goes here -->
  </body>
</html>
```

### Key HTML Elements Used

- `<header>`: Top section with navigation
- `<nav>`: Navigation menu
- `<main>`: Primary content area
- `<section>`: Logical sections of content
- `<div>`: Generic container for grouping
- `<h1>`, `<h2>`, `<h3>`: Headings (hierarchy)
- `<p>`: Paragraphs
- `<ul>` & `<li>`: Lists
- `<a>`: Links
- `<footer>`: Bottom section

### Semantic HTML

We use semantic HTML for better accessibility and SEO:

```html
<section id="theory" class="theory-section">
  <div class="container">
    <h2>What is Affine Control Theory?</h2>
    <p>Content here...</p>
  </div>
</section>
```

**Why?**

- Screen readers understand content structure
- Search engines rank pages better
- Code is more maintainable

---

## CSS Styling

### How CSS Works

CSS uses **selectors** to target HTML elements and apply **styles**:

```css
/* Select all paragraphs */
p {
  font-size: 1.2rem;
  line-height: 1.7;
}

/* Select elements with class "hero" */
.hero {
  background: linear-gradient(135deg, #0f4c75, #3282b8);
  padding: 8rem 0;
}

/* Select element with ID "theory" */
#theory {
  background-color: white;
}
```

### CSS Variables (Custom Properties)

We use CSS variables for consistent theming:

```css
:root {
  --primary-blue: #0f4c75;
  --accent-blue: #3282b8;
  --text-dark: #2c3e50;
}

/* Usage */
h2 {
  color: var(--primary-blue);
}
```

**Benefits:**

- Change colors site-wide by editing one place
- Easy to create color schemes
- Maintainable code

### Responsive Design

We use **media queries** to adapt to different screen sizes:

```css
/* Default (desktop) */
.site-title {
  font-size: 4rem;
}

/* Tablets */
@media (max-width: 768px) {
  .site-title {
    font-size: 2.5rem;
  }
}

/* Phones */
@media (max-width: 480px) {
  .site-title {
    font-size: 2rem;
  }
}
```

### Flexbox and Grid

**Flexbox** (for one-dimensional layouts):

```css
.nav-links {
  display: flex;
  gap: 2.5rem;
}
```

**Grid** (for two-dimensional layouts):

```css
.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
}
```

---

## JavaScript Interactivity

### What JavaScript Does

In AffineDrift, JavaScript handles:

- Smooth scrolling when clicking navigation links
- Highlighting the active section in navigation
- Fade-in animations as you scroll
- Mobile menu toggle (future feature)

### Basic Structure

```javascript
// Wait for page to load
document.addEventListener("DOMContentLoaded", function () {
  // Code runs after page loads
  console.log("Page loaded!");
});
```

### Smooth Scrolling Example

```javascript
links.forEach((link) => {
  link.addEventListener("click", function (e) {
    e.preventDefault(); // Stop default jump
    // Smoothly scroll to target
    window.scrollTo({
      top: targetPosition,
      behavior: "smooth",
    });
  });
});
```

---

## Development Workflow

### Setup Your Environment

1. **Install a Code Editor**

   - [VS Code](https://code.visualstudio.com/) (recommended)
   - [Sublime Text](https://www.sublimetext.com/)
   - [Atom](https://atom.io/)

2. **Install Git**

   - macOS: `brew install git` or download from [git-scm.com](https://git-scm.com/)
   - Linux: `sudo apt-get install git`
   - Windows: Download from [git-scm.com](https://git-scm.com/)

3. **Clone the Repository**
   ```bash
   git clone https://github.com/D-sorganization/AffineDrift.git
   cd AffineDrift
   ```

### Local Development

**Option 1: Open HTML directly**

- Right-click `index.html` → Open with → Your browser
- Simple but doesn't work well with some features

**Option 2: Use Python's Built-in Server** (Recommended)

```bash
python -m http.server 8000
# Visit http://localhost:8000 in your browser
```

**Option 3: Use VS Code Live Server**

- Install "Live Server" extension in VS Code
- Right-click `index.html` → "Open with Live Server"
- Auto-refreshes on save!

---

## Testing Your Changes

### Browser DevTools

Every browser has developer tools (F12 or right-click → Inspect):

1. **Elements Tab**: Inspect HTML and CSS in real-time
2. **Console Tab**: View JavaScript errors and logs
3. **Network Tab**: Check if resources load properly
4. **Responsive Mode**: Test different screen sizes

### Validation

**HTML Validation:**

- Use [W3C HTML Validator](https://validator.w3.org/)
- Upload your HTML file or paste the code

**CSS Validation:**

- Use [W3C CSS Validator](https://jigsaw.w3.org/css-validator/)

**Accessibility:**

- Use [WAVE](https://wave.webaim.org/)
- Checks for screen reader compatibility

### Cross-Browser Testing

Test in:

- Chrome/Edge (Chromium)
- Firefox
- Safari (if on Mac)

---

## Git and Version Control

### Basic Git Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "Update homepage content"

# Push to GitHub
git push origin main
```

### Branching

Create branches for new features:

```bash
# Create and switch to new branch
git checkout -b add-blog-section

# Make changes, commit

# Push branch
git push origin add-blog-section

# Create pull request on GitHub
```

### Best Practices

1. **Commit often** with clear messages
2. **Use branches** for experimental changes
3. **Write descriptive commit messages**:
   - ✅ "Add MathJax rendering for equations"
   - ❌ "Fixed stuff"

---

## Deployment

### GitHub Pages Setup

1. **Enable GitHub Pages**:

   - Go to repository Settings
   - Scroll to "Pages" section
   - Source: Deploy from a branch
   - Branch: `main` → `/root`
   - Save

2. **Custom Domain** (Optional):

   - Add `CNAME` file with your domain
   - Configure DNS settings with your provider

3. **Automatic Deployment**:
   - Handled by `.github/workflows/deploy.yml`
   - Deploys automatically on push to main

### Deployment Workflow

The GitHub Actions workflow:

```yaml
# Triggers on push to main
on:
  push:
    branches: [main]
# Deploys to GitHub Pages
# Validates HTML/CSS
# Runs accessibility checks
```

View deployment status in the "Actions" tab on GitHub.

---

## Common Tasks

### Adding a New Section to Homepage

1. Open `index.html`
2. Find the closing `</section>` of the last section
3. Add your new section:

```html
<section id="new-section" class="custom-section">
  <div class="container">
    <h2>New Section Title</h2>
    <p>Your content here...</p>
  </div>
</section>
```

4. Style it in `styles.css`:

```css
.custom-section {
  background: var(--pure-white);
  padding: 5rem 0;
}
```

5. Add to navigation in `<nav>`:

```html
<li><a href="#new-section">New Section</a></li>
```

### Adding a Resource

1. Open `resources.html`
2. Find the appropriate section (Videos, Papers, etc.)
3. Copy an existing resource card:

```html
<div class="resource-card video-card">
  <div class="resource-header">
    <span class="resource-type">YouTube</span>
    <h3>Your Video Title</h3>
  </div>
  <p class="resource-description">Description of the video or resource.</p>
  <div class="resource-tags">
    <span class="tag">Control Theory</span>
    <span class="tag">Advanced</span>
  </div>
  <a href="https://youtube.com/..." target="_blank" class="resource-link"
    >Watch Video</a
  >
</div>
```

### Changing Colors

Edit CSS variables in `styles.css`:

```css
:root {
  --primary-dark: #1a1a2e; /* Change this */
  --primary-blue: #0f4c75; /* And this */
  --accent-blue: #3282b8; /* And this */
}
```

All colors update automatically!

### Adding Math Equations

Use LaTeX notation with MathJax:

```html
<div class="equation">
  $$\dot{x}(t) = f_0(x) + \sum_{i=1}^{m} u_i(t) \cdot f_i(x)$$
</div>
```

**Inline math**: Use `$ ... $`
**Display math**: Use `$$ ... $$`

---

## Troubleshooting

### Common Issues

**Problem: Changes don't appear**

- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Clear browser cache
- Check if you saved the file

**Problem: CSS not loading**

- Check file path in `<link>` tag
- Ensure `styles.css` is in the same directory
- Check browser console for 404 errors

**Problem: JavaScript not working**

- Open browser console (F12)
- Look for error messages
- Ensure `<script src="script.js">` is before `</body>`

**Problem: MathJax not rendering**

- Check internet connection (MathJax loads from CDN)
- Verify MathJax script tag is in `<head>`
- Check for syntax errors in LaTeX

**Problem: GitHub Pages not updating**

- Check Actions tab for deployment status
- Wait 2-3 minutes after push
- Clear browser cache
- Check if branch is set correctly in Settings

### Debugging Tips

1. **Use console.log()**:

   ```javascript
   console.log("Debug message", variableName);
   ```

2. **Check Network Tab**:

   - See which files fail to load

3. **Validate HTML/CSS**:

   - Use W3C validators

4. **Test Incrementally**:
   - Make small changes and test
   - Easier to find what broke

---

## Resources

### Learning Web Development

**HTML:**

- [MDN HTML Tutorial](https://developer.mozilla.org/en-US/docs/Learn/HTML)
- [HTML5 Doctor](http://html5doctor.com/)

**CSS:**

- [CSS Tricks](https://css-tricks.com/)
- [Flexbox Froggy](https://flexboxfroggy.com/) (Game to learn Flexbox)
- [Grid Garden](https://cssgridgarden.com/) (Game to learn Grid)
- [MDN CSS Tutorial](https://developer.mozilla.org/en-US/docs/Learn/CSS)

**JavaScript:**

- [JavaScript.info](https://javascript.info/)
- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [Eloquent JavaScript](https://eloquentjavascript.net/) (Free book)

**Git:**

- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Learn Git Branching](https://learngitbranching.js.org/) (Interactive)

### Tools

- [VS Code](https://code.visualstudio.com/): Code editor
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/): Debugging
- [Can I Use](https://caniuse.com/): Browser compatibility
- [Color Picker](https://htmlcolorcodes.com/): Choose colors

### Mathematical Notation

- [MathJax Documentation](https://www.mathjax.org/)
- [LaTeX Math Symbols](https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols)
- [Detexify](http://detexify.kirelabs.org/classify.html): Draw symbol to find LaTeX

### Design Inspiration

- [Awwwards](https://www.awwwards.com/): Award-winning websites
- [Dribbble](https://dribbble.com/): Design inspiration
- [CodePen](https://codepen.io/): HTML/CSS/JS examples

---

## Next Steps

1. **Read through the code**: Understanding beats memorization
2. **Make small changes**: Experiment with colors, fonts, spacing
3. **Break things**: That's how you learn (Git has your back!)
4. **Build something new**: Add a blog section or image gallery
5. **Keep learning**: Web development is constantly evolving

---

**Remember**: Everyone starts as a beginner. The best way to learn is by doing. Don't be afraid to experiment, make mistakes, and ask questions!

Happy coding! 🚀
