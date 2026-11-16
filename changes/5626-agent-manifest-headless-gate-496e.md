## Handoff

- **Branch:** cursor/5626-agent-manifest-headless-gate-496e
- **Issue:** Refs #5626
- **Summary:** Add UpstreamDrift install/headless pages to agent canonical manifest and llms.txt; headless prose CI contract; bump README parity pin to current UpstreamDrift main.
- **Validation:** `python3 -m scripts.check_upstreamdrift_headless_docs`; `python3 -m scripts.generate_agent_entry_point --check`; pytest on new 5626 gate tests.
- **Next step:** merge after CI green.