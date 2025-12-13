# Sentinel's Journal

## 2024-05-23 - Unsanitized HTML Injection in Custom Build Script
**Vulnerability:** The `build-html.py` script injected `title` and `description` from `.qmd` YAML frontmatter directly into the HTML template without escaping. This allowed Cross-Site Scripting (XSS) via malicious metadata in source files.
**Learning:** Custom build scripts for static sites often lack the automatic sanitization features present in mature frameworks like Quarto or Jekyll. Input from source files (even "trusted" ones) should still be sanitized to prevent accidental markup breakage or injection.
**Prevention:** Always use `html.escape()` when injecting strings into HTML templates, even for build-time tools. Added strict typing and linting checks to the script.
