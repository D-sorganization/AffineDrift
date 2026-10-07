---
issue: 4597
summary: "Move the Quarto output-dir from docs/ to the git-ignored _site/ so docs/ holds only tracked internal documentation; untrack the committed CSS/JS/PDF build mirrors, drop the markdown-pruning half of prune_internal_docs_from_deploy.py, and pin the separation in tests/test_site_output_dir.py. Supersedes draft #4683."
branch: "chore/4597-site-output-dir"
---
