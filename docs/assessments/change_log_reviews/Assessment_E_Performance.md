# Assessment E Results: Performance & Scalability

## Executive Summary

The static nature of the site ensures excellent runtime performance for readers. Build performance is the primary concern, as `build-html.py` processes files sequentially and uses regex, which scales linearly. For the current size (~50 articles), this is negligible, but it could become a bottleneck. Frontend performance is managed via `requestAnimationFrame` in `script.js`.

## Top Risks

1.  **Build Time Scaling (Severity: LOW)**: Sequential processing in `build-html.py`.
2.  **Asset Loading (Severity: LOW)**: Large scientific images/GIFs (like `A-Dead-Fish-Swims.gif`) could impact LCP (Largest Contentful Paint).
3.  **Regex Overhead (Severity: LOW)**: Heavy use of regex for HTML parsing in Python is slower than using a dedicated parser like `BeautifulSoup` (though `check_site_health.py` uses `bs4`, `build-html.py` uses regex).

## Scorecard

| Category               | Score | Evidence                                           | Remediation                               |
| ---------------------- | ----- | -------------------------------------------------- | ----------------------------------------- |
| Runtime Performance    | 10/10 | Static HTML is extremely fast.                     | N/A                                       |
| Build Performance      | 8/10  | Python script is efficient enough for now.         | Parallelize if content > 1000 pages.      |
| Asset Optimization     | 7/10  | GIFs usage detected; usually heavy.                | Convert GIFs to MP4/WebM.                 |
| Algorithmic Efficiency | 8/10  | `script.js` uses throttling.                       | N/A                                       |

**Weighted Score: 8.3/10**

## Refactoring Plan

**Quick Wins**
1.  **Optimize Assets**: Check file size of `static/images/`. Compress if necessary.

**Strategic Fixes**
1.  **Switch to BS4**: Refactor `build-html.py` to use `BeautifulSoup` for more robust and potentially faster parsing (or just robustness).
