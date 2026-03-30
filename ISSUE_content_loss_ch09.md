# Content Loss: Volume II ch09 (Stochastic Trajectories) Truncated

**Priority:** High
**Labels:** bug, content-loss, geometry-of-motion
**Affected file:** `articles/The_Geometry_of_Motion/Volume_II/chapters/ch09_stochastic_trajectories_motor_.tex`

## Summary

The Agrachev & Sachkov integration commit (`f4fe4d7d`, PR #1849) truncated chapter 9 of Volume II mid-sentence at the Summary table. The file was cut from 126 lines to 72 lines, losing the final rows of the summary table and its closing environments.

## What Was Lost

The following content from the original file (commit `b04ff7f3`) was removed by the Agrachev integration and NOT replaced:

1. **Summary table rows** — The "Stochastic OCP", "Covariance Steering", and "Speed-Accuracy Tradeoff" rows were truncated
2. **Table/environment closings** — `\bottomrule`, `\end{tabular}`, `\end{center}`, `\vspace{0.3cm}`
3. **TikZ figure** (intentionally removed?) — A Deterministic OCP vs Stochastic OCP comparison diagram with trajectory ensembles and covariance ellipses was removed in the same commit

## Additional Content Changes in Same Commit

The Agrachev commit also made these intentional changes to ch09:

- Removed the `\begin{gomdraftnotice}` block (good — chapter is no longer draft)
- Removed `\cite{Henneman1957}`, `\cite{HarrisWolpert1998}`, `\cite{FlashHogan1985}`, `\cite{Fitts1954}` citations
- Simplified the Minimum Variance Theory discussion (removed mention of Flash & Hogan minimum jerk as alternative theory)
- Added two new paragraphs about Agrachev & Sachkov's risk-sensitive control and stochastic attainable sets

**Decision needed:** Were the citation removals intentional? The original cited Henneman 1957, Harris & Wolpert 1998, Flash & Hogan 1985, and Fitts 1954 — all foundational references for this chapter's topic.

## Temporary Fix Applied

The summary table has been restored from the original `b04ff7f3` version with all 5 rows intact. The TikZ diagram has NOT been restored (unclear if its removal was intentional).

## Recovery / Verification Steps

```bash
# View the full original version
git show b04ff7f3:articles/The_Geometry_of_Motion/Volume_II/chapters/ch09_stochastic_trajectories_motor_.tex

# View the diff that caused the truncation
git diff b04ff7f3..f4fe4d7d -- articles/The_Geometry_of_Motion/Volume_II/chapters/ch09_stochastic_trajectories_motor_.tex

# Verify current version compiles
cd articles/The_Geometry_of_Motion/Volume_II && latexmk -pdf -interaction=nonstopmode main.tex
```

## Decisions Required

1. Should the TikZ diagram (Deterministic vs Stochastic OCP visualization) be restored?
2. Should the removed citations (Henneman, Harris & Wolpert, Flash & Hogan, Fitts) be re-added?
3. Is the simplified Minimum Variance Theory section acceptable, or should the original nuanced version (acknowledging both minimum jerk and minimum variance theories) be restored?
