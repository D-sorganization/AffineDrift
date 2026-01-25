---
title: Visible Placeholder Content on User-Facing Pages
labels: incomplete-implementation, critical, content
assignee: unassigned
---

## Description
Several public-facing documentation pages contain explicit "Coming Soon" text or placeholder messages. These indicate missing functionality and degrade the user experience.

### Affected Pages
1.  **`tools.qmd`**: Contains "Coming Soon" placeholders for:
    -   Unit Converter
    -   RRT Path Planner
    -   Solar System Model
    -   Games
2.  **`daydreams-doodles.qmd`**: "Future Projects" section lists unimplemented tools.
3.  **`contact.qmd`**: Social media links (Twitter/X, LinkedIn) are non-functional and marked "Coming Soon".
4.  **`archive/handcrafted-site/wrist-universal-joint.html`**: Contains an HTML comment/placeholder for a Streamlit app URL.

## Required Actions
- [ ] For `tools.qmd` and `daydreams-doodles.qmd`: Either implement the missing tools or hide the sections until they are ready.
- [ ] For `contact.qmd`: Add valid social media URLs or remove the links.
- [ ] For `wrist-universal-joint.html`: Deploy the Streamlit app and update the URL, or remove the iframe placeholder.
