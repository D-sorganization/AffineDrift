---
issue: 5789
summary: "Remove the retired vendored GAAI tree, daemon launcher, and slash-commands"
---

- Deletes `.gaai/`, `start-gaai-daemon.sh`, and GAAI slash-commands.
- Drops them from the root hygiene allowlist; the former project-rules fence test now asserts the tree is gone.
- Refs D-sorganization/Repository_Management#2725 and
  D-sorganization/Repository_Management#2727.
