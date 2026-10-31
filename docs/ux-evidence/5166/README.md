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

## 1440px reading measure follow-up

Measured with headless Chrome 144 at 1440×900 on the live page DOM, after
`document.fonts.ready`, with CSS from PR base head
`9843e018e7c42b523bc42693f81254e7a63059ea` and the page-scoped 55ch overrides
injected. The shared default token remains 61ch. The sample includes paragraphs
over 200 characters, excludes code, math, superscripts, and each paragraph's
last (short) line, then counts rendered characters grouped by line box. This is
a one-run CSS/layout spot check, not a full Quarto branch render or Lighthouse
benchmark.

| Page | Effective width | Paragraphs / full lines | Median characters per full line | Median longest line per paragraph |
|---|---:|---:|---:|---:|
| Theory Part 1, before | 61ch | 62 / 346 | 74 | 78 |
| Theory Part 1, after | 55ch | 62 / 382 | 67 | 71 |
| ch03, before | 61ch | 47 / 198 | 74 | 79 |
| ch03, after | 55ch | 47 / 216 | 67 | 70 |

Both after medians are within the requested 65–71 character band. Existing
screenshots above predate this width correction and should not be treated as
screenshots of the updated 55ch layout.
