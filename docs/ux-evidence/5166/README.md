# AD #5166 rendered typography screenshots

Full-page follow-up captures after the 55ch reading-measure correction. Each
image was captured after fonts settled at the requested viewport dimensions.
The captures use the live page DOM with the PR CSS from this worktree injected;
Quarto could not render locally because its dotenv profile requires an absent
`CODECOV_TOKEN`, so these are not local Quarto branch renders.

## Home

- [375×812](home-375.jpg)
- [768×1024](home-768.jpg)
- [1440×900](home-1440.jpg)

## Theory Part 1

- [375×812](theory-375.jpg)
- [768×1024](theory-768.jpg)
- [1440×900](theory-1440.jpg)

## Physics of Golf, chapter 3

- [375×812](ch03-375.jpg)
- [768×1024](ch03-768.jpg)
- [1440×900](ch03-1440.jpg)

## axe-core WCAG 2.x A/AA scans

axe-core 4.14.0 (via `@axe-core/playwright`) ran 2026-11-01 after
`document.fonts.ready` on the live public site at 375×812 and 1440×900.
Tags included WCAG 2.0, 2.1, and 2.2 A/AA. Reproduce with
`node docs/ux-evidence/5166/capture_axe.js` after `npm ci`.

| Page | Viewport | Passes | Violations |
| --- | --- | ---: | ---: |
| Home | 375×812 | 27 | 0 |
| Home | 1440×900 | 27 | 0 |
| Theory Part 1 | 375×812 | 42 | 0 |
| Theory Part 1 | 1440×900 | 41 | 0 |
| Physics of Golf, ch03 | 375×812 | 29 | 0 |
| Physics of Golf, ch03 | 1440×900 | 29 | 0 |

## Lighthouse metrics (post-merge baseline)

Typography tokens landed on production through #5235, #5272, and #5280. Each row
below is one Lighthouse 12.8.2 navigation on 2026-11-01 against the live public
site (typography slice already deployed). #5235 recorded before/after medians for
the initial token rollout; this closeout re-confirms accessibility stays at 100
on the three test pages.

| Page | View | Perf | A11y | BP | SEO | FCP | LCP | TBT | CLS |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Home | Mobile | 98 | 100 | 100 | 100 | 1.7 s | 2.1 s | 20 ms | 0.021 |
| Theory Part 1 | Mobile | 89 | 100 | 100 | 100 | 1.8 s | 2.6 s | 310 ms | 0.057 |
| Physics of Golf ch03 | Mobile | 82 | 100 | 100 | 100 | 2.8 s | 3.4 s | 250 ms | 0.046 |
| Home | Desktop | 100 | 100 | 100 | 100 | 0.4 s | 0.4 s | 0 ms | 0.041 |
| Theory Part 1 | Desktop | 100 | 100 | 100 | 100 | 0.6 s | 0.6 s | 0 ms | 0.025 |
| Physics of Golf ch03 | Desktop | 99 | 100 | 100 | 100 | 0.6 s | 0.7 s | 0 ms | 0.043 |

## 1440px reading measure follow-up

The script requires the Python `websocket-client` package and headless Chrome.
Start Chrome on port 9227 with
`google-chrome --headless=new --no-sandbox --remote-debugging-port=9227 --user-data-dir=/tmp/ad5166-measure --no-first-run about:blank`, then run
`python3 docs/ux-evidence/5166/measure_reading_widths.py --chrome-port 9227`.
The script measures the five live pages below at 1440×900 after
`document.fonts.ready`, injects the 55ch rules read directly from the current
checkout, and prints the raw per-paragraph and full-line counts as JSON. It
excludes paragraphs of 200 characters or fewer and text inside code, math,
superscripts, or `aria-hidden` elements. It counts Unicode code points from
`Range` rectangles grouped by line top (rounded to 0.1px), excludes each
paragraph's final visual line, and reports medians over full lines and each
paragraph's longest full line. This is a one-run live-DOM measurement with exact
source CSS injected; it is not a local Quarto branch render, an independent
replication, or a Lighthouse benchmark. Screenshots above show the same live-DOM
with the scoped source CSS injected.

| Page | Paragraphs | 61ch full lines / median / longest median | Current scoped rules full lines / median / longest median | Hypothetical global 56ch full lines / median / longest median |
|---|---:|---:|---:|---:|
| Theory Part 1 | 58 | 337 / 73 / 78 | 371 / 66 / 70.5 | 367 / 67 / 71 |
| ch03 | 47 | 197 / 74 / 77 | 217 / 66 / 70 | 214 / 68 / 71 |
| Core Theses registry | 24 | 133 / 74 / 78 | 133 / 74 / 78 | 151 / 67 / 71.5 |
| Proximal-distal journey | 1,278 | 7,644 / 73 / 78 | 7,644 / 73 / 78 | 8,292 / 67 / 71 |
| Falsification atlas | 18 | 150 / 70 / 78 | 150 / 70 / 78 | 163 / 64 / 72 |

The two requested pages' full-line medians are 66 and 66 under the scoped
55ch rules, inside the 65–71 band; their longest-line medians are 70.5 and 70.
The two overrides match canonical page URLs, so title edits do not disable them.
The other representative pages remain at the shared 61ch in this PR. The
hypothetical global 56ch column is a scope comparison only: it would move the
atlas median to 64 and would put the shared token below the existing 60ch
reading-comfort floor. No threshold or scientific content is changed.
