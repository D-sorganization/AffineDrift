# Changelog

All notable changes to AffineDrift will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive assessment framework (A-O) with 15 quality categories
- Jules Control Tower agent for automated maintenance

### Changed

- Updated README to reflect Quarto-based architecture
- Migrated from HTML to Quarto markdown (.qmd)

### Fixed

- Cleaned up tangent-space material parallel sets by enforcing a single canonical path in the article index and `_quarto.yml` render rules (#3913)
- MathJax equation rendering issues
- Footer duplication in \_quarto.yml

## [2.0.0] - 2026-01-05

### Added

- Quarto-based static site generation
- 74 QMD content files
- RSS feed integration
- Dark mode support

### Changed

- Complete redesign with scientific typography
- Mobile-responsive layout

### Research Content

- Drift-Control Ratio (DCR) metrics
- Control Cone biomechanical analysis
- Intermediate Axis Fallacy defense

## [1.0.0] - 2025-09-01

### Added

- Initial AffineDrift website
- Affine control theory introduction
- Golf swing biomechanics modeling
- Resource hub with curated materials
- MathJax for mathematical notation
- Refactored `Array.prototype.forEach` to `for...of` loops in `js/forms.js`, `js/history.js`, `js/navigation.js`, `js/startup-launcher.js`, `js/ui-components.js`, and `js/bibliography.js` to improve iteration performance.
