# Contributing to AffineDrift

Thank you for your interest in contributing to AffineDrift! This document provides guidelines for contributing to the project.

## Ways to Contribute

1. **Report Issues**: Found a typo, broken link, or bug? [Open an issue](https://github.com/D-sorganization/AffineDrift/issues)

2. **Suggest Resources**: Know a great video, paper, or tool related to affine control theory or golf biomechanics? Let us know!

3. **Improve Documentation**: Help make guides clearer for beginners

4. **Fix Bugs**: Submit pull requests for any issues you find

5. **Enhance Content**: Suggest improvements to explanations or add new sections

## Getting Started

### Prerequisites

- **Git** - Version control
- **Python 3.8+** - For build scripts and tools
- **Quarto** - Static site generator ([Install Quarto](https://quarto.org/docs/get-started/))
- **Node.js** (optional) - For JavaScript linting and testing

### Initial Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/AffineDrift.git
   cd AffineDrift
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Quarto installation**:
   ```bash
   quarto check
   ```

5. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Make your changes** to `.qmd` files (Quarto markdown)
2. **Preview locally**:
   ```bash
   quarto preview
   ```
3. **Run quality checks**:
   ```bash
   # Python linting
   ruff check .
   ruff format .
   
   # Type checking
   mypy .
   
   # Run tests
   pytest
   ```
4. **Build the site**:
   ```bash
   quarto render
   ```
5. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   git push origin feature/your-feature-name
   ```
6. **Open a pull request** on GitHub

## Code Guidelines

### HTML

- Use semantic HTML5 elements
- Maintain consistent indentation (2 or 4 spaces)
- Add comments for complex sections
- Ensure accessibility (alt text, ARIA labels)

### CSS

- Use existing CSS variables for colors
- Follow BEM naming convention when adding new classes
- Keep specificity low
- Add comments for non-obvious styles
- Test responsive behavior

### JavaScript

- Write clean, readable code
- Add comments for complex logic
- Avoid global variables
- Test in multiple browsers

### Content

- Use clear, accessible language
- Explain technical terms
- Maintain consistent tone
- Check spelling and grammar
- Cite sources when appropriate

## Pull Request Process

1. **Update documentation** if you change functionality
2. **Test thoroughly** in multiple browsers
3. **Write a clear PR description**:
   - What changes did you make?
   - Why did you make them?
   - How did you test them?
4. **Keep PRs focused** - one feature or fix per PR
5. **Respond to feedback** from reviewers

## Reporting Issues

When reporting issues, please include:

- **Description**: What's the problem?
- **Steps to reproduce**: How can we see the issue?
- **Expected behavior**: What should happen?
- **Actual behavior**: What actually happens?
- **Screenshots**: If applicable
- **Browser/OS**: What environment are you using?

## Suggesting Resources

When suggesting resources for the Resources page:

1. **Verify the resource** is high-quality and relevant
2. **Provide complete information**:
   - Title
   - Author/Creator
   - URL
   - Brief description
   - Why it's valuable
3. **Suggest appropriate category**:
   - Video Lectures
   - Academic Papers/Books
   - Online Courses
   - Computational Tools
   - Helpful Links

## Code of Conduct

### Be Respectful

- Use welcoming and inclusive language
- Respect differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Be Professional

- No harassment, discrimination, or inappropriate content
- Keep discussions relevant and on-topic
- Assume good intentions

### Be Helpful

- Help beginners learn
- Share knowledge generously
- Give credit where it's due

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the "question" label
- Reach out via the repository discussions

## License

By contributing, you agree that your contributions will be licensed under the same terms as the project.

---

Thank you for helping make AffineDrift better! Your contributions, big or small, are greatly appreciated.
