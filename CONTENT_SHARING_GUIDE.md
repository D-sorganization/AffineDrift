# Content Sharing Guide: Including Projects from Other Repositories

## Overview

When you want to add a project from another repository to your website (e.g., in "Daydreams & Doodles"), you have several options. This guide explains the trade-offs and recommends the best approach for your static website.

## Option 1: Copy Content into This Repo (Recommended)

**How it works:** Copy the relevant files from your other repository into this one.

**Pros:**
- ✅ Simplest and most reliable
- ✅ Works perfectly with static site hosting (GitHub Pages)
- ✅ No dependencies or build complexity
- ✅ Fast loading (all content in one place)
- ✅ Easy to maintain and version control
- ✅ Can customize content for website presentation

**Cons:**
- ❌ Content exists in two places (need to sync manually)
- ❌ Larger repository size

**When to use:** Best for most cases, especially for:
- Static HTML/JS/CSS projects
- Documentation or articles
- Small to medium projects
- Projects you want to customize for the website

**Example workflow:**
```bash
# Copy project files
cp -r ../other-repo/project-name ./daydreams/project-name/

# Or copy specific files
cp ../other-repo/index.html ./daydreams/project-name/
cp ../other-repo/styles.css ./daydreams/project-name/

# Commit to this repo
git add daydreams/project-name/
git commit -m "Add project-name to Daydreams & Doodles"
```

## Option 2: External Links to Other GitHub Pages

**How it works:** Host the project in its own repository with GitHub Pages, then link to it from your website.

**Pros:**
- ✅ Keep projects in separate repos
- ✅ Each project has its own URL
- ✅ Can update projects independently
- ✅ No duplication

**Cons:**
- ❌ Projects load from different domains (not seamless)
- ❌ Need to set up GitHub Pages for each project
- ❌ More complex navigation
- ❌ Different styling/theme per project

**When to use:** Good for:
- Large, independent projects
- Projects that need their own domain/subdomain
- Projects you want to keep completely separate

**Example:**
```html
<div class="resource-card">
    <h3>My Space Flight Calculator</h3>
    <p class="resource-description">
        Interactive orbital mechanics calculator built with Python and JavaScript.
    </p>
    <a href="https://your-username.github.io/space-calculator/"
       class="resource-link"
       target="_blank"
       rel="noopener">
        View Project →
    </a>
</div>
```

## Option 3: Git Submodules (Advanced)

**How it works:** Include another repository as a subdirectory in this repository.

**Pros:**
- ✅ Keep projects in separate repos
- ✅ Can pull updates from source repo
- ✅ Version control for submodule

**Cons:**
- ❌ Complex to set up and maintain
- ❌ Can be fragile (submodule pointer issues)
- ❌ GitHub Pages may not handle submodules well
- ❌ Requires understanding of git submodules
- ❌ Team members need to know how to work with submodules

**When to use:** Rarely recommended for static websites. Only if:
- You're very comfortable with git submodules
- The project is actively developed in another repo
- You need to pull updates frequently

**Example:**
```bash
# Add submodule
git submodule add https://github.com/username/project-name.git daydreams/project-name

# Update submodule
git submodule update --remote daydreams/project-name
```

## Option 4: Build Process Integration

**How it works:** Use a build script that pulls content from other repos during site generation.

**Pros:**
- ✅ Keep projects separate
- ✅ Automated syncing
- ✅ Can transform content during build

**Cons:**
- ❌ Requires build infrastructure
- ❌ More complex CI/CD setup
- ❌ Need to handle authentication for private repos
- ❌ Build failures if source repo is unavailable

**When to use:** Good for:
- Automated content aggregation
- When using Quarto or other build systems
- Large-scale content management

**Example (pseudo-code):**
```bash
# In build script
git clone https://github.com/username/project-name.git temp/
cp -r temp/src ./daydreams/project-name/
rm -rf temp/
```

## Recommended Approach for AffineDrift

### For "Daydreams & Doodles" Projects

**Recommended: Copy content into this repo**

1. **Create a directory structure:**
   ```
   daydreams/
   ├── space-flight/
   │   ├── index.html
   │   ├── calculator.js
   │   └── styles.css
   ├── chemical-engineering/
   │   └── ...
   └── calculators/
       └── ...
   ```

2. **Copy files from other repos:**
   ```bash
   mkdir -p daydreams/space-flight
   cp -r ../space-flight-repo/* daydreams/space-flight/
   ```

3. **Update daydreams-doodles.html:**
   ```html
   <div class="resource-card">
       <h3>Space Flight Calculator</h3>
       <p class="resource-description">
           Interactive orbital mechanics calculator...
       </p>
       <a href="daydreams/space-flight/index.html"
          class="resource-link">
           View Project →
       </a>
   </div>
   ```

4. **Commit to this repo:**
   ```bash
   git add daydreams/
   git commit -m "Add space flight calculator to Daydreams & Doodles"
   ```

### When to Use External Links

Use external links when:
- Project is very large (would bloat this repo)
- Project has its own deployment/CI/CD
- Project needs to be updated frequently and independently
- Project is a separate service/application

## Best Practices

1. **Keep it simple:** For static websites, copying content is usually best
2. **Organize well:** Use clear directory structure (`daydreams/project-name/`)
3. **Document sources:** Add a README in each project directory noting the source repo
4. **Sync strategy:** Decide how to handle updates:
   - Manual copy when needed
   - Periodic sync script
   - One-time copy if project is "finished"

## Example: Adding a Project

Let's say you have a space flight calculator in `../space-calculator/`:

```bash
# 1. Create directory
mkdir -p daydreams/space-calculator

# 2. Copy files
cp ../space-calculator/index.html daydreams/space-calculator/
cp ../space-calculator/calculator.js daydreams/space-calculator/
cp ../space-calculator/styles.css daydreams/space-calculator/

# 3. Add README with source info
cat > daydreams/space-calculator/README.md << EOF
# Space Flight Calculator

Source repository: https://github.com/username/space-calculator

This project was copied into AffineDrift for website integration.
Original development happens in the source repository.
EOF

# 4. Update daydreams-doodles.html to link to it
# (Edit the HTML file to add a resource card)

# 5. Commit
git add daydreams/
git add daydreams-doodles.html
git commit -m "Add space flight calculator to Daydreams & Doodles"
```

## Summary

**For AffineDrift website:**
- ✅ **Copy content** - Best for most projects
- ⚠️ **External links** - Good for very large or independent projects
- ❌ **Git submodules** - Too complex for static sites
- ⚠️ **Build process** - Only if using Quarto/build system extensively

**Recommendation:** Start with copying content. It's simple, reliable, and works perfectly with GitHub Pages. You can always refactor later if needed.
