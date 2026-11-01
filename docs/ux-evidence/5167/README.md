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
page scanned once using `origin/main` CSS and once using the PR CSS. Tags
included WCAG 2.0, 2.1, and 2.2 A/AA, including the 2.2 target-size rule.

| Page | Viewport | Main passes / violations | PR passes / violations |
| --- | --- | ---: | ---: |
| Home | 375×812 | 28 / 0 | 28 / 0 |
| Home | 1440×900 | 27 / 0 | 27 / 0 |
| Theory Part 1 | 375×812 | 42 / 0 | 42 / 0 |
| Theory Part 1 | 1440×900 | 41 / 0 | 41 / 0 |
| Physics of Golf, ch03 | 375×812 | 29 / 0 | 29 / 0 |
| Physics of Golf, ch03 | 1440×900 | 29 / 0 | 29 / 0 |

## Lighthouse before/after metrics

Captured 2026-10-31 with Lighthouse 12.8.2 and Chrome 144.0.7559.96. Each row
is the median of three navigation runs. The same live HTML and assets were
served through a loopback proxy for both conditions; the after response adds
the exact `css/components/header-nav.css` from this PR as a stylesheet at the
end of `<head>`. Mobile uses Lighthouse's default mobile preset; desktop uses
`--preset=desktop`. Category scores are percentages. FCP/LCP/TBT/CLS, transfer
size (`total-byte-weight`), and request count are Lighthouse audit values.

| Page | View | Slice | Perf | A11y | BP | SEO | FCP | LCP | TBT | CLS | Transfer | Requests |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Home | Mobile | Before | 70 | 100 | 100 | 100 | 3.4 s | 5.1 s | 99 ms | 0.048 | 384.2 KiB | 44 |
| Home | Mobile | After | 70 | 100 | 100 | 100 | 3.4 s | 5.2 s | 47 ms | 0.013 | 386.1 KiB | 45 |
| Theory Part 1 | Mobile | Before | 48 | 100 | 100 | 100 | 5.4 s | 8.9 s | 370 ms | 0.127 | 1041.5 KiB | 65 |
| Theory Part 1 | Mobile | After | 50 | 100 | 100 | 100 | 5.6 s | 7.0 s | 412 ms | 0.066 | 1043.1 KiB | 66 |
| Physics of Golf ch03 | Mobile | Before | 50 | 100 | 100 | 100 | 4.8 s | 8.2 s | 320 ms | 0.046 | 945.5 KiB | 53 |
| Physics of Golf ch03 | Mobile | After | 51 | 100 | 100 | 100 | 4.9 s | 8.3 s | 386 ms | 0.079 | 947.6 KiB | 54 |
| Home | Desktop | Before | 97 | 100 | 100 | 100 | 0.9 s | 1.0 s | 0 ms | 0.041 | 384.2 KiB | 43 |
| Home | Desktop | After | 96 | 100 | 100 | 100 | 1.0 s | 1.1 s | 0 ms | 0.041 | 386.1 KiB | 44 |
| Theory Part 1 | Desktop | Before | 96 | 100 | 100 | 100 | 1.0 s | 1.1 s | 23 ms | 0.026 | 1041.1 KiB | 64 |
| Theory Part 1 | Desktop | After | 95 | 100 | 100 | 100 | 1.1 s | 1.1 s | 16 ms | 0.026 | 1043.1 KiB | 65 |
| Physics of Golf ch03 | Desktop | Before | 94 | 100 | 100 | 100 | 1.1 s | 1.1 s | 13 ms | 0.043 | 945.5 KiB | 52 |
| Physics of Golf ch03 | Desktop | After | 95 | 100 | 100 | 100 | 1.1 s | 1.1 s | 25 ms | 0.043 | 947.4 KiB | 53 |

The mobile performance values varied between runs, especially on the two
article pages. These are recorded measurements, not a claim that this CSS
change caused a performance improvement. The after condition adds one request
for the PR stylesheet; the remaining resource counts and sizes are otherwise
close to the baseline.
