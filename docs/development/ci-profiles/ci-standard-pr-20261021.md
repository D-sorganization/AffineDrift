# CI Standard Pull Request Job Timing Profile — 2026-10-21

This read-only profile supports AffineDrift #5115. It records historical timing for the successful `CI Standard` pull-request workflow in the bounded window below. It identifies the long job and observed slow steps; it does not establish why they are slow or validate an optimization.

## Scope and Window

- Repository: `D-sorganization/AffineDrift`.
- Window: 2026-10-07 00:00:00 UTC through 2026-10-21 07:06:48 UTC, the saved RM2216 snapshot's effective end time.
- Workflow: `.github/workflows/ci-standard.yml`, named `CI Standard`; event `pull_request`; completed successful runs; first attempt only.
- The workflow-runs endpoint returned 113 unique runs in two pages (100 + 13). The summary recomputed from those `updated_at - run_started_at` values matched the saved RM2216 aggregate exactly: p50 597 s, p90 4,848.2 s, mean 1,991.681 s, minimum 338 s, maximum 5,164 s.
- Of those 113 runs, 41 had a workflow proxy of at least 52 minutes and 14 at least 80 minutes.

## Job Sample and Method

The job API budget was 50 runs. All 42 runs with a workflow proxy of at least 30 minutes were selected, plus 8 time-of-day controls (two evenly spaced runs in each canonical UTC bucket: night, morning, afternoon, evening). This is a tail-enriched sample, not a random sample. All 41 runs at or above 52 minutes and all 14 at or above 80 minutes are represented in the job sample.

One `filter=all`, page-1 request (`per_page=100`) was made for each selected run. All 50 job lists were complete: 400 rows, no run/attempt mismatches, no missing timing fields, and no pagination gaps. Every sampled job was `completed/success` and carried the historical `ubuntu-latest` label. Run-list metadata did not include labels, so no label stratification is claimed. These historical labels do not describe current runner capacity.

Queue duration is `max(0, started_at - created_at)` and can include `needs:` dependency waiting. Execution duration is `max(0, completed_at - started_at)`. Percentiles use the canonical inclusive-linear method. Per-run job wall time is `max(job completed_at) - min(job created_at)`; parallel jobs are not summed. The workflow `updated_at - run_started_at` value is a completion proxy, not pre-run queue time.

## Run-Level Comparison

| Measure | Tail-Enriched Job Sample (n=50) | All Successful First-Attempt PR Runs In Window (n=113) |
| --- | ---: | ---: |
| Workflow `updated_at - run_started_at`, p50 | 4,557 s | 597 s |
| Workflow proxy, p90 | 5,028.7 s | 4,848.2 s |
| Workflow proxy, maximum | 5,164 s | 5,164 s |
| First job created to last job completed, p50 | 4,523.5 s | Not collected for all runs |
| First job created to last job completed, p90 | 5,025 s | Not collected for all runs |
| First job created to last job completed, maximum | 5,163 s | Not collected for all runs |
| Workflow proxy minus job wall, p50 / p90 / maximum | 2 s / 27.2 s / 98 s | Not collected for all runs |

The workflow proxy and measured job wall track closely in the 50 selected runs. This supports attributing the long duration to work inside jobs rather than a large gap between workflow start and job execution in this sample.

## Per-Job Timing

Each selected run contributes one row per job name. The 50-run sample includes all long-tail runs and 8 controls; do not interpret these summaries as an unbiased population estimate.

| Job | Rows | Queue p50 / p90 | Execute p50 / p90 | Execute Mean | Execute Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| `e2e-tests` | 50 | 4 / 5 s | 4,503 / 5,007.7 s | 3,721.7 s | 5,144 s |
| `js-tests` | 50 | 4 / 5 s | 27 / 31 s | 27.28 s | 33 s |
| `pick-runner` | 50 | 4 / 5.1 s | 3 / 4 s | 3.2 s | 6 s |
| `quality-gate` | 50 | 4 / 6 s | 3 / 4 s | 2.94 s | 4 s |
| `Reject hosted runner routing` | 50 | 4 / 5.1 s | 3 / 4 s | 3.2 s | 9 s |
| `Static checks` | 50 | 4 / 5 s | 112.5 / 123.3 s | 108.64 s | 159 s |
| `tests (3.12)` | 50 | 4 / 5 s | 557.5 / 582.1 s | 513.68 s | 595 s |
| `website-lint` | 50 | 4 / 5 s | 18 / 21.1 s | 18.54 s | 32 s |

The `e2e-tests` job dominates this sample. Its median execution is 75 minutes; its p90 is about 83 minutes. Its median queue duration is 4 seconds. This explains the observed 52–80+ minute workflow durations in the selected history, but does not explain the internal cause of the E2E runtime.

## Step-Level Examples

These three successful first-attempt tail jobs have saved step-level timing records. The durations are individual step intervals, not a sum across parallel jobs.

| Run ID | E2E Job ID | Build Site For E2E | Playwright E2E Suite | axe-core On Every Route |
| ---: | ---: | ---: | ---: | ---: |
| 39293010347 | 118198291888 | 2,951 s | 377 s | 1,533 s |
| 39228175880 | 117979538590 | 2,981 s | 249 s | 1,578 s |
| 38229073934 | 114743807783 | 2,657 s | 240 s | 1,429 s |

In these three cases, the full-site build and all-route accessibility scan take much longer than the browser suite. This is an investigation lead, not proof of a root cause or an optimization result. Issue #5116 remains separate and unimplemented; this profile does not reduce coverage or alter workflow timeouts or gates.

## Reproducibility and Source

The [companion CSV](ci-standard-pr-20261021.csv) contains the 400 selected job rows. The [provenance JSON](ci-standard-pr-20261021-provenance.json) records the 113 candidate IDs, exact selection rule, request caps, source hashes, per-run comparisons, and timing semantics.

Metric definitions and sampling buckets are pinned to [Repository_Management commit `820402ec16afac89e30f6674252ad9237352b8b4`](https://github.com/D-sorganization/Repository_Management/tree/820402ec16afac89e30f6674252ad9237352b8b4), specifically [`metrics.py`](https://github.com/D-sorganization/Repository_Management/blob/820402ec16afac89e30f6674252ad9237352b8b4/shared_scripts/ci_fleet_baseline/metrics.py) and [`sampling.py`](https://github.com/D-sorganization/Repository_Management/blob/820402ec16afac89e30f6674252ad9237352b8b4/shared_scripts/ci_fleet_baseline/sampling.py). The run-level summary matches the saved canonical RM2216 snapshot exactly.
