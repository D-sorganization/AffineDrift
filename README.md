# AffineDrift

[![Quarto Syntax Check](https://github.com/D-sorganization/AffineDrift/actions/workflows/quarto-syntax-check.yml/badge.svg)](https://github.com/D-sorganization/AffineDrift/actions/workflows/quarto-syntax-check.yml)
[![Quarto](https://img.shields.io/badge/built%20with-Quarto-blue.svg)](https://quarto.org/)

**Mathematical Modeling of Golf Swing Dynamics**

AffineDrift is a research-focused website exploring the golf swing through the lens of affine control theory. This platform bridges abstract mathematical concepts with real-world biomechanics, creating a rigorous framework for understanding and optimizing one of sport's most complex movements.

## 🎯 Mission

To explore the profound mathematical structure underlying the golf swing by modeling it as an affine controllable system, creating a repository for research, insights, and resources at the intersection of mathematics, control theory, and golf biomechanics.

## 🌐 Website

This is a static website hosted on GitHub Pages at `AffineDrift.com`.

### Features

- **Mathematical Rigor**: Detailed explanations of affine control theory with proper mathematical notation
- **Golf Application**: Analysis of how control theory applies to golf swing biomechanics
- **Resource Hub**: Curated collection of videos, papers, and educational materials
- **Elegant Design**: Clean, technically sophisticated aesthetic that emphasizes content
- **Responsive**: Fully responsive design that works on all devices
- **MathJax Integration**: Beautiful rendering of mathematical equations

## 📁 Project Structure

```
AffineDrift/
├── index.qmd           # Main homepage (Quarto markdown)
├── _quarto.yml         # Quarto configuration
├── styles.css          # Custom styling
├── script.js           # Interactive features
├── docs/               # Additional documentation
│   └── assessments/    # Quality assessments
├── tests/              # Python tests
├── .github/
│   └── workflows/      # CI/CD pipelines
│       ├── ci-standard.yml      # Core quality gates and tests
│       ├── deploy-website.yml   # GitHub Pages deployment
│       └── quarto-syntax-check.yml # Quarto syntax validation
└── *.qmd               # Content pages (Quarto markdown)
```

## 🚀 Quick Start

### Viewing Locally

1. Clone this repository:

   ```bash
   git clone https://github.com/D-sorganization/AffineDrift.git
   cd AffineDrift
   ```

2. Preview with Quarto:
   ```bash
   quarto preview
   # Opens browser at http://localhost:4000
   ```

### Making Changes

1. Edit `.qmd` files to update content (Quarto markdown)
2. Modify `styles.css` to change styling
3. Run `quarto preview` to see changes live
4. Commit and push to automatically deploy via GitHub Actions

See [WEBSITE_MANAGEMENT.md](docs/development/WEBSITE_MANAGEMENT.md) for detailed instructions.

## 📚 Documentation

- **[DEVELOPMENT_GUIDE.md](docs/development/DEVELOPMENT_GUIDE.md)**: Complete beginner's guide to web development and this project
- **[WEBSITE_MANAGEMENT.md](docs/development/WEBSITE_MANAGEMENT.md)**: How to update content, add resources, and manage the site
- **[DOCS_ARTIFACT_POLICY.md](docs/development/DOCS_ARTIFACT_POLICY.md)**: Source-of-truth and generated `docs/` artifact rules

## 🛠️ Technologies

- **Quarto**: Scientific publishing system
- **HTML5/CSS3**: Styling with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Interactive features
- **MathJax**: Mathematical notation rendering
- **GitHub Pages**: Static site hosting
- **GitHub Actions**: Automated deployment

## 🐍 Python Runtime

- Tooling and type checks target **Python 3.12**
- CI runs quality checks and tests on Python 3.12
- Recommended local setup:

  ```bash
  python3.12 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

## 🔄 CI/CD Pipeline

This repository includes an automated CI/CD pipeline that:

- Validates HTML and CSS on every commit
- Automatically deploys to GitHub Pages on push to main branch
- Runs accessibility and performance checks
- See `.github/workflows/deploy-website.yml` and `.github/workflows/ci-standard.yml` for details

## 🤝 Contributing

This is a personal research platform, but suggestions and discussions are welcome! Feel free to:

- Open issues for suggestions or corrections
- Suggest resources to add to the Resources page
- Report any technical issues with the website

## 📖 Learning Resources

New to web development? Check out:

- [DEVELOPMENT_GUIDE.md](docs/development/DEVELOPMENT_GUIDE.md) for a comprehensive introduction
- [MDN Web Docs](https://developer.mozilla.org/) for HTML/CSS/JS reference
- [GitHub Pages Documentation](https://docs.github.com/pages)

## 📄 License

All content is the property of the repository owner. The code structure may be used as a template for similar projects with attribution.

## 🌟 Quote

> "What we do now echoes in eternity" — Marcus Aurelius

---

**AffineDrift** - Where control theory meets the fairway
