# AffineDrift Programming Companion Turnover Prompt

Use the following prompt verbatim to start the next agent. The state below was
verified on 2026-08-30; GitHub state can advance, so the first action is always
to fetch and requery rather than assume.

---

You are taking over the AffineDrift Programming Companion and its governed
UpstreamDrift provider dependency. Continue from current protected evidence;
do not restart the website review or recreate already delivered work.

## Mission

Finish the remaining protected delivery safely while preserving AffineDrift as
the immutable explanatory/publication companion to UpstreamDrift. Use TDD,
DbC, LoD, and DRY. Keep scientific, provider, publication, screenshot, and
human-validation authority separate and fail closed.

## Read First

1. `C:\Users\diete\Repositories\AffineDrift\AGENTS.md`
2. `C:\Users\diete\Repositories\AffineDrift\CLAUDE.md`
3. `C:\Users\diete\Repositories\AffineDrift\AGENT_HANDOFF.md`
4. `C:\Users\diete\Repositories\AffineDrift\SPEC.md`
5. `C:\Users\diete\Repositories\AffineDrift\reports\website-companion-review-2026-08-29.md`
6. `C:\Users\diete\Repositories\AffineDrift\articles\proximal_distal_energy_transfer\source_manifest.json`
7. `C:\Users\diete\Repositories\UpstreamDrift\AGENTS.md` and its current
   `AGENT_HANDOFF.md`, but do not modify the occupied dirty primary checkout.

## Exact AffineDrift State

- Primary checkout: `C:\Users\diete\Repositories\AffineDrift`, clean `main`,
  equal to `origin/main` at protected #4107 merge
  `6350a5d4fdd59ccc68e1b8562d8f8c2b20d3e262` when the corrective worktree was
  created. Reverify because GitHub may have advanced.
- Programming Companion presentation: protected PR #4099, merge
  `717461e42e2de9f257cfa873ed336795dcc2d321`, successful deployment 33317188855. The stable `/models/models.html` route prominently presents the
  proximal-distal technical monograph beside the longer books, plus the visual
  companion, falsification atlas, workbench, and learning paths.
- Bibliography hierarchy repair: protected PR #4103, merge
  `d8775589e4ac5270816e60330b338354a78047db`; issue #4102 is closed. All
  exact-head checks passed. The diff is four retained files, +49/-8, zero
  deleted paths. The immutable proximal-distal tree has zero diff.
- Deployment 33321616181: build green; 928/928 pre-deployment inspections
  green. Live attempt 1 was 927/928 because
  `/articles/impact-optimality-and-model-limits.html` returned HTTP 503 at
  desktop/light. The one permitted retry was 927/928 because the different
  route `/pages/drifter-manifesto.html` returned HTTP 503 at mobile/light.
  Both artifacts contain all 928 expected records and exactly one failure.
  Do not rerun this run again.
- Issue #4104 is the only authority for the live-host/verifier reliability
  closure. A correct solution may add bounded, observable retry/backoff for
  transient 5xx responses, but must have deterministic tests for eventual
  success, exhaustion, and non-retriable failures and must not weaken any DOM,
  layout, heading, canonical, navigation, theme, notes, or overflow assertion.
- Turnover issue #4105 is closed by protected PR #4106 at
  `27d8a560a34fe7928d276960870853a2b35206cb`.
- Turnover deployment 33323483901 passed all four 232-route live groups for
  928/928 evidence items and zero failures, confirming the earlier 503s were
  intermittent. Artifact ID is 9735795376.
- Initial retry PR #4107 merged at
  `6350a5d4fdd59ccc68e1b8562d8f8c2b20d3e262`, but #4104 was reopened because
  retries were not live-only, retry attempts were absent from the artifact,
  intermediate error events persisted, and all navigation exceptions retried.
  Corrective work is in
  `C:\Users\diete\Repositories\worktrees\AffineDrift-4104-live-evidence` on
  `fix/4104-live-evidence-v2`. Requery its PR state before continuing.
- The clean pushed branch `fix/4104-bounded-live-retries` at `83dafc2b` in the
  `AffineDrift-4104-live-retries` worktree is superseded. Do not open it as a
  competing PR.
- Corrective-branch validation at turnover: full JavaScript 319 passed/19
  skipped; focused verifier 22/22 passed; deployment/content integrity passed
  with one declared missing-LaTeX-workflow skip; full headless Python 3,658
  passed/26 skipped. One PyQt6 GUI module was excluded because QtGui's native
  DLL would not import on this workstation; rely on protected CI for that lane.

## Exact UpstreamDrift State

- The primary checkout `C:\Users\diete\Repositories\UpstreamDrift` is occupied
  and dirty on unrelated branch `fix/9120-ci-conformance-docker-provenance`,
  with dirty submodules and untracked `book/`. Preserve it untouched.
- Use worktree
  `C:\Users\diete\Repositories\worktrees\UpstreamDrift-9190-workflows`.
- Protected main observed at
  `f98bf7b382083322c609bfd7d680e4e82d71aed8` (PR #9306).
- Provider workflow PR #9307 is open at exact head
  `6614f7ad8eafedde8a4f3162470850921d20e195` and exact base
  `f98bf7b382083322c609bfd7d680e4e82d71aed8`.
- Its 15-file diff is +3,292/-94 with no deleted paths. It defines a strict,
  hashed 15-record workflow registry: ten success workflows, four deterministic
  failure fixtures, and one explicitly unavailable native OpenSim GUI record.
  Registry SHA-256 is
  `ef78695030635fbe476912ecb7f59c8cdfd303cf0c187de0d24d63e22fd6be35`.
- All substantive checks passed, including `companion-workflows`, both Python
  lanes, optional stack, quality gate, publication, security, docs, Rust, and
  dependency contracts. `check-and-trigger` was still queued at turnover.
- GitHub reported #9307 as conflicting even though local Git proved protected
  main is the second parent of the exact PR head. Requery. Never force-push.
  If GitHub does not reconcile, create a fresh replacement branch from current
  protected main and carry the exact governed tree without weakening evidence;
  close #9307 only after the replacement PR exists and is cross-linked.
- PRs #9303 and #9304 are closed superseded branches. Do not revive them.
- #9174 and #9190-#9193 remain the provider program boundaries. Workflow
  execution evidence is not catalog publication, screenshot, native-engine, or
  scientific qualification authority.

## Deletion and Content-Loss Finding

No reviewed delivery deleted a path. The alarming summary of 222 files,
+12,882/-46,645 was transient Quarto-generated `docs/` churn, not committed
source loss. Direct reproductions reached more than 20,000 apparent removed
generated lines; restoring only tracked `docs/` output returned the canonical
source diff clean. Never commit a full-render `docs/` churn set without proving
it is intended. Always inspect `git diff --name-status`, `git diff --stat`, and
the immutable projection verifier before publication.

## Required Order

1. Fetch and verify exact repository, issue, PR, check, deployment, and worktree
   state. Do not trust this snapshot if GitHub advanced.
2. Complete the corrective #4104 branch through ordinary protected review;
   preserve #4107's valid tests and the two prior 503 artifacts.
3. Require one new protected exact-revision deployment whose pre-deployment and
   live matrices pass 928/928 and whose live artifact exposes the attempt and
   transient counters. Close #4104 only after inspecting that artifact.
4. Reconcile #9307 without force-pushing. Merge only when the exact head/base,
   every required check, and GitHub merge state are green. Verify the squash
   commit/tree, post-merge CI, and #9190 issue state.
5. Keep production AffineDrift catalog installation fail closed until provider
   #9174/#9190-#9193 independently publish the required immutable artifacts.
   Then continue AffineDrift #4023/#4024 and compatibility #4030 in dependency
   order; do not invent provider versions, commands, counts, or support tiers.
6. Preserve the protected proximal-distal monograph, #4087 atlas, and source
   manifest. UpstreamDrift owns computation/evidence; AffineDrift owns the
   immutable projection. Do not infer human technique, anatomy, physiology,
   safety, or coaching effects from structural-model evidence.

## Initial Commands

```powershell
git -C C:\Users\diete\Repositories\AffineDrift fetch origin
git -C C:\Users\diete\Repositories\AffineDrift status --short
git -C C:\Users\diete\Repositories\AffineDrift rev-parse HEAD
git -C C:\Users\diete\Repositories\AffineDrift rev-parse origin/main

git -C C:\Users\diete\Repositories\worktrees\UpstreamDrift-9190-workflows fetch origin
git -C C:\Users\diete\Repositories\worktrees\UpstreamDrift-9190-workflows status --short
gh pr view 9307 --repo D-sorganization/UpstreamDrift --json state,headRefOid,baseRefOid,mergeable,mergeStateStatus,statusCheckRollup,url
gh issue view 4104 --repo D-sorganization/AffineDrift --json state,title,url
gh issue view 4105 --repo D-sorganization/AffineDrift --json state,title,url

python C:\Users\diete\Repositories\AffineDrift\scripts\verify_proximal_distal_projection.py
```

## Stop Conditions

- Stop rather than merge if exact head/base/tree is uncertain, required checks
  are pending or failing, or GitHub reports a conflict.
- Stop rather than import if provider publication, compatibility, provenance,
  or artifact identity is incomplete.
- Stop rather than rerun if the action would erase adverse evidence, bypass
  capacity/protection, or repeat deployment 33321616181.
- Stop rather than edit the immutable projection when upstream release and
  source-manifest gates are not all protected.
- Leave both primary checkouts and every active worktree clean; report exact
  paths, branches, SHAs, issue/PR URLs, checks, and deployment evidence.

---

End of copy-ready prompt.
