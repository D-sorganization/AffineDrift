# Code Quality Rules - AffineDrift

This document defines quality requirements for all code types in the AffineDrift repository.

---

## Table of Contents

1. [Python Code](#python-code)
2. [HTML](#html)
3. [CSS](#css)
4. [JavaScript](#javascript)
5. [MATLAB](#matlab)
6. [Quarto Documents](#quarto-documents)
7. [Markdown](#markdown)

---

## Python Code

### Requirements

- **Type Hints**: All functions must have return type annotations
- **Docstrings**: All functions must have docstrings (Google or NumPy style)
- **No Placeholders**: No TODO, FIXME, NotImplementedError, or pass statements
- **No Magic Numbers**: All constants must be named with units and sources
- **Error Handling**: All functions must handle errors appropriately
- **Formatting**: Code must pass Black formatting checks
- **Linting**: Code must pass Ruff linting checks
- **Type Checking**: Code must pass MyPy type checking

### Example

```python
def calculate_torque(
    force_n: float,  # [N] Applied force
    radius_m: float,  # [m] Moment arm
) -> float:
    """Calculate torque from force and radius.
    
    Args:
        force_n: Applied force [N]
        radius_m: Moment arm [m]
        
    Returns:
        Torque [N⋅m]
        
    Raises:
        ValueError: If force or radius is negative
    """
    if force_n < 0:
        raise ValueError(f"Force must be non-negative, got {force_n} N")
    if radius_m < 0:
        raise ValueError(f"Radius must be non-negative, got {radius_m} m")
    
    return force_n * radius_m  # [N⋅m]
```

---

## HTML

### Requirements

- **Valid HTML5**: All HTML must be valid HTML5
- **Semantic HTML**: Use semantic elements (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`)
- **Accessibility**: 
  - All images must have `alt` attributes
  - All forms must have labels
  - Use ARIA attributes where appropriate
  - Ensure proper heading hierarchy (h1 → h2 → h3)
- **Language Attribute**: Root `<html>` element must have `lang` attribute
- **Meta Tags**: Include proper meta tags (charset, viewport, description)
- **No Inline Styles**: Avoid inline styles (use CSS classes)
- **No Inline Scripts**: Avoid inline scripts (use external JS files)
- **Valid Links**: All links must be valid (no broken links)

### Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AffineDrift - Mathematical Modeling of Golf Swing Dynamics">
    <title>AffineDrift</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="index.html">Home</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <article>
            <h1>Article Title</h1>
            <img src="image.jpg" alt="Descriptive alt text">
        </article>
    </main>
    <footer>
        <p>&copy; 2025 AffineDrift</p>
    </footer>
    <script src="script.js"></script>
</body>
</html>
```

### Validation Tools

- `html-validate` - HTML validation
- Manual accessibility checks
- Browser developer tools

---

## CSS

### Requirements

- **Valid CSS3**: All CSS must be valid CSS3
- **Consistent Formatting**: Use consistent indentation (2 or 4 spaces)
- **No Magic Numbers**: Use CSS variables for colors, spacing, etc.
- **Responsive Design**: Use media queries for responsive layouts
- **Browser Compatibility**: Test in modern browsers
- **Performance**: 
  - Minimize CSS file size
  - Use efficient selectors
  - Avoid deep nesting (max 3-4 levels)
- **Organization**: 
  - Group related rules together
  - Use comments to separate sections
  - Follow BEM or similar naming convention

### Example

```css
/* CSS Variables */
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --spacing-unit: 1rem;
    --border-radius: 4px;
}

/* Component Styles */
.header {
    background-color: var(--primary-color);
    padding: var(--spacing-unit);
}

.header__title {
    color: white;
    font-size: 1.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header {
        padding: calc(var(--spacing-unit) / 2);
    }
}
```

### Validation Tools

- `stylelint` - CSS linting
- `prettier` - CSS formatting
- Browser developer tools

---

## JavaScript

### Requirements

- **Valid ES6+**: Use modern JavaScript (ES6+)
- **No Console Logs**: Remove `console.log` statements in production code
- **No Debugger**: Remove `debugger` statements
- **Error Handling**: Use try-catch for error handling
- **Strict Mode**: Use `'use strict';` at the top of files
- **Consistent Formatting**: Use consistent code style
- **Comments**: Add comments for complex logic
- **Performance**: 
  - Avoid global variables
  - Use const/let instead of var
  - Minimize DOM queries
- **Accessibility**: Ensure JavaScript doesn't break accessibility

### Example

```javascript
'use strict';

(function() {
    'use strict';
    
    const App = {
        init: function() {
            this.setupEventListeners();
        },
        
        setupEventListeners: function() {
            const button = document.querySelector('.button');
            if (button) {
                button.addEventListener('click', this.handleClick.bind(this));
            }
        },
        
        handleClick: function(event) {
            try {
                // Handle click event
                event.preventDefault();
                // ... logic here
            } catch (error) {
                console.error('Error handling click:', error);
                // Handle error appropriately
            }
        }
    };
    
    // Initialize app when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', App.init.bind(App));
    } else {
        App.init();
    }
})();
```

### Validation Tools

- `eslint` - JavaScript linting
- `prettier` - JavaScript formatting
- `node -c` - Syntax checking
- Browser developer tools

---

## MATLAB

### Requirements

- **Function Naming**: Function name must match filename
- **Help Documentation**: All functions must have help documentation
- **Input Validation**: Use `arguments` block (R2019b+) or `validateattributes`
- **No Clear All**: Avoid `clear all`, `clc`, `close all` in library code
- **No Eval**: Avoid `eval`, `assignin`, `feval` with strings
- **No Global**: Avoid global variables
- **Vectorization**: Use vectorized operations where possible
- **Preallocation**: Preallocate arrays before loops
- **Error Handling**: Use try-catch for error handling
- **Reproducibility**: Seed random number generator in tests

### Example

```matlab
function result = calculateTorque(force, radius)
    %CALCULATETORQUE Calculate torque from force and radius.
    %
    %   result = CALCULATETORQUE(force, radius) calculates the torque
    %   from the applied force and moment arm radius.
    %
    %   Inputs:
    %       force   - Applied force [N] (must be positive)
    %       radius  - Moment arm [m] (must be positive)
    %
    %   Outputs:
    %       result  - Torque [N⋅m]
    %
    %   Raises:
    %       Error if force or radius is negative
    
    arguments
        force (1,1) double {mustBePositive}
        radius (1,1) double {mustBePositive}
    end
    
    result = force * radius;  % [N⋅m]
end
```

### Validation Tools

- MATLAB Code Analyzer (`checkcode`/`mlint`) - Local development
- Python-based static analysis - CI/CD (no MATLAB license required)
- Manual code review

---

## Quarto Documents

### Requirements

- **Valid Syntax**: All .qmd files must have valid Quarto syntax
- **Proper Structure**: Use proper YAML front matter
- **Cross-References**: All cross-references must work
- **Code Chunks**: All code chunks must execute without errors
- **Mathematical Notation**: Use proper LaTeX syntax for equations
- **Citations**: Use consistent citation style
- **Links**: All links must be valid

### Example

```markdown
---
title: "Article Title"
author: "Author Name"
date: "2025-01-27"
format: html
---

## Introduction

This is an introduction with mathematical notation:

$$E = mc^2$$

And inline math: $F = ma$

## Code Example

```{python}
#| echo: true
import numpy as np
x = np.array([1, 2, 3])
print(x)
```

## References

See @citation-key for more information.
```

### Validation Tools

- `quarto check` - Structure validation
- `quarto render` - Rendering validation
- Manual review

---

## Markdown

### Requirements

- **Valid Markdown**: All .md files must have valid Markdown syntax
- **Consistent Formatting**: Use consistent heading levels
- **Links**: All links must be valid
- **Code Blocks**: Use proper syntax highlighting
- **Lists**: Use consistent list formatting
- **Tables**: Use proper table formatting

### Example

```markdown
# Main Heading

## Section Heading

This is a paragraph with a [link](https://example.com).

### Code Example

```python
def example():
    return "Hello, World!"
```

### List Example

- Item 1
- Item 2
  - Sub-item 2.1
  - Sub-item 2.2

### Table Example

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

### Validation Tools

- `markdownlint-cli2` - Markdown linting
- Manual review

---

## Common Quality Checks

All code types are checked for:

- **No TODO/FIXME**: Remove placeholder comments
- **No Debug Code**: Remove debug statements
- **Consistent Formatting**: Use automated formatters
- **Valid Syntax**: All code must be syntactically valid
- **Documentation**: All code must be documented
- **Error Handling**: All code must handle errors appropriately

---

## CI/CD Integration

All quality checks run automatically in CI/CD:

- **Python**: Ruff, MyPy, Black, pytest
- **HTML**: html-validate
- **CSS**: stylelint, prettier
- **JavaScript**: eslint, prettier, node syntax check
- **MATLAB**: Python-based static analysis
- **Quarto**: quarto check, quarto render
- **Markdown**: markdownlint-cli2

See `.github/workflows/ci.yml` for details.

---

**Last Updated:** 2025-01-27

