# Self-Hosted Assets, SRI, and CSP vs. ADR 0002 Audit (#5252)

## 1. Inventory of Third-Party Scripts, Fonts, and Hosts

| Source / Rendered Surface | Asset Type | Third-Party Host | URL | SRI (`integrity`) | `crossorigin` |
| --- | --- | --- | --- | --- | --- |
| `_includes/mathjax-loader.html` | `script` (dynamic) | `cdn.jsdelivr.net` | `https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js` | **Yes** (`sha384-AHAnt9ZhGeHIrydA1Kp1L7FN+2UosbF7RQg6C+9Is/a7kDpQ1684C2iH2VWil6r4`) | `anonymous` |
| `_templates/latex_article.html` | `script` | `cdn.jsdelivr.net` | `https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js` | **Yes** (`sha384-Wuix6BuhrWbjDBs24bXrjf4ZQ5aFeFWBuKkFekO2t8xFU0iNaLQfp2K6/1Nxveei`) | `anonymous` |
| `_includes/site-head.html` | `preconnect` / `dns-prefetch` | `cdn.jsdelivr.net` | `https://cdn.jsdelivr.net` | N/A (connection hint) | `anonymous` |
| `_templates/latex_article.html` | `preconnect` / `dns-prefetch` | `cdn.jsdelivr.net` | `https://cdn.jsdelivr.net` | N/A (connection hint) | `anonymous` |
| `articles/rotation-converter.qmd` | `script` | `cdn.jsdelivr.net` | `https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js` | **No (MISSING)** | missing |
| `articles/rotation-converter.qmd` | `script` | `cdn.jsdelivr.net` | `https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js` | **No (MISSING)** | missing |
| `src/tools/wrist_universal_joint/grip_angle_simulator.html` | `script` | `cdn.plot.ly` | `https://cdn.plot.ly/plotly-2.26.0.min.js` | **No (MISSING)** | missing |
| `fonts/playfair-display/playfair-display-latin-400-700.woff2` (`_includes/site-head.html`, `css/tokens/typography.css`) | `font` (`woff2`) | `'self'` (self-hosted) | `/fonts/playfair-display/playfair-display-latin-400-700.woff2` | Self-hosted | `anonymous` |

## 2. Content-Security-Policy (`_includes/site-head.html`)

- `default-src 'self'`
- `script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net`
- `style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net`
- `font-src 'self' https://cdn.jsdelivr.net data:`
- `img-src 'self' data: https:`
- `connect-src 'self'`
- `frame-src 'self' https://www.youtube.com`
- `child-src 'self' https://www.youtube.com`

## 3. Gaps Against ADR 0002

1. **Missing SRI on ADR 0002 §7 CDN-exempted widget pages**:
   - `articles/rotation-converter.qmd` loads `three@0.147.0/build/three.min.js` and `OrbitControls.js` from `cdn.jsdelivr.net` without `integrity` or `crossorigin="anonymous"`.
   - `src/tools/wrist_universal_joint/grip_angle_simulator.html` loads `plotly-2.26.0.min.js` from `cdn.plot.ly` without `integrity` or `crossorigin="anonymous"`, and lacks the site-wide CSP `<meta>` header.
2. **MathJax CDN usage omitted from ADR 0002 §7**:
   - ADR 0002 §2 and §7 state that `https://cdn.jsdelivr.net` leaves the CSP once the two §7 widget migrations (`rotation-converter.qmd` and `grip_angle_simulator.html`) land.
   - However, `_includes/mathjax-loader.html` (`tex-chtml.js`) and `_templates/latex_article.html` (`tex-mml-chtml.js`) load MathJax 3.2.2 from `cdn.jsdelivr.net` (plus MathJax's dynamic `ui/lazy` extension and CHTML font/style subresources, which cannot carry static `<script integrity>` tags when dynamically fetched by MathJax's internal loader). Removing `https://cdn.jsdelivr.net` from `script-src`, `style-src`, and `font-src` therefore also requires either self-hosting MathJax or explicitly retaining `cdn.jsdelivr.net` for MathJax in ADR 0002.
3. **Duplicate MathJax bundles across templates**:
   - `_includes/mathjax-loader.html` gates and loads `tex-chtml.js`, whereas standalone `_templates/latex_article.html` unconditionally loads the heavier `tex-mml-chtml.js` bundle from `cdn.jsdelivr.net`.
