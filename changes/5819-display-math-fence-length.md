---
issue: 5819
summary: "Make the display-maths checker honour code-fence character and length so nested fences no longer invert its state."
---

`check_display_math.py` closed a fence on any fence-looking line, so a shorter
or different fence nested inside a longer one flipped the in-code state for the
rest of the file and hid undelimited equations. Fences now follow CommonMark
closing rules. Regression tests cover nested backtick and tilde fences.
