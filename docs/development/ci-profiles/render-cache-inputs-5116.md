# Render Cache Input Filtering and Evaluation

This change addresses AffineDrift #5116 using the job profile from #5115. It
reduces unnecessary invalidation of the existing E2E render cache. It does not
add jobs or change runner routing, job timeouts, required checks, browser routes,
accessibility scans, or publication behavior.

Editing this workflow also required correcting seven pre-existing ShellCheck
findings reproduced on the unchanged base: quote three GitHub path-file
redirects, log three existing retry counters, and read the existing numeric
test-count baseline through its shell environment variable. Retry counts and
the test-count threshold remain unchanged.

## Evidence and Scope

The profile's tail-enriched sample identified `e2e-tests` as the dominant job.
Three saved step examples recorded full renders taking 2,657–2,981 seconds. Those
examples motivate investigating reuse; they do not establish a population cache
hit rate or predict the improvement from this change.

The previous key hashes tracked Git index records while excluding `tests/`,
`.github/`, and `docs/development/`. It still includes change-note fragments.
An index-equivalent comparison of main `4d75d5556689a5014f703c4c9c66879b44bb6f28`
and profile source `b4521cff92169c8486358d2b59261df525af16f4` found different old
keys. Excluding `changes/` made their remaining payload identical. A bounded
cache inventory at the same observation contained the old main key and no old
profile-source main cache. This establishes avoidable input invalidation; it
does not prove which cache a running merge-group job restored.

The new key additionally excludes root `SPEC.md` and `changes/`. The current
Quarto render and resource declarations do not consume these authoring records.
All other tracked inputs remain in the existing broad fingerprint, including
Quarto configuration, QMD, Lua filters, includes, CSS, data, schemas, dependency
locks, the pinned Quarto version, and the cache-key helper itself. Git blob IDs,
file modes, and paths remain significant. Invalid or incomplete index records
fail the key step instead of emitting a usable key.

The `quarto-render-v3-` prefix separates this contract from old cache entries.
Expect a cold render when no exact v3 key is available. Restore remains exact
only, with a full render on a miss. Existing post-restore checks and generation
of revision-bound public-site metadata remain mandatory. Website Deploy retains
its full render and existing publication checks.

## Dependency Maintenance

Tests check the current render/resource declarations and representative input
changes. They cannot prove the dependency closure of future content or runtime
code. A change that makes Quarto consume `SPEC.md` or `changes/` must remove the
affected exclusion or explicitly incorporate that dependency into the key.
One cold render after changing a QMD file would not make subsequent excluded
metadata edits safe. Keep this review requirement with the cache contract.

## Evaluation Window

Observe normal first-attempt `CI Standard` runs for seven calendar days after
the merge, extending observation until ten eligible completed runs are recorded
if necessary. Record the merge time, source and merge-group SHAs, event, runner
labels, exact cache key, restore result, whether full rendering ran, E2E step
times, job conclusion, and routing/quality-gate conclusions. Count PR,
merge-group, and main runs separately. Keep cold and restored runs separate;
record failures and cancellations instead of silently dropping them.

Use naturally occurring metadata-only changes and render-input changes. Do not
create benchmark PRs, trigger duplicate workflows, or rerun successful jobs for
this evaluation. If no qualifying reuse occurs, report insufficient evidence
and continue observing. Never report a hit-rate improvement from cache inventory
counts or compare this cohort's percentiles directly with the tail-enriched
historical sample as a causal estimate.

Acceptance of the mechanism requires a naturally observed exact-key reuse for
unchanged render inputs, a different key for a changed render input, and passing
required checks including `Reject hosted runner routing`. Report measured
runtime differences only with their event, runner, and cold/restore context.
The first successful source check alone does not complete this observation.

## Rollback Triggers and Procedure

Open a focused revert PR immediately if a changed render input reuses a key, a
restored site contains stale content, cache-key computation breaks an otherwise
valid checkout, or required routing/render/publication contracts regress because
of this change. Preserve evidence and allow current jobs to finish normally.
Do not weaken checks, raise timeouts, or change runner capacity as a workaround.

Revert the helper, its workflow integration, and corresponding tests together
through the protected merge path. The prior v2 namespace then resumes normal
behavior. No cache deletion or live dashboard configuration change is needed.
Runtime variation without a demonstrated regression is an observation to
investigate, not a reason to claim success or force a rollback.
