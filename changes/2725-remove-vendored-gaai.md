# Change fragment: remove the retired vendored GAAI tree

- Deletes `.gaai/`, `start-gaai-daemon.sh`, and GAAI slash-commands.
- Drops them from the root hygiene allowlist; the former project-rules fence test now asserts the tree is gone.
- Refs #2725. Refs #2727.
