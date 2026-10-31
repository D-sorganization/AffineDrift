# AD #5167 header and navigation evidence

Captured 2026-10-31 from the live public pages in headless Chrome 144 after
`document.fonts.ready`. The browser used the `origin/main` or PR version of
`css/components/header-nav.css` injected into the page DOM. These are live DOM
captures, not local Quarto renders.

## Full-page screenshots with the PR CSS

| Page | 375×812 | 768×1024 | 1440×900 |
| --- | --- | --- | --- |
| Home | [375](home-375x812.jpg) | [768](home-768x1024.jpg) | [1440](home-1440x900.jpg) |
| Theory Part 1 | [375](theory-375x812.jpg) | [768](theory-768x1024.jpg) | [1440](theory-1440x900.jpg) |
| Physics of Golf, ch03 | [375](ch03-375x812.jpg) | [768](ch03-768x1024.jpg) | [1440](ch03-1440x900.jpg) |

## axe-core WCAG 2.x A/AA scans

axe-core 4.10.3 ran after fonts settled at 375×812 and 1440×900, with each
page scanned once using `origin/main` CSS and once using the PR CSS.

| Page | Viewport | Main passes / violations | PR passes / violations |
| --- | --- | ---: | ---: |
| Home | 375×812 | 27 / 0 | 27 / 0 |
| Home | 1440×900 | 26 / 0 | 26 / 0 |
| Theory Part 1 | 375×812 | 41 / 0 | 41 / 0 |
| Theory Part 1 | 1440×900 | 40 / 0 | 40 / 0 |
| Physics of Golf, ch03 | 375×812 | 28 / 0 | 28 / 0 |
| Physics of Golf, ch03 | 1440×900 | 28 / 0 | 28 / 0 |

## Remaining measurement

The requested Lighthouse mobile and desktop before/after runs remain
unavailable in this WSL 1 environment: `node --version` exits with
`WSL 1 is not supported`, and the Playwright wrapper is unavailable. No
Lighthouse scores or timing metrics are inferred from the axe scans or browser
captures.
