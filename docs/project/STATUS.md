# AffineDrift Project Status

Steward projection generated on 2026-11-16 from
[CHARTER.md](CHARTER.md), the published [catalog](../development/planning/catalog.json),
merged and open PRs, open issues, and CI state on `main`.
This is the impact/acoustics slice of the charter, not a whole-repository progress assessment.

Sources verified 2026-11-16: issue #4253 `CLOSED` (completed, 2026-10-09T18:05:39Z);
main CI **green** (latest completed `CI Standard`, `Deploy Website`, `Seed Quarto E2E
Render Cache`, `Performance Benchmarks` and `Cross-Browser Nightly` runs on `main` succeeded;
the 12:09Z push run was still in flight); 28 open PRs (13 opened today, 15 older,
of which 13 carry `do-not-merge`); 58 open issues; 242 PRs merged since the 2026-11-03
pass. Planning catalog validates (`python3 -m shared_scripts.deferred_planning
docs/development/planning` → 1 plan, valid); no v2 `docs/planning/deferred-validation.json`
exists, so there is a single authority.

## Progress

| ID | Feature | Status | Progress | Last Change |
| --- | --- | --- | --- | --- |
| IA-THEORY | Source review and qualified numerical synthesis | done | Tracking epic #4253 closed as completed 2026-10-09; the charter status now matches that closure | 2026-10-09 |
| DV-4253 | Physical and perceptual evidence synthesis | parked | Awaiting verified prerequisites; [catalog.json](../development/planning/catalog.json) unchanged since 2026-09-22; Board proposal submitted this pass | 2026-11-16 |

## Recent Activity (since 2026-11-03)

242 PRs merged in 13 days. None touches DV-4253's prerequisites. Most of the work falls
outside this charter slice: it closes out the 2026-11-10 technical-accuracy and
UpstreamDrift knowledge-gap epic (#5587) and its children:

- **#5757 / #5751**: proximal-distal monograph physics and evidence contracts (#5610, #5611).
- **#5755 / #5726 / #5662**: agent-readiness entry point, `llms.txt`, symbol registry v2 (#5596).
- **#5750**: conventions agent entry and canonical-v2 parity gate (#5619).
- **#5745 / #5735**: motion-control stale-companion check and Bosch alignment (#5615).
- **#5687**: ZTCF/superposition figure provenance gate (#5590).
- **#5654 / #5670 / #5732**: UpstreamDrift protocol, learning and ZVCF documentation (#5620, #5625, #5626).
- **#5651 / #5724 / #5742**: Physics of Golf content corrections and locks (#5598).
- **#5681 / #5722**: Geometry of Motion notation harmonisation (#5602, #5592).
- **#5719**: correction-authority peak bound and norm provenance (#5567).

## Stuck (72-Hour PR Rule)

- **#5579** (Alpha War Study 6, #5463 slice 2) and **#5572** (correction-authority note,
  #5565): opened 2026-11-10, merge state `CLEAN`, no failing checks, auto-merge **not armed**.
  CI is not the blocker. The owning lane must arm or close these PRs. The steward does not
  change another session's PR state.
- **#5562, #5197, #5196, #5194, #5158** (non-draft) and **#5480–#5489, #5327** (drafts):
  under the `do-not-merge` hold for 7–23 days. They wait on the Alpha War owner sign-off
  (#5403) and on article decisions; the hold is intentional, so these are not CI failures.

## Blockers

- DV-4253 lacks the qualified downstream physical/radiation and controlled blinded
  perception evidence that the owner plan requires. Numerical work does not clear
  these gates.

## Decisions Needed

- **(BOARD PROPOSAL SUBMITTED 2026-11-16; 54 days old)** (first appeared 2026-09-23)
  DV-4253: **Should the Board resource the
  [Owner Plan](https://github.com/D-sorganization/AffineDrift/blob/main/docs/development/planning/DV-4253.md)?**
  Funding, access dates, execution capacity and an accountable human/equipment owner
  are all unverified. The project-steward run on 2026-11-16 submitted this to the Board
  through `submit_proposal` (`source: project-steward`, repo `AffineDrift`, title
  "Resource or formally shelve the DV-4253 physical/perceptual impact-acoustics validation
  plan"). Earlier passes (2026-10-07, 2026-11-03) had no submission tool.
- (first appeared 2026-09-23) DV-4253: Decide how to obtain and qualify
  Tools/UpstreamDrift physical impact and radiation results with uncertainty;
  prerequisite evidence remains unavailable.
- (first appeared 2026-09-23) DV-4253: Decide how to obtain and qualify controlled
  blinded perception evidence before any player-specific sweetness claim; prerequisite
  evidence remains unavailable.
- (first appeared 2026-11-16) Charter scope: now that IA-THEORY is done, the charter
  feature list tracks only parked DV-4253. Active epics #5587, #5638, #5565, #5395 and
  #5171 have no charter rows, so this projection cannot report on most of the active
  work. The product owner or Dieter should decide whether to add those rows (#1823). The
  steward does not add features itself.

## Reactivation

Follow the owner plan: record the Board decision and accountable owner, verify
all prerequisite evidence, then link the bounded activation issue in the catalog.
Preserve uncertainty, null findings and unavailable outcomes. A status projection
never substitutes for that decision or for physical/perceptual validation.
