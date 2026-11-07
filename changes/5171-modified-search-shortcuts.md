---
issue: 5171
summary: "Leave modified keyboard shortcuts untouched by lazy search"
dl_state: "in_progress"
branch: "codex/5171-native-search-shortcuts"
owner: "codex"
next_step: "Review this keyboard slice and its browser receipts; other UX acceptance remains open"
---

Refs #5171. Ctrl/Meta/Alt chords no longer load lazy search or prevent their keyup
event; configured unmodified search keys still work. No article or rendering change.
