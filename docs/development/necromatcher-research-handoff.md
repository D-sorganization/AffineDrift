# Historical-Player Research Handoff

Issue: AffineDrift #4828. This adapter admits sanitized JSON for **local research
review only**. It does not publish a page, attest a registry entry, redistribute
footage, or change scientific acceptance. The qualified markerless mocap v1
projection and authoritative research-release registry remain separate.

## Public Boundary

`src.affine_control.historical_research` exposes `validate_research_schema`, `admit_package`,
`render_research_page`, `HistoricalResearchConsumer`, `ResearchImportPins`, and
immutable typed package/record/clock/identity records. The static contract is
`schemas/historical-player-research-v1.schema.json`, identified by
`urn:upstreamdrift:historical-player-research:v1`. The URN identifies a contract;
it is not an asserted hosted endpoint.
`validate_research_schema(schema_bytes)` checks fetched schema semantics against
the canonical contract. `admit_package(payload, expected_sha256, expected_bytes,
source_commit)` has four arguments and always validates payloads with the
mandatory canonical Draft schema; callers cannot replace admission semantics.

The provider exports plain JSON with `schema` equal to
`upstreamdrift/historical-player-research/v1`. Every unknown or additional field
fails admission. Records are generic: adding a player requires another record,
not another renderer or provider adapter. Stable fit IDs must be unique; player
names and swing ownership must not contradict their IDs.

## Provider Contract

Top-level fields are `schema`, `provider`, `distribution`, and `records`.
`provider.repository` is `D-sorganization/UpstreamDrift`; `source_commit` is a
40-character lowercase Git hash for the export implementation. Its `source_url`
is the exact repository tree reference for that revision. This code reference
is **not** a claim that the package has been published at that revision.
Distribution is `local_research_only`, `not_authorized_for_publication`, with
`contains_original_media: false`.

Every record contains:

- Stable `player_id`, `player_name`, `swing_id`, and `fit_id`.
- A separate `producer_commit` for the numerical computation.
- Plain 64-character SHA-256 hashes for actual downloaded source bytes, capture
  JSON, model, fit, and input evidence. A source-video hash is not a capture hash.
- `source_clock.start` and `.end` as `{numerator, denominator}` rational seconds;
  `origin: video_presentation_time`, positive `frame_count`, and
  `physical_time: unknown`. Fractions must increase and start at or after zero.
- `execution_status: succeeded`, `qualification: monocular_research_hypothesis`,
  `scientific_acceptance: rejected`, `optimizer_converged: false`, and
  `continuous_certified: false`. v1 admits this research cohort only.
- Distinct finite-target IDs and boolean outcomes. Passing every sampled target
  cannot promote acceptance, continuous certification, or release rights.
- Finite nonnegative training, held-out, and dense RMS in pixels; sampled grip
  gap/penetration in millimeters and grip angle in degrees. `metric_definition`
  must describe the confidence-weighted Euclidean landmark RMS, including all
  positive image observations and unknown-visibility weight 0.5; the explicit
  `unknown_visibility_weight` field is fixed to 0.5. Finite geometric targets
  are numerical research criteria, not accepted physical tolerances.
- Rights status (`unresolved`, `restricted`, or `documented_local_use`) with
  distribution `not_authorized`, and explicit nonempty limitations.
- Optional strictly positive `image_counts` for source/training frames and
  dense/training observations. These counts do not imply extra image evidence.

No source pixels, person media, machine paths, optimizer arrays, private runtime
objects, or Upstream implementation imports cross this boundary. Unqualified
camera/anatomy, unknown physical timing, incomplete club geometry, and sampled
nonlinear constraints belong in limitations. The consumer checks syntax,
identity, pins, and declared states; it cannot independently certify biomechanics
from this small package or verify unavailable original media.

## Acquisition and Local Preview Procedure

1. Obtain and review the sanitized manifest and the exact supported schema.
   Independently record SHA-256 **and byte size for each file**, along with the
   provider/export revision. Do not substitute the numerical producer revision.
2. Construct existing public `ImportRequest` and `ConsumerPolicy` records for
   the reviewed logical addresses. For an unpublished bundle, use existing
   `DirectoryTransport` to map those immutable logical addresses to local JSON
   files. Logical transport addresses do not establish actual public availability.
3. Build `ResearchImportPins(request, manifest_bytes, schema_bytes)` and
   `HistoricalResearchConsumer(policy, transport, storage_root)`. The policy
   must use the research URN and exact Upstream repository boundary.
4. Call `inspect(pins)` first. This performs bounded JSON/schema/hash/size/source
   validation without storage writes. Redirects, altered schema contracts,
   malformed/duplicate JSON, nonfinite values, and local paths fail closed.
5. Call `render_research_page(package)` for deterministic generic QMD. It
   rechecks the admitted immutable bytes and escapes labels and limitations.
   Write the returned string only to an explicitly chosen **local** preview
   workspace; Quarto rendering does not authorize public deployment.
6. If retaining the review, call `install(pins)`. Existing public `SnapshotStore`
   provides atomic/idempotent storage under the distinct child namespace
   `historical-player-research-v1`. The shared companion lock format is a
   **storage envelope**, with `publication_state: draft`; it is not a companion
   scientific manifest or an authoritative research-release attestation.
7. `recall()` verifies stored bytes, draft state, provider, immutable transport
   identity, supported schema, and package semantics before rendering again.
   Symlinks and Windows junctions in storage ancestry are refused.

A conflicting immutable pin cannot silently replace the active record. Use a
new explicit local storage root for a separately reviewed package. Preserve
previous evidence; this facade intentionally exposes no replacement or public
publish operation. Any hash, size, schema, source, or stored metadata failure
requires re-review of candidate evidence rather than status repair/promotion.

## Turnover and Validation

Production changes are confined to the new `historical_research` package and
static schema. Transport, storage, qualified mocap projections, evidence
projectors, public routes, and authoritative release registries are reused or
left in their existing scopes. In particular the companion evidence projector
that assigns qualified simulation is not used here.

Red-first regressions cover rejected target passes, status/rights promotion,
exact source/hash/byte pins, rational source timing, finite metrics, malformed
JSON, schema substitution, contradictory identities, third-player generation,
label injection, redirected/tampered transport, atomic idempotence, conflicting
pins, stored-byte mutation, and foreign/mutable recall metadata. Run:

```powershell
python3 -X utf8 -m pytest tests/test_historical_research_handoff.py tests/test_historical_research_admission_regressions.py -q --cov=src.affine_control.historical_research --cov-report=term-missing
python3 -m mypy src/affine_control/historical_research
python3 -m ruff check src/affine_control/historical_research tests/test_historical_research_handoff.py
python3 -m black --check --line-length 100 src/affine_control/historical_research tests/test_historical_research_handoff.py
```

After the output-preserving budget refactor, the focused suite has 42 passing
cases and 95.35% module coverage,
above the repository's unchanged 75% floor. Existing qualified mocap,
companion consumer/storage, and research-readiness regression suites also pass
in the focused integration selection. Synthetic contract tests alone do not establish actual package admission or
publication. The separate actual local admission and browser receipts below
record the subsequent provider/consumer execution without public publication.

Independent review reproduced installation through a snapshot-parent junction
and contradictory optional observation counts. Five red regressions failed
before the fixes; the additional six-case regression file includes valid partial
training coverage. Installation now checks the exact snapshot destination and
all its ancestors before acquisition or writes. Optional counts must match the
clock's source-frame count, have training frames no greater than source frames,
and have training observations no greater than dense observations. These checks
do not invent an anatomical landmark-capacity bound.

Use UTF-8 mode for Windows validation (`python3 -X utf8`): a full baseline run
with the host's cp1252 default failed while an unchanged minifier test wrote
Unicode JavaScript to a temporary file. Its seven cases pass in UTF-8 mode.
This environment setting does not skip or weaken the offline suite.

## Full Offline Validation and Windows Runtime

The SDK-first offline run before the final budget refactor passed **6,681 tests**,
with **26 skipped**,
**187 deselected by the existing marker policy**, and **61 warnings**, in
**795.45 seconds**. The host was Python **3.13.5**; the repository's configured
Python target remains **3.12**. This host result does not claim a separate
Python 3.12 run. Post-refactor consumer coverage is **95.35% across 42 passing cases**; the
earlier full run did not replace that focused coverage measurement. The final clean
SDK-first full run after the budget refactor passed **6,685 tests**, with
**26 skipped**, **187 existing-marker deselected**, **61 warnings**, in
**600.28 seconds**. It retained the same runtime controls and offline policy.

The final unchanged SDK-first full offline coverage retry passed 6,685 tests, with26 skips,187 existing-marker deselections and61 warnings in1,044.94 seconds; full src coverage was93.51%, exceeding the configured75% floor. Logs are affine-historical-full-suite-final-coverage-retry.log and affine-necromatcher-final-coverage-retry.xml in the local temporary directory. The first coverage attempt timed out in unchanged wheel packaging and is retained as failed; the untouched four packaging tests passed on retry in39.82 seconds before the unchanged full retry passed. Coverage reports missing temporary installed-wheel-copy source warnings; these are disclosed, not treated as separate Python3.12 validation. HostPython3.13.5, UTF-8, MuJoCo3.3.4 SDK-first import, single BLAS threads and the exact existing offline marker policy remain unchanged.

The earlier cp1252 baseline stopped at an unchanged Unicode minifier fixture.
After UTF-8 mode was enabled, a later run reached 4,614 passing tests before a
late MuJoCo import produced a Windows access-violation diagnostic and
`WinError 1114` DLL initialization failure. That attempt is retained as failed,
not counted as a full-suite pass. The successful fresh process imported the
installed **MuJoCo 3.3.4 before pytest** and set UTF-8 and BLAS thread controls:

```powershell
$env:PYTHONUTF8='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
python3 -X utf8 "$env:TEMP/affine-historical-sdk-first-validation.py" `
  > "$env:TEMP/affine-historical-full-suite-sdk-first.log" 2>&1
```

The reviewed temporary driver used the following invocation from the Affine
worktree, preserving the repository's exact offline marker expression:

```python
import mujoco
import pytest

raise SystemExit(pytest.main([
    '-x', '--timeout=60', '-ra', '--override-ini',
    "addopts=-p no:xvfb -m 'not slow and not live_simulation and not e2e and not requires_network and not content_lint'",
]))
```

The actual driver was `affine-historical-sdk-first-validation.py`; its output
was retained in `affine-historical-full-suite-sdk-first.log` in the local
Windows temporary directory. SDK preloading and environment controls did not
alter assertions, add deselections, remove SDK tests or weaken the offline
policy. The 26 skips and 187 deselections remain explicit limitations of that
lane. Five reproduced junction/count failures were fixed through red/green
regressions before this run; partial training coverage remains admissible.

These are implementation and regression results. The separate actual frozen provider package and consumer admission, atomic
install/recall and local QMD preview are recorded below. Neither test success
nor local rendering authorizes footage redistribution, a public route or
scientific qualification.

## Actual Local Admission and Browser Review

The local workflow inspected the published Upstream package from
`6654881b0788c77620a0afb8a9a6763f3ee1ccb9` without writes, installed a separate
exclusive draft snapshot, reinstalled idempotently, recalled exact bytes and
reproduced deterministic QMD. Manifest pins remain 6,849 bytes and
`757a644c5408e4f5fc54904bd2918290f2c3af7d77d9a3b4045420334f1bc93d`;
schema pins remain 8,745 bytes and
`a194bf0c8145e417262f460c9bc4ea817b73d491b8468be7dfcd17a88334cb30`.

The actual receipt `local-admission-preview-receipt.json` is 21,943 bytes,
SHA-256 `ccf4615f4eb3d51a51b6b3a1af98b9bfd92abda4683be20b26744ff6c67136c2`.
Its input/source/driver/authoritative-registry brackets were unchanged. Consumer
checkout base `29472661de971899bfb7cdc4a3f92b3e9eee19aa` is distinct from tested
working-tree fingerprint
`4c712713d0aa4dde9afc34876a3b73a0074bbe04515b23215cca9f410cc6af09`;
the consumer changes are not claimed committed at that base.

Quarto 1.8.26 rendered a standalone local HTML preview with `--no-execute`,
exit code zero. QMD: 4,850 bytes,
`811e52a380d275d119525bc9f7b013711c8cf8f2f33fe585ec60e268c48ace19`;
HTML: 26,172 bytes,
`079655676dbc588731a9c82c195e0e24db922eec11b4e5f35c7124e39340abe8`.
Separate actual browser evidence is `browser-review-receipt.json`, SHA-256
`f39ffed5532bbc8700b32e50053abf4e0dafd335ad838c6b255130d3c6edadef`.
Accessibility-tree and three screenshot checks inspected the local-research
title, both rejected statuses, metrics, Tiger's finite ground failure and
limitations. No clipping or overlap was found at the reviewed default
1234-by-712 viewport. This is bounded programmatic browser evidence, not manual
user acceptance or complete accessibility qualification.

The actual package cohort is **Hogan V12 and Tiger V14**, not subsequent V15
research. No optimizer, original-media import, authoritative registry mutation,
public route or deployment occurred. Rights remain unresolved and all records
remain rejected/nonconverged. The local receipts and rendered files reside in
the exclusive Desktop folder `Necromatcher Affine Local Review 2026-10-02`;
consumer commit and reviewed PR delivery remain separate workflow steps. The
final post-budget-refactor full-suite result is recorded below.

The first post-budget-refactor full rerun stopped after 4,638 passing tests on
one repository-root hygiene check: an earlier full suite had generated ignored
`build/`, `dist/` and `affinedrift.egg-info` packaging scratch. The owning
workflow preserved those bytes outside the workspace rather than deleting them
or changing tests/source. The preservation receipt has SHA-256
`962d1dc8de24bf2f01c4320542a1d1cc1ef4c147c7478a5e0cb25e45eeb4e308`;
all six root-hygiene cases then passed. The subsequent clean SDK-first full
rerun retained the same offline filtering and passed **6,685 tests**, with
**26 skipped**, **187 existing-marker deselected**, **61 warnings**, in
**600.28 seconds**. Exact output is retained in
`affine-historical-full-suite-budget-clean.log` in the local temporary
directory. The failed 4,638-pass attempt is not counted as a completed
full-suite pass. Host Python 3.13.5 remains distinct from configured 3.12; no
separate Python 3.12 validation is claimed.
