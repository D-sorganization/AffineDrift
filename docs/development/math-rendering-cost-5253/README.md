# Repeated Math Rendering Baseline for #5253

Measurement-only follow-up to #5486. Refs #5253; the issue remains open.
Three independent public-site captures were made on DeskComputer on November 6,
2026, with Lighthouse 12.6.1 and Playwright Chromium 1248, mobile 390 by 844,
device scale factor 3 and Lighthouse's default simulated throttling.
The requested URL redirected to `https://www.affinedrift.com/articles/theory-part1.html`.

## Evidence and Limits

| Metric | Minimum | Median | Maximum |
| --- | ---: | ---: | ---: |
| Performance Score | 0.55 | 0.56 | 0.59 |
| LCP (ms) | 3298 | 3342 | 3414 |
| Total Blocking Time (ms) | 2142 | 2335 | 2541 |
| Math Script Boot-Up (ms) | 2394 | 2465 | 2615 |
| Math Scripting (ms) | 1802 | 1837 | 1982 |
| Math Transfer (bytes) | 207277 | 260209 | 260330 |

All three processes returned zero and produced finite required metrics. All also
emitted `LanternError: Invalid dependency graph created, cycle detected` to stderr.
These are warning-bearing diagnostic captures, not a clean Lighthouse qualification.
The raw reports retain every audit, including errored auxiliary insights; the
summary does not silently replace failed required audits with zero.

The public deployment's source SHA was not established. The code review base was
`6ee9c59f89624ab6f58f3b566119f9ae829697ed`; that is **not** asserted as the deployed
page revision. Captures used the live site rather than a pinned local render.
They cannot establish a performance change from #5486's single localhost report,
isolate MathJax as a cause, or predict savings from removing it. Other fleet
processes and public network conditions were not controlled. The three runs show
observed spread on this host only.

## Reproduction

Use Lighthouse 12.6.1 and an isolated headless Chromium. Set `CHROME_PATH` to the
chosen browser executable, then run this command three times with distinct output
paths (`baseline-1.json`, `baseline-2.json`, `baseline-3.json`):

```sh
npx --yes lighthouse@12.6.1 https://affinedrift.com/articles/theory-part1.html \
  --only-categories=performance --form-factor=mobile \
  --screenEmulation.width=390 --screenEmulation.height=844 \
  --screenEmulation.deviceScaleFactor=3 \
  --chrome-flags="--headless=new --disable-gpu" \
  --output=json --output-path=baseline-1.json --quiet
python scripts/lighthouse_math_cost.py baseline-1.json baseline-2.json baseline-3.json
```

The original one-report command remains supported. Three-report mode requires
matching requested/final URLs, version and settings, distinct fetch times, and
finite successful required audits. It reports min/median/max and per-run values.

`baseline-summary.json` records the settings, run timestamps and SHA256 digests.
The three deterministic gzip files contain the original JSON bytes. Decompress
with Python's `gzip.decompress` and verify both compressed and raw hashes before
recomputing the summary. No screenshots or raw reports are fabricated fixtures.

## Remaining Acceptance

The branch-local SSR prototype, three prototype runs, build-time delta and pinned
local-build comparison are still outstanding. A build-time renderer dependency
remains an owner decision. This slice changes no dependencies, production math
configuration, workflows, article content, publication state or existing holds.
