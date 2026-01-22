---
title: Critical Incomplete Content - "Coming Soon" Pages
date: 2026-01-22
status: Critical
label: jules:code-quality,critical
---

# Issue: User-Facing "Coming Soon" Placeholders

## Description
Multiple user-facing pages in the `docs/` directory contain "Coming Soon" text or placeholder images (`placehold.co`). These pages are reachable via navigation but offer no value, degrading the user experience and perceived quality.

## Affected Pages
*   `tools.qmd`
*   `resources-videos.qmd`
*   `resources-software.qmd`
*   `resources-researchers.qmd`
*   `resources-websites.qmd`
*   `resources-books.qmd`

## Remediation
1.  **Hide** these pages from navigation (`_quarto.yml`) until content is ready.
2.  **OR** Replace placeholders with minimal viable content immediately.
