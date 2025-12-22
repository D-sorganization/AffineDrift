# Website Link Health Check

## Summary
- Internal documentation and site navigation now reference the corrected Pinocchio page (`models-pinocchio.html`) and GitHub repository (`Pinocchio_Golf_Model`).
- Custom navigation JavaScript no longer targets removed legacy selectors, avoiding inactive code paths during page loads.
- Legacy placeholder pages display archived notices with links to relevant current sections instead of rendering blank screens.

## Details
- Navbar, models listings, and repository references consistently use the Pinocchio spelling to prevent broken or misleading links.
- `script.js` now defers to Quarto's Bootstrap navbar for collapsing behavior and uses `.navbar-nav` anchors when highlighting sections.
- `legacy-pages/qmd/mujoco-demo.html` and `legacy-pages/qmd/reading-list.html` include lightweight HTML notices that guide visitors to active content.
