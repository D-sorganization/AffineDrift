# AffineDrift Adversarial Architecture Review and Issue Drafts (2026-11-09)

Status: **draft for panel review. Nothing in this document has been filed as a GitHub issue.**
The Assessment Board hold ("no remediation issue flood until gated") applies; filing is a
separate, owner-approved step.

| Field | Value |
| --- | --- |
| Reviewed revision | `origin/main` at `df3c2a0ec` (2026-11-09) |
| Scope | Whole repository: `src/`, `scripts/`, `shared_scripts/`, `js/`, `tests/`, `.github/`, packaging, root docs, `schemas/`, `data/`, `config/` |
| Not in scope | Prose and scientific content of the articles and books; CSS detail; `_extensions/*.lua`; `scripts/verify-public-site*.js` (sized only) |
| Method | Six parallel adversarial reviewers by subsystem, each required to cite `file:line` and to reproduce numerically where possible; lead reviewer spot-verified the highest-severity items against source |
| Standard applied | "Comprehensive, professional-grade modeling software suite with excellent architecture" |
| Issue drafts | 90, in 14 epics (section 5): 12 P0, 45 P1, 32 P2, 1 P3 |
| Implicit state machines | 72 inventoried (section 4) |

## 1. How to read this document (instructions to the panel)

Each issue draft carries a **confidence** label. Treat them differently.

- **CONFIRMED (ran)**: a reviewer executed a probe that demonstrates the defect. The probe result
  is quoted.
- **CONFIRMED (read)**: established by reading the cited lines. No execution.
- **PLAUSIBLE**: a reasoned concern that needs a check before filing. Do not file as a bug
  without that check.
- **LEAD-VERIFIED**: the lead reviewer independently re-read the cited lines after the
  subsystem reviewer reported. This is marked on the items where the claim is most
  consequential.

What the panel is asked to do:

1. Challenge severity. P0 is reserved for "wrong numbers presented as right", "a safety or
   integrity gate that does not gate", or "user data loss".
2. Challenge the single design decision for state machines in section 4.2. It is one decision
   applied three ways (Python domain, Python numerics, browser). If you disagree, propose the
   replacement decision, not a per-site variation.
3. Flag any draft whose fix would break stored data, a published URL, or a public import path
   without the stated compatibility shim.
4. Flag duplicates of open issues. Known overlaps are listed in section 6.
5. Rule on the open questions in section 7.

Known limits of this review, stated so they are not mistaken for clean results:

- The repository's own `.venv` in the main checkout is empty (no numpy). All numerical probes
  ran on system Python 3.14 with numpy 2.4.6 and scipy 1.17.1, not on the pinned versions
  (numpy 2.5.3, scipy 1.18.1). No probe depends on a version-specific behaviour that we know
  of, but none was run on the pinned set.
- The full test suite was not run. Targeted files and mutation runs on a copy were.
- No Playwright, no Quarto render, no browser session. Frontend findings are from source.
- Launch-monitor reference carries in draft GS-03 are from reviewer memory of published
  tour averages. The fix must cite a source; the draft says so.
- Whether the self-hosted runner image has Quarto preinstalled was not verified (affects
  TS-07).

## 2. Verdict

AffineDrift is a carefully governed publication repository with a small numerical library
inside it. It is not yet a modeling software suite. The distance is mostly architectural and
is closable without a rewrite.

What is sound, and should be protected while fixing the rest:

- Import layering between the top-level packages is clean: no `src` module imports `scripts`,
  and `affine_control`, `core`, `golf_simulation`, `tangent_models` depend only inward.
- The core mechanics that were cross-checked are right: RNEA agrees with the Lagrangian route
  and with `GolfModel` to 2e-8 over 50 random states; the unforced `GolfModel` conserves
  energy to 1e-10 over 0.2 s; the iLQR solver reproduces the exact finite-horizon LQR cost on
  a double integrator to 1e-15.
- The companion-ingestion transport validates exact URLs against policy and bounds response
  size; the `quality-gate` fan-in correctly fails on skipped or cancelled dependencies.
- No `shell=True` anywhere in `scripts/` or `shared_scripts/`; every network call there has a
  timeout; no attacker-influenced HTML sink was found in `js/`.
- Two existing designs are the right pattern and are reused in the recommendations: the
  `research_readiness` transition function, and the DCR visualizer's versioned, validated
  `#state=` URL codec.

What stands between the repository and the stated standard, in order of consequence:

1. **Some published numbers and labels are wrong or unearned.** The LTV reachability Gramian
   recursion is incorrect for time-varying systems (NC-01). The swing optimizer reports
   `converged=True` when nothing was optimized (NC-03). The round simulator scores 172 to 180
   on a par-72 course because it almost never holes out (GS-01). The trust registry labels 131
   companion entities "CI-Verified" from a test fixture while the real pin is `draft` (EV-01).
   A validation report's outcomes are string constants that do not depend on the data (EV-02).
2. **Safety nets that do not catch.** All contract checks, including a policy gate, vanish
   under `python -O` or `DBC_LEVEL=warn` (NC-05). Six sign-flip mutants of the iLQR backward
   pass all pass the test suite (TS-01). CI type-checks `src/tools` only, not the numerical
   packages (CI-02). A required status check is satisfied by a job that runs `echo "Bypass"`
   (CI-01).
3. **There is no product boundary.** The distribution `affinedrift` installs a top-level
   package literally named `src`; `import affinedrift` does not exist (PK-01). Library modules
   read `data/` and `schemas/` through `Path(__file__).parents[N]`, so an installed wheel
   breaks at use (PK-02). The declared minimum Python cannot parse the code (PK-04). There is
   no CLI, no public API, no version single-source, and the release workflow has never run
   (PK-05, RL-01).
4. **Lifecycles are encoded as strings and booleans, redefined per module.** The same
   outcome vocabulary is declared in six modules with conflicting meanings; "negative" means
   "negligible effect shown" in one and "effect in the negative direction" in another (SM-03). Seventy-two implicit state
   machines were found; two have a transition table and one of those is bypassable.
5. **The test suite measures the repository more than the software.** About 15% of tests never
   touch repository code; roughly 3,300 assertions pin literal strings in prose; 214 of 684
   Python test files only read content (TS-03, TS-04).
6. **Gates exist as about 55 YAML steps with no local entry point** (GT-01), over 203 scripts
   with duplicated parsers whose behaviour has already drifted (GT-04).

## 3. Top 15 for immediate attention

Ordered by "would a user or reader be misled today".

| # | Draft | One line | Confidence |
| --- | --- | --- | --- |
| 1 | EV-01 | Trust registry marks 131 entities "CI-Verified" from a test fixture with a `"b"*64` digest; real pin is `draft` | CONFIRMED (ran), LEAD-VERIFIED |
| 2 | NC-01 | LTV backward Gramian recursion wrong for time-varying A, B (relative error 0.72 on a random 4-step case) | CONFIRMED (ran), LEAD-VERIFIED |
| 3 | NC-02 | Evaluator radius is a Cauchy-Schwarz outer bound; reports `recoverable=True` for unreachable targets | CONFIRMED (ran), LEAD-VERIFIED |
| 4 | NC-03 | `SwingOptimizer` returns `converged=True`, zero controls, target missed | CONFIRMED (ran), LEAD-VERIFIED |
| 5 | EV-02 | Population validation outcomes are hard-coded strings | CONFIRMED (ran), LEAD-VERIFIED |
| 6 | GS-01 | Round simulator: 140 of 144 holes end at the stroke cap | CONFIRMED (ran) |
| 7 | GS-02 | Lob wedge carries 61 m then rolls to 152 m on fairway | CONFIRMED (ran), LEAD-VERIFIED (formula) |
| 8 | NC-05 | Contracts and the mock-solver policy gate disappear under `-O` / `DBC_LEVEL=warn` | CONFIRMED (ran), LEAD-VERIFIED |
| 9 | SEC-01 | Security finding, filed privately | See private advisory |
| 10 | TS-01 | Six iLQR backward-pass mutants survive the test suite | CONFIRMED (ran) |
| 11 | CI-01 | Required check "Reject hosted runner routing" is produced by `echo "Bypass"` | CONFIRMED (read), LEAD-VERIFIED |
| 12 | FE-01 | Notes workspace: a stale tab overwrites newer notes on `visibilitychange` | CONFIRMED (read), LEAD-VERIFIED |
| 13 | SEC-02 | Security finding, filed privately | See private advisory |
| 14 | PK-01 | Wheel installs a top-level package named `src` | CONFIRMED (read), LEAD-VERIFIED |
| 15 | SM-03 | "negative" and "null" mean opposite things across protocol modules | CONFIRMED (read), LEAD-VERIFIED (literals) |

## 4. Implicit state machines

### 4.1 What was found

Seventy-two places hold a lifecycle, mode or outcome without declaring it as one. They fall
into five recurring shapes:

| Shape | What it looks like in this repository | Count |
| --- | --- | --- |
| A. Bare strings | `mode = "MPC_WARN"`, `status: "review-required"`, `Literal[...]` redeclared per module | 31 |
| B. Boolean sets | `converged` + `status`; `_using_mock` + `solver is None`; three booleans in the automerge guard | 11 |
| C. `None` sentinels | "not loaded yet", "not available", "no recovery" expressed as `None` or `-inf` | 8 |
| D. DOM as the state | class names, `aria-expanded`, `hidden`, inline styles each updated separately | 19 |
| E. Files and labels | a Markdown row, a JSON `status` field, a GitHub label, with no transition rule | 12 |

(Several machines show more than one shape; the count assigns each to its dominant one, with
nine counted twice.)

Only two have an explicit transition table: the research-readiness lifecycle
(`src/affine_control/research_readiness/states.py`) and the critique disposition table
(`scripts/generate_claim_critique_ledger.py:26-33`). The second can be bypassed (EV-05).
`src/` has 8 `Enum` classes against 81 `Literal[...]` declarations.

The cost is concrete, not stylistic. Each of these was traced to an implicit machine:

- `converged=True` with no optimization (NC-03): status string and boolean set independently.
- "negative" meaning both "effect in the negative direction" and "negligible effect shown"
  (SM-03): the vocabulary has no owner.
- A companion pin can move from `qualified` back to `draft` with no guard, and `stale` is not
  a state at all, so 14 of 22 pins sit at `review-required` with CI green (EV-09).
- Notes overwritten by a stale tab (FE-01): the document has no `conflict` state.
- Forty-nine development-log entries stuck at `in_review` after their PRs merged (SM-07).
- A round that "ends" by hitting the stroke cap is indistinguishable from one that was holed
  (GS-01).

### 4.2 The decision

One decision, applied in three places. It was chosen because it is the only option examined
that improves UX, DX and AX together and can be introduced without changing a stored value, a
URL or an import path.

> **Every lifecycle gets one named type that owns its states, one table that owns its legal
> transitions, and one function that performs a transition. Stored values do not change.
> Anything that can be computed from other state is computed, never stored.**

Applied to Python domain and governance code (shapes A, E):

```python
# src/affine_control/lifecycle/core.py  (new; no third-party dependencies)
class Lifecycle[S: StrEnum]:
    def __init__(self, states: type[S], transitions: Mapping[S, frozenset[S]],
                 terminal: frozenset[S] = frozenset()) -> None: ...
    def can(self, src: S, dst: S) -> bool: ...
    def advance(self, src: S, dst: S, *, reason: str) -> Transition[S]:  # raises IllegalTransition
    def replay(self, history: Sequence[Transition[S]]) -> S:             # validates stored history
    def to_mermaid(self) -> str:                                         # docs are generated
```

- States are `StrEnum` whose **values equal the strings already on disk**. A
  `LEGACY_ALIASES: dict[str, S]` maps the known variant spellings on read; writers emit only
  canonical values.
- JSON Schema `enum` lists are generated from the enums (`$defs` written by one script and
  diffed in CI), so Python and schema cannot drift.
- Derived states (`stale`, `critique_status`, "is this pin current") are pure functions of
  stored facts and are never written to disk.

Applied to numerical results (shapes B, C): tagged unions, not flag sets.

```python
class SolveStatus(StrEnum): CONVERGED; MAX_ITERATIONS; LINE_SEARCH_FAILED; NUMERICAL_FAILURE; NOT_RUN
@dataclass(frozen=True, slots=True)
class OptimizationResult:
    status: SolveStatus
    ...
    @property
    def converged(self) -> bool: return self.status is SolveStatus.CONVERGED   # kept, derived
```

`Available[T] | Unavailable(reason)` replaces `None`-means-missing. Existing attributes
(`converged`, `recoverable`, `_using_mock`) remain as derived read-only properties for one
minor version with a `DeprecationWarning`, then are removed under the policy in PK-05.

Applied to the browser (shape D): one small dependency-free module.

```js
// js/lib/machine.js  (new, ~60 lines, ES module)
export function createMachine(root, { initial, transitions, onEnter }) { ... }
// send(event) looks up transitions[state][event]; unknown events are ignored and logged in dev.
// The current state is written to root.dataset.state. CSS and ARIA are derived from it.
```

- `data-state` on the widget root is the single source of truth. CSS selects on
  `[data-state="open"]`; `aria-expanded`, `hidden`, `inert` are set in `onEnter`, in one place.
- State types are JSDoc discriminated unions checked by `tsc --checkJs` (no build step, no
  TypeScript migration).
- Shareable widget state uses the existing DCR pattern: a versioned, validated `#state=v1.…`
  codec, generalized into `js/lib/url-state.js` (already specified in
  `docs/audits/widget-url-hash-state-spec-5255.md`).

Why not the alternatives:

| Alternative | Why rejected |
| --- | --- |
| A state-machine library (`transitions`, `python-statemachine`, XState) | Adds a runtime dependency to a numerical library and a build step or 40 kB to a static site, for tables that fit in 60 lines. Fails "without breaking anything" for the no-build frontend. |
| Enums only, no transition tables | Fixes spelling, not legality. EV-09 (downgrade unguarded) and SM-07 (stuck `in_review`) would remain. |
| Per-module fixes | This is the current state. Six modules redeclare the outcome tuple today. |
| Rename stored values to a clean vocabulary | Breaks committed JSON, schemas and published pages. Deferred to a versioned migration (EV-08) after the types exist. |

How this serves each audience:

- **UX**: every widget gets `loading`, `error` and `empty` states because the table makes
  their absence visible; readers see "not run" instead of "converged"; trust labels can only
  be reached by a recorded transition.
- **DX**: one place to read a lifecycle; exhaustive `match` checked by mypy; illegal
  transitions fail at the call site with the legal set in the message; diagrams generated.
- **AX**: an agent can ask `python -m affinedrift lifecycle show readiness --json` and get the
  states, the legal next states and the reason a transition was refused, instead of inferring
  them from prose in a 51 kB AGENTS.md. `data-state` gives browser agents and E2E tests a
  stable hook that is not a CSS class.

Migration rule for every machine below (the "without breaking anything" contract):

1. Add the type and table beside the existing code. No behaviour change. Characterization
   tests pin the current reachable transitions first, including the ones believed wrong.
2. Route writers through `advance()`. Readers accept legacy aliases.
3. Turn each wrong-but-reachable transition into an explicit decision: allow it in the table,
   or reject it with a migration for existing data. One PR per decision.
4. Remove deprecated flags after one minor version.

### 4.3 Inventory

Columns: **Now** is how the state is held today. **Problem** is the observed consequence, not
a style complaint. **Target** is the type under decision 4.2. The last column names the issue
draft that carries the work.

#### 4.3.1 Numerics and control (9)

| # | Machine | Where | Now | Problem | Target | Draft |
| --- | --- | --- | --- | --- | --- | --- |
| N-1 | Residual monitor control mode | `src/affine_control/residuals.py:285,313-357` | strings `LQR`/`MPC_WARN`/`MPC_FULL` plus three counters, public and mutable | 2n-sample escalation latency; never escalates on alternating residuals; callers can set any mode | `ControlMode(StrEnum)`, `ResidualBand`, frozen `MonitorState`, `TRANSITIONS` table, pure `step(state, residual)` | NC-12 |
| N-2 | iLQR solve lifecycle | `ilqr_solver.py` | status strings and a redundant `converged` bool | diagnostics stale after failed line search; raise instead of status | `SolveStatus`, frozen `OptimizationResult` | SM-05 |
| N-3 | Swing optimizer solver selection | `swing_optimizer.py:139,342-356` | `solver=None` means mock; `_using_mock`; `PYTEST_CURRENT_TEST` sniffing | mock solver is the library default; env var spoofs the gate | required `TrajectoryOptimizer` protocol argument; mock only in `tests/` | NC-10 |
| N-4 | Swing optimizer convergence | `swing_optimizer.py:472` | `abs(cost_improvement) < tol and iteration > 1` | `converged=True` with zero progress | `SolveStatus.NOT_RUN` / `STALLED` distinct from `CONVERGED` | NC-03 |
| N-5 | Swing analysis data loading | `swing_analysis.py` | attributes `None` until a method fills them | call order is an undocumented protocol; `AttributeError` far from cause | frozen `SwingKinematics` / `SwingDynamics` returned by pure functions; facade kept | SM-05 |
| N-6 | ZTCF intervention availability | `ztcf_contract.py` | `status` string with fields valid only for some values | fields read when unavailable | pydantic discriminated union on the existing `status` key | NC-11 |
| N-7 | Impact contact topology | `impact_contact_models.py` | regime encoded as message-string prefixes | consumers parse prose | `ContactRegime`, `ContactPhase`, outcome union | NC-13 |
| N-8 | Swing phase | `motion_clip_frames.py:24-29` | a comment above the `KEY_S` array | Python and JS each re-derive phase boundaries | `SwingPhase` enum, `Keyframe`, `phase_at(s)`, exported in frame JSON | SM-05 |
| N-9 | Correction-authority result kind and contract level | `correction_authority_*.py`; `core/contracts/definitions.py:44` | `recoverable: bool` with `-inf` sentinel margins; contract level is a module global captured at decoration time | "unreachable", "degenerate" and "not evaluated" collapse into `False`; level cannot be changed per call or per test | `AuthorityStatus`; `ContextVar` level read at call time | NC-02, NC-05 |

#### 4.3.2 Golf simulation and tools (8)

| # | Machine | Where | Now | Problem | Target | Draft |
| --- | --- | --- | --- | --- | --- | --- |
| G-1 | Ball lifecycle | `ball_flight.py`, `terrain.py`, `round_simulator.py` | implicit in control flow | "landing" detected mid-air; bounce and roll share one friction number | `BallPhase`: `FLIGHT`/`BOUNCE`/`ROLL`/`AT_REST`/`IN_HAZARD`/`OUT_OF_BOUNDS`/`TIMED_OUT`; trajectory as typed segments | SM-06 |
| G-2 | Hole and round progression | `round_simulator.py:217-241` | loop counter and a stroke cap | capped hole indistinguishable from holed | `HoleOutcome`, `Stroke` union, `LieState` | SM-06, GS-01 |
| G-3 | Putt outcome | `putting.py` | floats and a `holed` bool | lip-out, off-green and "never stopped" not representable | `PuttOutcome`, `PuttResult` | GS-04 |
| G-4 | Green surface kind | `putting.py:111-113` | one class, branches on optional arrays | world coordinates passed to a green-local surface | `PlanarGreen` / `SampledGreen` with an explicit frame | GS-04 |
| G-5 | Slack transmission contact | `src/tools/slack_transmission.py:108,168,188` | booleans and `-1.0`-style sentinels | dead-zone model implemented twice | `ContactState`, `Phase`, `recovery_delay_s: float \| None` | TL-02 |
| G-6 | Wrist app signal and plot modes | `wrist_universal_joint/` (Streamlit and Qt front ends) | strings compared in two UIs | UIs disagree on valid combinations | `SignalKind`, `PlotKind`, one shared reducer | TL-05 |
| G-7 | Notebook bridge status | `notebooks_bridge.py:175-187` | generated vs unknown | authored notebooks overwritten; unknown files deleted | add `AUTHORED`; delete only `GENERATED` with a matching marker | TL-03 |
| G-8 | Tool results | `src/tools/*` | status strings per tool | callers string-match | `ToolOutcome`, `GainStatus` | TL-05 |

#### 4.3.3 Evidence, protocols and trust (16)

| # | Machine | Where | Now | Problem | Target | Draft |
| --- | --- | --- | --- | --- | --- | --- |
| E-1 | Research-readiness lifecycle (12 states) | `research_readiness/states.py`, `validation.py:178-332` | explicit table (best in repo) | attempt history cannot survive promotion; `published` unreachable | keep; move onto `Lifecycle`; append-only attempts | EV-10 |
| E-2 | Evidence status | protocol modules | `Literal` per module | vocabularies differ by module | one `EvidenceStatus` | SM-03 |
| E-3 | Critique disposition | `scripts/generate_claim_critique_ledger.py:26-33,185-205` | table exists | validated only on one code path | `Lifecycle.replay` on load | EV-05 |
| E-4 | Claim `critique_status` | claim registry data | hand-maintained field | disagrees with the ledger (`ad-dcr-001`) | derived from ledger, not stored | EV-05 |
| E-5 | Claim-audit route and finding disposition | claim-audit inventory scripts | JSON fields | resettable with `--initialize-from-manifest`; no `stale` | add source-hash-derived `stale`; reset requires explicit flag and reason | GT-03 |
| E-6 | Publication and maturity state | page front matter, catalog, registry | strings | `validated` and `experimental` each mean two things (`evidence_class: experimental` maps to `VALIDATED_EVIDENCE`) | two separate enums: `Maturity`, `EvidenceClass`; no shared words | SM-04 |
| E-7 | Evidence tier and rung | `schemas/`, `evidence_presentation/` | `StrEnum` and `Literal` both exist; one schema enum mixes two ladders | projectors default to the stronger tier | single enum per ladder; unknown maps to weakest | EV-06 |
| E-8 | Companion publication and qualification | `programming_companion/`, lock file | strings | downgrade `qualified` to `draft` unguarded; registry ignores it | `Lifecycle` with explicit downgrade transition that invalidates dependants | EV-01 |
| E-9 | Pin review state | `scripts/check_companion_pins.py:40,325-342` | `reviewed` / `review-required` | review never expires; no `stale` | derived `stale` from review date and upstream head | EV-09 |
| E-10 | Acquisition attestation | (withheld) | (withheld) | (withheld; filed privately) | `Attestation` union (see private advisory) | SEC-02 |
| E-11 | Snapshot store lifecycle | `programming_companion/store.py:95-216` | directory layout | no writer lock, no fsync, extra directories accepted | `STAGING`/`COMMITTED`/`QUARANTINED` with atomic rename | EV-09 |
| E-12 | Result outcome | six protocol modules | 4-tuple redeclared | "negative"/"null" contradict | one `ResultOutcome` with documented semantics | SM-03 |
| E-13 | Evidence origin | generators, schemas | five spellings of "synthetic" | filters miss variants | one `EvidenceOrigin` plus aliases | SM-03 |
| E-14 | Human-study gate | four implementations, e.g. `hand_wrench_evidence.py:95-101` | dataclass of free strings and a bool | `HumanTierGate("TODO","n/a","tbd","?",True).authorize()` returns `True` | one `HumanGovernanceGate` with validated fields and a `Decision` union | EV-04 |
| E-15 | Release level and disposition | `research-releases` scaffold | unvalidated fields | no schema, no transitions | schema plus `Lifecycle`, or delete the scaffold | EV-10 |
| E-16 | Const-pinned placeholder statuses | several schemas | `const: "placeholder"` | a state that can never change is documentation, not data | remove or make it a real enum | EV-08 |

#### 4.3.4 Browser (27)

All take `createMachine` and `data-state` unless noted. "Missing" lists states that do not
exist today and should.

| # | Machine | Where | Now | Missing or wrong | Draft |
| --- | --- | --- | --- | --- | --- |
| U-1 | Notes workspace: panel (`closed`/`open`/`popped`) × document (`clean`/`dirty`/`saving`/`saved`/`error`/`conflict`) | `js/notes-workspace.js` | flags and DOM | `conflict`, `error`; cross-tab sync | FE-01, FE-02 |
| U-2 | Service worker lifecycle and update banner | `js/service-worker*.js` | `skipWaiting` + `clients.claim` | `update-available`, `update-deferred`; version skew | FE-03 |
| U-3 | Service worker request strategy | `js/service-worker-utils.js:30-77` | timeout races | `slow` distinct from `failed` | FE-03 |
| U-4 | Search lazy loader | search loader | boolean | `failed`; retry | FE-09 |
| U-5 | Bibliography filter and fallback | `js/bibliography.js` | DOM | `loading`, `empty`; debounce broken | FE-04 |
| U-6 | Navbar collapse | `js/navigation.js` | class toggles | ARIA can desynchronize | FE-07 |
| U-7 | Sidebar | `js/navigation.js` | class toggles | same | FE-07 |
| U-8 | Scroll-spy | `js/navigation.js:438-469` | two implementations; overrides `offsetTop` | one owner | FE-09 |
| U-9 | Lightbox | `js/ui-components.js:426-429` | DOM | alt text destroyed; focus return | FE-06 |
| U-10 | Disclosures | several files | duplicated | one implementation | FE-07 |
| U-11 | Print mode | print handlers | before/after events | restore on cancel | FE-07 |
| U-12 | Back-to-top | UI components | scroll listener | none (low risk) | FE-07 |
| U-13 | Keyboard modality | UI components | body class | delete; use `:focus-visible` | FE-06 |
| U-14 | Theme | two files | two-state, duplicated | `system`/`light`/`dark` | FE-09 |
| U-15 | Copy buttons | UI components | timers | `copied`/`failed` | FE-07 |
| U-16 | Contact form | `js/forms.js` | DOM | `submitting`/`sent`/`failed`; landmark flooding | FE-06 |
| U-17 | MathJax gate | site head | flag | `failed`; overlaps open #5253 | FE-09 |
| U-18 | Drift-control sandbox | `js/drift-control-sandbox.js` | globals | `loading`, `error`; name collisions | FE-08 |
| U-19 | ZTCF explorer | `js/ztcf-explorer.js` | globals | same | FE-08 |
| U-20 | DCR visualizer | DCR visualizer | versioned `#state=` codec | reference pattern; generalize | FE-08 |
| U-21 | Rotation converter | `articles/rotation-converter.qmd` | inline script | CDN without SRI | SEC-04 |
| U-22 | Swing, arm and motion-clip viewers | `js/*-viewer.js` | three copies of playback | shared `createPlayback`: `loading`/`error`/`paused`/`playing`/`scrubbing` | FE-08 |
| U-23 | Dataset explorer | dataset explorer | DOM | `loading`/`empty`/`error` | FE-08 |
| U-24 | History panel | `js/history.js` | localStorage | basename links; unversioned storage | FE-05 |
| U-25 | Local metrics | metrics script | localStorage | unbounded | FE-09 |
| U-26 | Section fade | UI components | IntersectionObserver | reduced-motion | FE-06 |
| U-27 | Grip-angle simulator | `grip_angle_simulator.html` | standalone page | CDN without SRI; outside the site shell | SEC-04 |

#### 4.3.5 Repository process (12)

These machines are run by people and agents, which is why they matter most for AX.

| # | Machine | Where | Now | Problem | Target | Draft |
| --- | --- | --- | --- | --- | --- | --- |
| P-1 | Change fragment | `changes/` | file presence | collation is a commit to `main` per fragment batch (67 of the last 200 commits) | `pending`/`collated`/`released`; collate at release | RL-02 |
| P-2 | Development-log entry | development log | `status` field | 49 entries stuck `in_review` | derive from PR state; never hand-edit | SM-07 |
| P-3 | SPEC row | `SPEC.md` | appended rows | 80% of the file is log; duplicate keys | normative spec separate from generated change log | DOC-02 |
| P-4 | Release | `VERSION`, tags, `release.yml` | five version numbers | workflow never run | `unreleased`/`tagged`/`built`/`published`/`yanked` in one manifest | RL-01 |
| P-5 | PR merge state | labels plus `scripts/automerge_guard.py` | three booleans; refusal reason dropped | agents cannot tell why arming was refused | `Verdict` union with reason (upstream in Repository_Management) | GT-06 |
| P-6 | Deploy | `deploy-website.yml` | last run only | no last-good, no rollback | `building`/`deployed`/`failed`/`rolled-back`; record last-good artifact | RL-02 |
| P-7 | Quarto cache seed | CI cache steps | implicit | stale seed silently reused | key on input hash; `miss` is a visible state | CI-04 |
| P-8 | Quality-budget ratchets | five baseline files | independent JSON | no monotone enforcement; budgets were loosened | `ratchets.toml`; loosen only with a labelled, reasoned change | GT-03 |
| P-9 | Deferred validation | deferred-work file A | schema A | two incompatible schemas | one schema, one lifecycle | GT-06 |
| P-10 | Deferred planning | deferred-work file B | schema B | same | merged into P-9 | GT-06 |
| P-11 | Handoff document | vendored `handoff_validator` | unwired | repository fails its own validator | wire it or remove it | GT-06 |
| P-12 | Agent hook result | agent hook manifest | pass/fail | a missing tool passes | `pass`/`fail`/`not_applicable`/`unavailable`/`misconfigured` | GT-06 |

## 5. Issue drafts

Ninety drafts in fourteen epics. Each draft is sized to become one issue and, where possible,
one PR under 500 changed lines. Drafts marked **(split)** need more than one PR and say how to
cut them.

Draft fields: **Evidence** (what was observed, with `file:line`), **Impact**, **Fix**,
**Accept** (acceptance criteria a reviewer can check), **Compat** (what must not break and
how), **UX/DX/AX** (who gains what). Paths are relative to the repository root; paths that
begin with a bare module name are under `src/affine_control/`.

Epic index:

| Epic | Theme | Drafts | P0 | P1 | P2 | P3 |
| --- | --- | --- | --- | --- | --- | --- |
| NC | Numerics and control correctness | 14 | 4 | 6 | 4 | 0 |
| AR | Library architecture | 4 | 0 | 3 | 1 | 0 |
| GS | Golf simulation | 6 | 2 | 3 | 1 | 0 |
| TL | Tools | 5 | 0 | 3 | 2 | 0 |
| EV | Evidence, protocols and trust | 11 | 2 | 4 | 4 | 1 |
| SEC | Security | 4 | 1 | 2 | 1 | 0 |
| SM | State-machine foundations | 7 | 0 | 4 | 3 | 0 |
| PK | Packaging and public API | 6 | 0 | 4 | 2 | 0 |
| RL | Release and deploy | 2 | 0 | 2 | 0 | 0 |
| CI | CI integrity | 4 | 1 | 1 | 2 | 0 |
| DOC | Documentation | 4 | 0 | 2 | 2 | 0 |
| FE | Frontend | 10 | 1 | 5 | 4 | 0 |
| TS | Test adequacy | 7 | 1 | 3 | 3 | 0 |
| GT | Gates and agent tooling | 6 | 0 | 3 | 3 | 0 |
| | **Total** | **90** | **12** | **45** | **32** | **1** |

### 5.1 Epic NC: numerics and control correctness

#### NC-01 [P0] LTV reachability Gramian recursion is wrong for time-varying systems

- **Labels**: `bug`, `numerics`, `correctness`. **Confidence**: CONFIRMED (ran), LEAD-VERIFIED.
- **Evidence**: `correction_authority_evaluator.py:118` computes
  `gramian = a @ gramian_next @ a.T + b @ b.T`, a backward sweep that propagates the
  accumulated Gramian through the wrong transition matrix. It equals the horizon-end
  reachability Gramian `W(k,N) = Σ_{j=k}^{N-1} Φ(N,j+1) B_j B_jᵀ Φ(N,j+1)ᵀ` only when `A` and
  `B` are constant. On a random 4-step LTV system the relative Frobenius error against the
  brute-force sum was 0.718. For LTI input the two agree, which is why existing tests pass.
- **Impact**: every correction-authority margin computed along a real (time-varying)
  linearized swing trajectory is wrong, by an amount that depends on how fast the
  linearization changes. This is the central published quantity of the correction-authority
  work.
- **Fix**: accumulate with the correct recursion,
  `W(k,N) = W(k+1,N) + Φ(N,k+1) B_k B_kᵀ Φ(N,k+1)ᵀ`, carrying `Φ(N,k+1)` backward
  (`Φ(N,k) = Φ(N,k+1) A_k`). State in the docstring which Gramian this is (reachability to the
  horizon end, state coordinates at `N`).
- **Accept**: (1) a Hypothesis property test compares against the brute-force sum for random
  LTV systems with n ≤ 6, N ≤ 12, relative error < 1e-10; (2) the LTI case is unchanged to
  1e-12; (3) every committed artifact derived from this function is regenerated, and the diff
  in reported margins is listed in the PR body; (4) pages that cite those numbers are updated
  or flagged in the same PR.
- **Compat**: numerical results change by design. Function signature unchanged. Add a
  `changes/` fragment under "Fixed" naming the affected artifacts.
- **UX/DX/AX**: readers get correct margins; developers get an oracle test; agents get a
  property test that fails loudly on regression instead of a tolerance to tune.

#### NC-02 [P0] Correction-authority radius is an outer bound, so unreachable targets are reported recoverable

- **Labels**: `bug`, `numerics`, `correctness`. **Confidence**: CONFIRMED (ran), LEAD-VERIFIED.
- **Evidence**: `correction_authority_evaluator.py:152` returns
  `input_bound * sqrt(dᵀ W d * horizon_steps)`. That is the Cauchy-Schwarz bound for an
  energy-bounded input rescaled to a peak bound; it is never smaller than the true support
  function of the reachable set under `‖u‖∞ ≤ ū`, and is usually larger. Double integrator,
  `ū = 1`, exact reach along the tested direction 0.5: the evaluator returns
  `recoverable=True` at 0.55. `tests/test_correction_authority_evaluator.py:80` passes because
  it compares with `tol_margin=0.08`.
  Related, same files: `_margin_to_target` is duplicated in
  `correction_authority_contract.py:129-132` and `correction_authority_evaluator.py:95-104`,
  is discontinuous in the target, ignores its tolerance argument on one path, and accepts
  `NaN` tolerance.
- **Impact**: the answer errs in the unsafe direction: "this error can still be corrected"
  when it cannot.
- **Fix**: compute the exact support function for the declared input set. For a per-channel
  peak bound: `h(d) = ū · Σ_j ‖B_jᵀ Φ(N,j+1)ᵀ d‖₁`. Make the input-set norm an explicit enum
  argument (`PEAK_PER_CHANNEL`, `ENERGY`), with the Gramian formula used only for `ENERGY`.
  One `_margin_to_target`, continuous, tolerance validated finite and ≥ 0. Replace the
  `recoverable: bool` plus `-inf` sentinel with `AuthorityStatus` (state machine N-9).
- **Accept**: (1) double-integrator closed form matched to 1e-12, and 0.55 is reported
  unreachable; (2) property test: the reported radius is attained by an admissible bang-bang
  input (constructive check) and no admissible random input exceeds it; (3) the test
  tolerance of 0.08 is removed; (4) artifact regeneration and diff as in NC-01.
- **Compat**: `recoverable` stays as a derived property. Results change by design and become
  more conservative.
- **UX/DX/AX**: the claim shown to readers becomes a guarantee rather than an optimistic
  estimate; the norm assumption is visible in the API and in JSON output.

#### NC-03 [P0] `SwingOptimizer` reports `converged=True` when no optimization happened

- **Labels**: `bug`, `numerics`. **Confidence**: CONFIRMED (ran), LEAD-VERIFIED.
- **Evidence**: `swing_optimizer.py:472`:
  `if abs(cost_improvement) < cfg.convergence_tol and iteration > 1`. Zero improvement
  satisfies it. A run with zero controls and the target missed returns `converged=True`.
  `swing_optimizer.py:384` silently caps the inner solver at `min(5, …)` iterations.
  `swing_optimizer.py:383` passes one tolerance into three places where it means cost change,
  gradient norm and constraint violation.
- **Impact**: any figure, table or page built from this optimizer may present an unoptimized
  trajectory as an optimum.
- **Fix**: convergence requires a first-order optimality measure below tolerance **and** the
  terminal target error within a declared tolerance. Stalled runs return
  `SolveStatus.STALLED`; a run that never iterated returns `NOT_RUN`. Remove the hidden cap or
  make it a named, documented config field. Three named tolerances.
- **Accept**: (1) the zero-control case returns a non-converged status; (2) a test asserts the
  reported cost equals the cost recomputed from the returned trajectory; (3) no literal
  iteration cap remains outside config; (4) every committed result marked converged is
  re-run and its status re-recorded.
- **Compat**: `converged` remains, derived from `status`.
- **UX/DX/AX**: "not run" and "stalled" become visible states; agents consuming JSON results
  can branch on `status` instead of trusting a bool.

#### NC-04 [P1] Swing optimizer reports a different objective than it optimizes, with a unit error in the target

- **Labels**: `bug`, `numerics`. **Confidence**: CONFIRMED (read).
- **Evidence**: the cost reported at `swing_optimizer.py:147-151` is not the cost the solver
  minimizes at `ilqr_solver.py:275-277`; control and terminal weights from the optimizer
  config never reach the solver. `target_velocity` is documented as clubhead speed in m/s
  (`swing_types.py:27-28`) but is applied as the target angular rate of every joint
  (`swing_optimizer.py:207`), and the norm of joint rates is logged as m/s
  (`swing_optimizer.py:506,517`).
- **Impact**: the optimizer solves a different problem from the one it documents and reports.
- **Fix**: one cost object constructed once and passed to both solver and reporter. Clubhead
  speed target expressed through the forward-kinematics Jacobian, or the field renamed to
  what it is (`target_joint_rate_rad_s`) with the old name deprecated. Units in field names
  or in a typed quantity.
- **Accept**: test that solver cost and reported cost agree to 1e-10 on the returned
  trajectory; test that a clubhead-speed target of v produces clubhead speed v within
  tolerance on a two-link model.
- **Compat**: old field accepted with `DeprecationWarning` for one minor version.
- **UX/DX/AX**: numbers on pages carry the unit they claim.

#### NC-05 [P0] Contract checks, including a policy gate, disappear under `python -O` or `DBC_LEVEL=warn|off`

- **Labels**: `bug`, `safety`, `architecture`. **Confidence**: CONFIRMED (ran), LEAD-VERIFIED.
- **Evidence**: `src/core/contracts/definitions.py:44` reads the level once at import;
  `:134-146` makes `require()` a no-op or a warning below `strict`, and parts of the layer
  use `assert`. The same `require()` is used for boundary validation of user input and for
  the gate that refuses to run the mock solver outside tests.
  `ContractViolationError(AssertionError, ValueError)` (`definitions.py:67`) means
  `except ValueError` and `except AssertionError` both swallow it.
  `validators.py:34,39` accept `±inf` and `bool` as valid numbers.
- **Impact**: an environment variable or an interpreter flag turns input validation and a
  policy gate off. Design-by-Contract is a development aid; boundary validation is not
  optional.
- **Fix**: separate the two. (a) `validate_*` functions that always run and raise
  `InvalidInputError(ValueError)`; (b) optional `@contract` pre/post/invariant checks governed
  by a `ContextVar` level read at call time. No `assert` in either. Policy gates use neither:
  they are ordinary `if … raise`. One error taxonomy: `AffineDriftError` →
  `InvalidInputError(ValueError)`, `NumericalFailure(ArithmeticError)`,
  `ContractViolation` (not an `AssertionError`).
- **Accept**: (1) the test suite passes under `python -O`, and a CI job runs a boundary-test
  subset that way; (2) with `DBC_LEVEL=off`, invalid public inputs still raise
  `InvalidInputError`; (3) `rg "^\s*assert " src/` returns nothing outside `TYPE_CHECKING`
  narrowing; (4) validators reject `inf`, `nan`, `bool`.
- **Compat**: `ContractViolationError` kept as an alias that still subclasses `ValueError`
  for one minor version. `DBC_LEVEL` keeps working for contracts only.
- **UX/DX/AX**: users get the same errors in every environment; developers can raise the
  contract level for one test via a context manager; agents get stable exception types to
  match on.

#### NC-06 [P1] Public numerical entry points validate nothing; one validation layer is needed (split)

- **Labels**: `robustness`, `architecture`. **Confidence**: CONFIRMED (ran) for the listed
  cases; PLAUSIBLE for `modal_frequencies` units.
- **Evidence**: `GolfModel` and `PlanarLink` accept negative masses and lengths; `steps=0`
  raises `ZeroDivisionError`; nine modules carry their own ad hoc finite-ness checks;
  `src/core/constants.py:43-46,76-104` reads environment overrides at import and swallows
  malformed values, and mixes physical, numerical and site constants in one module. Whether
  `modal_frequencies` returns rad/s or Hz is not stated and callers appear to disagree
  (needs a check before filing that part).
- **Fix**: validated frozen parameter dataclasses (`__post_init__` using NC-05 validators);
  every public function validates shape, dtype and finiteness once at the boundary and
  internal helpers trust their inputs; configuration via an explicit `Settings` object, not
  import-time environment reads; split constants by domain.
- **Accept**: a parametrized test feeds `nan`, `inf`, wrong shape, negative physical
  parameters and zero steps to every symbol in the public API (PK-05) and asserts
  `InvalidInputError`; a malformed environment override raises at startup with the variable
  name.
- **Compat**: inputs that were silently accepted and produced garbage now raise. List them in
  the changelog. Split by package: `core`, `affine_control`, `golf_simulation`.
- **UX/DX/AX**: errors name the argument and the constraint.

#### NC-07 [P1] `discrete_lqr` returns non-stabilizing or indefinite solutions without warning

- **Labels**: `bug`, `numerics`. **Confidence**: CONFIRMED (ran).
- **Evidence**: `lqr.py:31,121-150`: fixed-point iteration with absolute tolerance 1e-14, no
  input checks, no post-conditions. It fails to converge for `Q = 1e6·I` (absolute tolerance
  below rounding at that scale) and returns whatever the last iterate was for
  non-stabilizable pairs.
- **Fix**: validate `Q ⪰ 0`, `R ≻ 0`, shapes; use `scipy.linalg.solve_discrete_are` as the
  primary solver (scipy is already a dependency) and keep the iteration only as a documented
  fallback with relative tolerance; post-check symmetry, positive semidefiniteness, Riccati
  residual and closed-loop spectral radius < 1; return a result object with `status`.
- **Accept**: agreement with scipy to 1e-9 relative over a random well-posed suite; scaled
  problems (`Q` from 1e-6 to 1e8) converge; an unstabilizable pair returns
  `NUMERICAL_FAILURE` with the reason.
- **Compat**: tuple return preserved through `__iter__` on the result for one minor version.
- **UX/DX/AX**: a failed design is a status, not a silently bad gain.

#### NC-08 [P1] iLQR: line search raises instead of backtracking; optimum depends on the time grid

- **Labels**: `bug`, `numerics`. **Confidence**: CONFIRMED (ran) for grid dependence;
  CONFIRMED (read) for the rest.
- **Evidence**: `ilqr_solver.py:313-318` raises when a trial rollout is non-finite instead of
  shrinking the step; only 5 backtracks; no Armijo sufficient-decrease test; diagnostics
  describe the last accepted iterate after a failed one. `:200-204` uses ad hoc
  regularization and `np.linalg.inv`. `:141` uses forward differences with ε = 1e-5. `:160`
  and `:438` integrate with explicit Euler. `:412-413` does not scale running cost by `dt`,
  so the same continuous problem gave cost 11.86 on one grid and 108.69 on another.
- **Fix**: treat a non-finite rollout as a rejected step; Armijo condition with expected
  reduction; Levenberg-Marquardt regularization schedule with Cholesky factorization and
  `solve`, never `inv`; `dt`-scaled running cost; integrator injected (AR-01); central
  differences with scaled step, or user-supplied Jacobians.
- **Accept**: a grid-refinement test (cost converges at the integrator's order as `dt` is
  halved); a test whose first full step is non-finite and which still converges; no
  `linalg.inv` in the solver.
- **Compat**: costs change for existing configurations because of `dt` scaling. Provide
  `legacy_unscaled_cost=True` for one minor version and regenerate committed results.
- **UX/DX/AX**: results stop depending on an incidental discretization choice.

#### NC-09 [P1] Continuous-time Gramian uses an endpoint-inclusive Riemann sum with 32 fixed samples

- **Labels**: `bug`, `numerics`. **Confidence**: CONFIRMED (ran), LEAD-VERIFIED.
- **Evidence**: `reachability.py:289-294`. For a case with exact `W = 1`, the function returns
  1.032. Sample count is a literal.
- **Fix**: Van Loan's matrix-exponential block method for LTI (exact to rounding); composite
  Simpson or Gauss-Legendre with a caller-set tolerance and an error estimate for LTV.
- **Accept**: closed-form cases to 1e-10; a convergence-order test; no literal sample count.
- **Compat**: results change in the third significant figure; regenerate dependants.
- **UX/DX/AX**: accuracy becomes a parameter with a reported estimate.

#### NC-10 [P1] A non-functional mock DDP solver is the library default; solver interface is duck-typed

- **Labels**: `architecture`, `bug`. **Confidence**: CONFIRMED (read).
- **Evidence**: `ddp.py:7-9,55,243-244` is a placeholder that does not optimize;
  `swing_optimizer.py:139` selects it when no solver is passed. The guard against using it
  outside tests sniffs `PYTEST_CURRENT_TEST`, which any caller can set, and is a contract
  (NC-05). The package docstring advertises DDP and swing-up capabilities that do not exist.
  `swing_optimizer.py:342-356,399-411` and `optimizer_factory.py:21-56` discover solver
  capabilities with `inspect.signature`, catch `TypeError`, and retry with different
  arguments, which also swallows genuine `TypeError`s raised inside a solver.
- **Fix**: a `TrajectoryOptimizer` `Protocol` with one `solve(problem) -> OptimizationResult`
  method; the solver is a required argument or a named registry entry; the mock moves to
  `tests/`; the docstring states only what exists.
- **Accept**: constructing `SwingOptimizer` without a solver is a `TypeError`; no
  `inspect.signature` and no `except TypeError` around solver calls; `rg -i mock src/` is
  empty.
- **Compat**: `SwingOptimizer()` with no solver currently "works" by returning garbage. It
  will raise. Changelog under "Removed", with the one-line migration.
- **UX/DX/AX**: there is one obvious way to plug in a solver, and it is typed.

#### NC-11 [P2] `execute_ztcf_intervention` never compares with `expected` and ignores its tolerance

- **Labels**: `bug`, `contracts`. **Confidence**: CONFIRMED (read).
- **Evidence**: `ztcf_contract.py:107,270-298`: `expected` and `absolute_tolerance` are
  accepted, stored and never used. The reference pin is a hard-coded git SHA string.
- **Fix**: perform the comparison and return a typed verdict; move the pin to the lock file
  that already governs companion pins; model availability as a discriminated union (N-6).
- **Accept**: a test where `expected` differs beyond tolerance returns a failing verdict.
- **Compat**: callers that relied on the comparison being absent will see failures; that is
  the defect.

#### NC-12 [P2] `ResidualMonitor` escalates late, or never, and exposes mutable state

- **Labels**: `bug`, `state-machine`. **Confidence**: CONFIRMED (read).
- **Evidence**: `residuals.py:285,313-357`: escalation needs up to 2n samples; an alternating
  over/under residual sequence resets the counters forever; mode and counters are public
  attributes.
- **Fix**: state machine N-1. Pure `step(state, residual) -> (state, events)` over frozen
  state; hysteresis defined in the transition table; a windowed exceedance fraction instead
  of consecutive counts.
- **Accept**: property test that exceedance fraction ≥ p over a window always escalates
  within the window; alternating-sequence regression test; transition diagram generated into
  the docs.
- **Compat**: `monitor.mode` stays readable and returns the enum, whose value equals the old
  string.

#### NC-13 [P2] Impact models: hard-coded limits, mislabelled intervals, a tautological residual

- **Labels**: `numerics`, `modeling`. **Confidence**: CONFIRMED (read).
- **Evidence**: 120 m/s² literal at `impact_contact_models.py:345` and
  `impact_contact_uncertainty.py:84`; a type named `ClosedInterval` that holds the sample
  minimum and maximum, not a bound; a momentum residual computed from the quantity it is
  meant to check; fixed-step integration through contact with no event localization
  (`impact_contact_models.py:237`); thresholds absolute rather than scaled; `-inf` sentinel
  margins; an O(N²) recomputation of a loop-invariant.
- **Fix**: named, sourced parameters; rename to `SampleRange` or compute a real bound;
  residual from independently integrated impulse; event detection with root-finding on the
  gap function; `ContactRegime` union (N-7).
- **Accept**: restitution test with an analytic answer; residual test that fails when a
  momentum error is injected.

#### NC-14 [P2] Numerical hygiene: finite-difference terms in the integrator loop, explicit inverses, no accuracy safeguards

- **Labels**: `numerics`, `performance`, `tech-debt`. **Confidence**: CONFIRMED (ran) for the
  figures quoted.
- **Evidence**: Coriolis and gravity terms obtained by finite differences inside the
  integration loop (error floor about 5e-11, about 950 µs per call); explicit inverses and a
  rank test in `constrained_affine_fields` (`dynamics.py:300-308`); fixed-step RK4 with no
  step-size control or energy check (0.55% energy drift in one configuration, unflagged);
  almost no logging in solvers; `assert` used for control flow; loosely typed result
  containers.
- **Fix**: analytic or RNEA-based bias terms; `solve`/`lstsq` with a condition-number check
  and a `NumericalFailure` on ill-conditioning; an optional invariant monitor on the
  integrator (AR-01) that reports drift; structured `logging` at DEBUG in solver loops.
- **Accept**: a benchmark gate on the dynamics call (TS-06); a test that an ill-conditioned
  constraint Jacobian raises `NumericalFailure`; drift reported in the result object.

### 5.2 Epic AR: library architecture

#### AR-01 [P1] No shared model, state, trajectory or integrator abstraction (split)

- **Labels**: `architecture`, `dry`. **Confidence**: CONFIRMED (read).
- **Evidence**: RK4 is implemented at least five times (`dynamics.py:252`, `golf_model.py:281`,
  `ztcf_explorer.py:108`, `ddp.py:267`, `impact_contact_models.py:237`). The planar chain is
  implemented twice (`rnea.py:127-171`, `golf_model.py:65-211`). The double pendulum exists
  three or four times (`dynamics.py:145`, `double_pendulum_affine.py`,
  `src/tools/rl_funnel_support.py:42`, `src/tangent_models/examples.py:366`). There are three
  joint-angle conventions, two "default golfer" parameter sets (`golf_model.py:47-48` against
  `swing_analysis.py:50-51`), gravity defined in five places, and trajectories passed as
  lists of tuples. `src/core/protocols.py` defines `DynamicalSystemProtocol` beside lint and
  report protocols, and the only user of it is `tests/test_protocols.py`. The real base class
  `DynamicalSystem` lives in `src/tangent_models/examples.py:66`.
- **Impact**: this is the gap between a set of studies and a modeling suite. Each duplicate
  is a place where conventions already differ.
- **Fix**, in this order, one PR each:
  1. `integrators`: `rk4_step`, `integrate(f, x0, t, method)`, returning a frozen
     `Trajectory(t, x, u)` of arrays, with an optional invariant monitor.
  2. `ControlAffineSystem` protocol: `drift(x)`, `input_matrix(x)`, `linearize(x, u)`,
     `n_state`, `n_input`, with one concrete double pendulum and one planar chain. Each
     duplicate becomes a thin alias and is then deleted.
  3. One `GolferParameters` frozen dataclass with one default, and an explicit, tested
     angle-convention converter.
  4. Physical constants from one module.
- **Accept**: one RK4, one double pendulum, one planar chain in `src/`; a cross-check test
  retained from the deleted duplicates (RNEA against Lagrangian is already in agreement to
  2e-8, keep it as the oracle); `DynamicalSystemProtocol` implemented by every model and
  consumed by solvers.
- **Compat**: old function names remain as re-exports with `DeprecationWarning`. Where two
  parameter sets differ, the PR states which pages used which and regenerates them.
- **UX/DX/AX**: a new model plugs into every solver and viewer by implementing one protocol;
  an agent asked to "add a three-link model" has exactly one place to put it.

#### AR-02 [P1] `src/tools` is a grab bag whose import has side effects

- **Labels**: `architecture`, `tech-debt`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED
  for the import side effect.
- **Evidence**: `src/tools/__init__.py:3` imports site tooling and calls
  `logging.basicConfig` at import, so importing any `src.tools.*` module reconfigures the
  host application's logging. Reusable solvers live in `*_examples.py` files; there are
  three LaTeX converters; one-off patch scripts ship in the package; duplicated controllers
  have drifted apart; several utilities are tested but have no caller.
- **Fix**: no side effects at import, anywhere (`logging.basicConfig` only inside
  `main()`). Sort contents into: library code (move to the owning package), applications
  (`apps/` with their own extras, PK-06), site tooling (`scripts/` or a `sitekit` package
  that is not shipped in the wheel), and delete the dead remainder with a list in the PR.
- **Accept**: `python -c "import src.tools.<any>"` leaves the root logger without handlers;
  an import-linter contract forbids library packages from importing application or site
  code.
- **Compat**: moved modules keep a re-export shim for one minor version.

#### AR-03 [P1] Domain packages contain site rendering and gate tooling; boundary rules have holes

- **Labels**: `architecture`. **Confidence**: CONFIRMED (read).
- **Evidence**: `evidence_presentation` and parts of `research_readiness` render site
  fragments from inside `affine_control`; the gate "framework" used by `scripts/` lives in
  the shipped package; the existing import-boundary rules do not list `golf_simulation`;
  `src/core/protocols.py` mixes dynamics, lint and report protocols.
- **Fix**: three layers with enforced direction: `affinedrift` (library: numerics, models,
  domain types), `affinedrift_evidence` or a subpackage boundary (registries, schemas,
  validation, no HTML), and repository tooling (rendering, gates) that depends on the first
  two and is not in the wheel. Enforce with import-linter in CI, including `golf_simulation`.
- **Accept**: the wheel contains no HTML or Markdown templating; import-linter contract in
  CI with zero ignores.
- **Compat**: script entry points unchanged; only import paths move, with shims.

#### AR-04 [P2] `affine_control` is 48 flat modules mixing solver core, demos, viewers and governance

- **Labels**: `architecture`, `dx`. **Confidence**: CONFIRMED (read).
- **Evidence**: one directory holds solvers, model definitions, figure generators, viewer
  exporters and governance records; there is no `__all__` and no statement of what is public.
- **Fix**: subpackages `models/`, `solvers/`, `analysis/`, `lifecycle/`, `io/`; a curated
  top-level `__init__` with `__all__` (PK-05); everything else prefixed private or documented
  as internal.
- **Accept**: an API snapshot test (`griffe` or a simple `__all__` dump) fails on unreviewed
  public-surface change.
- **Compat**: moves done with re-export shims; removed only per the deprecation policy.

### 5.3 Epic GS: golf simulation

#### GS-01 [P0] The round simulator almost never holes out

- **Labels**: `bug`, `modeling`. **Confidence**: CONFIRMED (ran).
- **Evidence**: `round_simulator.py:217-241`. Simulated 18-hole rounds scored 172 to 180 on a
  par-72 course; 140 of 144 holes across eight rounds ended at the per-hole stroke cap rather
  than in the hole. The cap is recorded as a normal score.
- **Impact**: every statistic derived from a simulated round is an artifact of the stroke
  cap.
- **Fix**: depends on GS-02 and GS-04 (rollout and putting are the causes). Independently:
  `HoleOutcome` (`HOLED`, `STROKE_LIMIT`, `ABANDONED`) so a capped hole can never be read as
  a score (state machine G-2); the round summary reports the count of non-holed holes and
  refuses to report a total if it is non-zero unless asked.
- **Accept**: with a fixed seed and the default player, at least 95% of holes end `HOLED`;
  the mean score for the default scratch-level player on the default course falls in a
  declared, sourced plausible band; a regression test fails if any hole hits the cap.
- **Compat**: score outputs change. Mark prior committed round outputs as superseded.
- **UX/DX/AX**: a simulated scorecard becomes believable; the failure mode is a typed
  outcome an agent can count.

#### GS-02 [P0] Rollout is unphysical: a lob wedge rolls further than it flies

- **Labels**: `bug`, `modeling`. **Confidence**: CONFIRMED (ran), LEAD-VERIFIED (formula).
- **Evidence**: a lob wedge carries 61 m, then rolls to 152 m on fairway and 129 m of roll on
  a green. The rolling-resistance coefficient is reused as the impact friction coefficient
  (`round_simulator.py:418`, `terrain.py:113`), so almost no horizontal speed is lost at
  landing, and spin and descent angle have no effect. `compute_bounce` accepts a coefficient
  of restitution above 1 and an upward-moving ball.
- **Fix**: a landing model with separate normal restitution and tangential impulse (sliding
  or gripping decided by the friction cone, with spin), then rolling deceleration with a
  surface-specific coefficient. Validate inputs. `BallPhase` segments (G-1).
- **Accept**: roll-to-carry ratio decreases monotonically with loft and backspin; wedge roll
  on a green is under a declared, sourced bound; kinetic energy is non-increasing across a
  bounce (property test).
- **Compat**: outputs change by design.

#### GS-03 [P1] Ball flight under-carries by 10 to 23%, and the club table disagrees with the flight model

- **Labels**: `bug`, `modeling`, `needs-source`. **Confidence**: CONFIRMED (ran) for the
  model output; PLAUSIBLE for the size of the gap, because the reference carries were quoted
  from reviewer memory.
- **Evidence**: `ball_flight.py:37-38` places the drag-crisis transition at the smooth-sphere
  Reynolds number; a dimpled ball transitions far earlier, so the model applies high drag
  across the whole playing range. The carry table in `clubs.py:192,277-280` does not match
  what the flight model produces for the same launch conditions. Landing is detected at the
  first sample below ground with no interpolation (`ball_flight.py:346-362`), and can trigger
  mid-air over falling terrain.
- **Fix**: drag and lift coefficients as functions of Reynolds number and spin ratio from a
  cited dataset, stored under `data/` with provenance; the club table generated from the
  model, or the model calibrated to a cited table, not both hand-maintained; event-located
  landing by root-finding.
- **Accept**: carries for a cited reference set within ±5%; a test that table and model agree
  within tolerance; a landing-time convergence test under step refinement.
- **Before filing**: replace the remembered reference carries with a citable source.

#### GS-04 [P1] Putting physics: wrong deceleration, putts that never stop, wrong frame, wrong slopes

- **Labels**: `bug`, `modeling`. **Confidence**: CONFIRMED (ran) for non-termination and
  capture speed; CONFIRMED (read) for the rest.
- **Evidence**: gravity along the slope is applied at full `g`, not `5/7 g` for a rolling
  sphere (`putting.py:321-322`); capture speed is 1.5 m/s while the repository's own test
  derives 1.313; on slopes above about 5% the ball never stops and leaves the green
  (`putting.py:283-303`); world coordinates are passed to a green-local surface
  (`round_simulator.py:579`); the inverse-distance-weighted slope estimate is not the
  gradient of the interpolated surface (`putting.py:111-113`).
- **Fix**: rolling-sphere dynamics; a single sourced capture criterion; a static-friction
  stopping condition and an explicit `OFF_GREEN` outcome; `PlanarGreen`/`SampledGreen` with a
  declared frame and a transform at the boundary (G-3, G-4); slope as the analytic gradient
  of the interpolant.
- **Accept**: flat-green stopping distance matches the closed form; every simulated putt
  terminates with a `PuttOutcome`; a frame test with a green placed away from the origin.

#### GS-05 [P2] Penalties, validation, immutability and performance

- **Labels**: `bug`, `performance`. **Confidence**: CONFIRMED (read); 11 s per round measured.
- **Evidence**: penalty handling at `round_simulator.py:331-335` does not apply stroke and
  distance or relief correctly; `linearize` and several constructors accept invalid input; a
  "frozen" state object holds mutable arrays; one round takes about 11 s; course geometry is
  internally inconsistent; unit-conversion constants are duplicated.
- **Fix**: rules as data (`Penalty` union); validated frozen dataclasses with read-only
  arrays; profile and vectorize the flight integrator; one units module.
- **Accept**: a rules table test; a round under 2 s on the CI runner (benchmark gate, TS-06).

#### GS-06 [P1] Round-simulator tests are tautological

- **Labels**: `testing`. **Confidence**: CONFIRMED (read).
- **Evidence**: the tests stub the flight model and assert `total_score > 0`. They pass with
  GS-01 and GS-02 present.
- **Fix**: invariant and plausibility tests: every hole terminates `HOLED`; stroke count per
  hole within a band; energy non-increasing after impact; a golden seeded round reviewed by a
  human once.
- **Accept**: reverting the GS-01 or GS-02 fix makes these tests fail.

### 5.4 Epic TL: tools

#### TL-01 [P1] RL-funnel benchmark ignores its control limit and its headline claim is a strawman

- **Labels**: `bug`, `scientific-integrity`. **Confidence**: CONFIRMED (ran), LEAD-VERIFIED
  for the ignored limit.
- **Evidence**: `rl_funnel_benchmark.py:366,378` accept `control_limit` and never apply it.
  The effort metric is computed from a quantity that is not the applied control. The claim
  that "TTCF outperforms" compares against a mis-tuned baseline; in the reviewer's run the
  passive system scored 0.025, TTCF 0.058 and the baseline 5.24, so doing nothing beat the
  proposed method. The module contains neither reinforcement learning nor a funnel.
- **Fix**: apply and test saturation; effort from the applied control; a baseline tuned by a
  stated procedure, with the passive case in the table; rename the module to what it does;
  correct any page that cites the result.
- **Accept**: a saturation test; the published table includes the passive row; the page text
  matches the table.

#### TL-02 [P2] Slack-transmission model: explicit Euler with no stability guard, dead zone implemented twice

- **Labels**: `numerics`, `dry`. **Confidence**: CONFIRMED (read).
- **Evidence**: `slack_transmission.py:108,168,188`.
- **Fix**: shared integrator (AR-01) with a step-size check against the stiffest time
  constant; one dead-zone function; `ContactState` (G-5).
- **Accept**: a step-halving convergence test; one dead-zone implementation.

#### TL-03 [P1] `sync_notebook_bridge` overwrites authored notebooks and deletes files it does not recognize

- **Labels**: `bug`, `data-loss`. **Confidence**: CONFIRMED (read).
- **Evidence**: `notebooks_bridge.py:175-177,187`.
- **Fix**: write a generated-by marker with a content hash into generated notebooks; only
  overwrite or delete files that carry the marker and whose hash matches; everything else is
  `AUTHORED` and is reported, never touched (G-7); `--dry-run` by default.
- **Accept**: a test with a hand-edited notebook that survives a sync; deletion requires an
  explicit flag.

#### TL-04 [P1] A tracked MATLAB file is corrupted, and its duplicate has diverged

- **Labels**: `bug`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED.
- **Evidence**: `matlab_code_analyzer_gui/exportCodeIssues.m:1` reads
  `function T --- exportCodeIssues` and the file contains 135 `---` sequences where `=`
  should be (a text transform applied to code). A second copy of the tool differs. The
  runner builds a MATLAB command by string concatenation, so a path containing a quote
  breaks out of the string.
- **Fix**: restore from history; one copy; pass arguments safely; add the `mlint`/`checkcode`
  step that the workflow already claims to run (CI-03 notes that step points at a missing
  script).
- **Accept**: the file parses; a CI syntax check covers tracked `.m` files, or MATLAB code is
  moved out of this repository.

#### TL-05 [P2] Tools hygiene: shared RNG, uncaught evaluator errors, wrong run instructions, checks that cannot fail

- **Labels**: `tech-debt`. **Confidence**: CONFIRMED (read).
- **Evidence**: a module-level random generator in `constants.py:37` shared by all callers;
  evaluator error handling in one app (see the private SEC-01 advisory);
  application run instructions that do not work; `verify_images` cannot return a failing exit
  code; benchmarks time re-implementations rather than the library; signal and plot modes as
  strings compared in two UIs (G-6); stringly typed tool results (G-8).
- **Fix**: pass `numpy.random.Generator` explicitly; catch and present evaluator errors;
  test the run instructions in CI by invoking `--help`; non-zero exit on failure; benchmarks
  import the library.

### 5.5 Epic EV: evidence, protocols and trust

Paths in this epic that begin with a bare package name are under `src/affine_control/`.

#### EV-01 [P0] The trust registry labels 131 companion entities "CI-Verified" from a test fixture

- **Labels**: `bug`, `scientific-integrity`, `trust`. **Confidence**: CONFIRMED (ran),
  LEAD-VERIFIED.
- **Evidence**: `evidence_presentation/generator.py:64-65,137` builds the registry input from
  a fixture with default SHAs (a `"b" * 64` digest). `evidence_presentation/projector.py:220-221`
  maps the result to the label "Pinned Companion Artifact (CI-Verified)" and the tier
  `QUALIFIED_SIMULATION`. The output is committed as
  `data/trust/generated/evidence_presentation_registry.json`. The active companion lock
  points at commit `27b6eead…` with `publication_state: "draft"`. No CI job verifies those
  entities against that pin.
- **Impact**: the site's trust layer asserts a verification that did not happen. For a
  project whose stated aim is evidence-first claims, this is the most damaging finding in the
  review, because the mechanism built to prevent overclaiming is the thing overclaiming.
- **Fix**: the generator reads the real lock and the real verification record or fails.
  Fixtures live under `tests/` and cannot be imported from `src/` (import-linter rule). The
  label is a function of the companion lifecycle state (E-8): `draft` can never project to a
  verified tier. A digest that is a repeated character is rejected at load.
- **Accept**: (1) regenerating from the current lock yields zero "CI-Verified" entities, or
  yields them only with a linked CI run identifier stored in the record; (2) a gate fails if
  the registry was built from anything other than the active lock (lock hash embedded in the
  output and checked); (3) a test asserts `publication_state != "qualified"` implies no
  qualified tier; (4) the affected pages are regenerated in the same PR.
- **Compat**: labels on published pages are downgraded. That is the fix. Note it in the
  changelog and on the trust page.
- **UX/DX/AX**: readers can rely on the badge; an agent cannot mint trust by running a
  generator.

#### EV-02 [P0] Population-validation outcomes are hard-coded strings

- **Labels**: `bug`, `scientific-integrity`. **Confidence**: CONFIRMED (ran), LEAD-VERIFIED.
- **Evidence**: `population_generalization_evidence.py:134-135` assigns the outcome fields
  from literals; changing the input data does not change them. The reported "interval" at
  `:130` is the minimum and maximum of cluster means, presented as an interval estimate. The
  output is committed and referenced from `models/population-generalization.qmd`.
- **Fix**: outcomes computed from a pre-declared decision rule stored with the protocol;
  a real interval (bootstrap over subjects, or a mixed-model interval) with its method named
  in the output; the min/max, if kept, is labelled a range.
- **Accept**: a test that perturbs the data across the decision threshold and observes the
  outcome flip; the artifact records the rule and the method; the page is regenerated.
- **Compat**: the published outcome may change.

#### EV-03 [P1] The research-readiness "registry" is minted by a fixtures module, and fixtures ship in the library

- **Labels**: `architecture`, `trust`. **Confidence**: CONFIRMED (read).
- **Evidence**: `scripts/generate_research_readiness_library.py:19` imports
  `research_readiness/fixtures.py` (`:203,267-273,326`) as the source of the committed
  registry. About 2,170 lines of fixtures live under `src/`. `_require_text` is reimplemented
  twelve times across protocol modules.
- **Fix**: registry content is data (`data/research_readiness/*.yaml` or JSON) validated
  against a schema; fixtures move to `tests/`; shared validators come from one module
  (NC-05).
- **Accept**: `rg fixtures src/` is empty; the generator's only inputs are data files; the
  generated output is byte-identical before and after the move (pure refactor PR).

#### EV-04 [P1] Authority-independence and human-governance gates accept any string

- **Labels**: `bug`, `governance`. **Confidence**: CONFIRMED (ran) for the gate; CONFIRMED
  (read) for independence.
- **Evidence**: `authority.py:72-78` treats two authorities as independent if two strings
  differ. The human-governance gate is implemented four ways;
  `HumanTierGate("TODO", "n/a", "tbd", "?", True).authorize()` returns `True`
  (`hand_wrench_evidence.py:95-101`).
- **Fix**: one `HumanGovernanceGate` (state machine E-14) whose fields are validated: an
  approval identifier matching a declared pattern, a date, a named approver from an allow-list
  file, and rejection of placeholder tokens. `authorize()` returns a `Decision` union with
  the reason. Independence is declared in data (an authority registry with organization and
  relationship), not inferred from string inequality.
- **Accept**: the placeholder call returns `Denied`; the four implementations are replaced by
  one; a test for same-organization authorities returns "not independent".
- **Compat**: records that currently pass with placeholders will fail. List them in the PR;
  each needs a real approval or a downgrade.

#### EV-05 [P1] Claim critique status is hand-maintained and disagrees with the ledger; the transition table can be bypassed

- **Labels**: `bug`, `state-machine`. **Confidence**: CONFIRMED (read).
- **Evidence**: `critique_status` on claims is edited by hand and differs from the critique
  ledger for `ad-dcr-001`. The table at `scripts/generate_claim_critique_ledger.py:26-33` is
  enforced only on one path (`:185-205`); editing the ledger file directly, or using the
  initialization path, skips it.
- **Fix**: `critique_status` is derived from the ledger and removed from stored claims (kept
  in generated output). The ledger is validated on load with `Lifecycle.replay` over each
  claim's full history, so an illegal history fails regardless of how it was written.
- **Accept**: a hand-edited illegal transition fails the gate; no stored `critique_status`
  remains in source data; `ad-dcr-001` is consistent.
- **Compat**: generated pages keep the field. Schema marks the stored field deprecated, then
  removes it in a versioned migration (EV-08).

#### EV-06 [P1] Projectors fail open to stronger tiers and invent provenance

- **Labels**: `bug`, `trust`. **Confidence**: CONFIRMED (read).
- **Evidence**: `evidence_presentation/projector.py:32-34,87,155-157,179`: unknown or missing
  inputs fall through to a default that is not the weakest tier, and provenance fields are
  filled with plausible constants when absent. `tools_catalog` defaults `maturity` to
  `"stable"`. One schema `evidence-rung` enum mixes two different ladders.
- **Fix**: total functions over enums with `match` and `assert_never`; unknown maps to the
  weakest tier or raises; missing provenance is `Unavailable(reason)` and renders as
  "provenance not recorded"; catalog default `experimental`.
- **Accept**: property test: for any input, the projected tier is no stronger than the tier
  justified by the weakest recorded fact; no string default for provenance in `src/`.

#### EV-07 [P2] Statistical defects in equipment-response, multiplicity and reachability reporting

- **Labels**: `statistics`, `scientific-integrity`. **Confidence**: CONFIRMED (read).
- **Evidence**: equipment-response analysis has defects in its test construction and emits
  constant interpretation strings regardless of the result; a Holm correction is declared in
  the protocol and never called; the reachability verdict carries no uncertainty.
- **Fix**: interpretation text generated from the computed result through a small table;
  apply the declared correction and record adjusted p-values; report an interval or a
  sensitivity range with the reachability verdict.
- **Accept**: a test where the declared family has two hypotheses and the adjusted values
  differ from the raw ones; no constant interpretation strings.
- **Before filing**: a statistician on the panel should review the specific test
  construction; the reviewer flagged it but the correct replacement is a judgment call.

#### EV-08 [P2] Schemas: formats not enforced, identity and versioning inconsistent, shapes duplicated by hand (split)

- **Labels**: `schemas`, `architecture`. **Confidence**: CONFIRMED (read).
- **Evidence**: `jsonschema` is installed without the `format` extra and five validation
  sites pass no `FormatChecker`, so `format: date-time`, `uri` and similar are not checked;
  at least fifteen versioned document types have no schema (including the DCR and ZTCF
  atlases); `$id` and version conventions vary; there are no migrations; Python dataclasses
  and JSON Schemas describe the same shapes by hand; some schemas pin a status with
  `const` (E-16).
- **Fix**: one `validate(document, schema_name)` helper with `FormatChecker` and a local-only
  registry (see SEC-04); a schema for every committed, versioned document; `$id` and
  `schema_version` conventions written down; `migrations/<name>/vN_to_vN+1.py` with a test
  per step; enums in schemas generated from Python (decision 4.2).
- **Accept**: a gate that every JSON file under `data/` with a `schema_version` validates
  against a registered schema; an invalid `date-time` fails; generated `$defs` diff clean in
  CI.
- **Compat**: validation becomes stricter. Run in report-only mode first, fix data, then
  enforce. Split: helper, missing schemas, enum generation, migrations.

#### EV-09 [P2] Snapshot store is not crash-safe, and pin reviews never expire

- **Labels**: `robustness`, `governance`. **Confidence**: CONFIRMED (read).
- **Evidence**: `programming_companion/store.py:95-97,128-148,198-216`: no writer lock, no
  fsync, unexpected subdirectories accepted, lock provenance unchecked.
  `scripts/check_companion_pins.py:40,325-342`: a review has no expiry and 14 of 22 pins are
  `review-required` while CI is green.
- **Fix**: stage, fsync, atomic rename; a lock file for writers; strict layout check;
  quarantine on mismatch (E-11). Pin state gains a derived `stale` (E-9) computed from review
  date and upstream head; the gate fails on `stale` beyond a declared age and reports
  `review-required` counts as a ratchet that may only go down (GT-03).
- **Accept**: a kill-during-write test leaves the store readable; the gate fails when a
  review is older than the policy window.
- **Compat**: CI will turn red on the existing 14 pins unless the ratchet starts at 14.
  Start it there.

#### EV-10 [P2] Promotion history cannot survive promotion; `published` is unreachable; research-releases is an unvalidated scaffold

- **Labels**: `state-machine`, `tech-debt`. **Confidence**: CONFIRMED (read).
- **Evidence**: `research_readiness/validation.py:178-182,292-295,326-332` and
  `states.py:65-68`: validation rules reject the attempt records that a promoted item would
  necessarily carry, and no transition leads to `published`. The `research-releases`
  structure has fields and no schema or transitions (E-15).
- **Fix**: attempt history append-only and valid in every state; either add the transition
  into `published` with its evidence requirement or delete the state; give the release
  scaffold a schema and a `Lifecycle`, or remove it until needed.
- **Accept**: a round-trip test promotes an item through every state with history intact;
  no unreachable states (checked by a generic `Lifecycle` reachability test, SM-01).

#### EV-11 [P3] Hardening bundle: denylist guards, flat exceptions, nondeterministic generators, duplicated sources

- **Labels**: `tech-debt`. **Confidence**: CONFIRMED (read).
- **Evidence**: guards built on denylists of bad tokens rather than allow-lists; one flat
  exception type across the evidence code; generators whose output order depends on
  filesystem or set ordering; bibliographic sources recorded in more than one place;
  transport hardening items (redirect handling, content-type checks).
- **Fix**: allow-lists; the taxonomy from NC-05; sorted, timestamp-free generator output with
  a "regenerate and diff" gate; one bibliographic source of truth.

### 5.6 Epic SEC: security

#### SEC-01 [P0] Security finding (filed privately)

- Details withheld: filed privately with the maintainers (private security advisory).

#### SEC-02 [P1] Security finding (filed privately)

- Details withheld: filed privately with the maintainers (private security advisory).

#### SEC-03 [P1] Workflow-security finding (filed privately)

- Details withheld: filed privately with the maintainers (private security advisory). The fix belongs in Repository_Management (fleet-managed workflows); see Q3 and `docs/audits/workflow-hardening-5249.md`.

#### SEC-04 [P2] Remote `$ref` retrieval, CDN scripts without SRI, permissive CSP

- **Labels**: `security`. **Confidence**: CONFIRMED (read). **Overlaps open work on #5252.**
- **Evidence**: `programming_companion/validation.py:128` validates a provider-supplied
  schema with a resolver that may fetch remote `$ref`s. `articles/rotation-converter.qmd:285-286`
  and `grip_angle_simulator.html:7` load CDN scripts with no integrity attribute. The CSP is
  delivered by `<meta>` and allows `'unsafe-inline'` (`_includes/site-head.html:34`).
  A same-origin check uses `startsWith(origin)`.
- **Fix**: a `referencing.Registry` with only local schemas and retrieval disabled; vendor or
  add SRI and `crossorigin`; move inline scripts to files and drop `'unsafe-inline'` as
  specified in `docs/audits/sri-csp-adr0002-5252.md`; compare parsed `URL.origin`.
- **Accept**: a schema with a remote `$ref` fails validation without a network call; a gate
  that every external `<script>` has `integrity`.

### 5.7 Epic SM: state-machine foundations

These drafts implement decision 4.2. Individual machines are fixed in their owning drafts;
this epic provides the shared pieces and the cross-module vocabularies.

#### SM-01 [P1] Add the `lifecycle` kernel and move the two existing tables onto it

- **Labels**: `architecture`, `state-machine`. **Confidence**: design proposal.
- **Scope**: `Lifecycle[S]`, `Transition`, `IllegalTransition`, `replay`, `to_mermaid`,
  reachability and dead-state checks, about 150 lines with no dependencies. Port
  research-readiness (E-1) and critique disposition (E-3) with no behaviour change.
- **Accept**: characterization tests written first pass unchanged after the port; a generic
  test asserts every registered lifecycle has no unreachable and no undeclared-terminal
  states (this will flag `published`, EV-10, as an expected failure to resolve); a
  `lifecycle show <name> [--json]` command lists states and legal transitions; diagrams are
  generated into the docs and diffed in CI.
- **Compat**: stored strings unchanged; schema enums byte-identical.
- **UX/DX/AX**: this is the single biggest AX gain in the document. An agent can query the
  legal next states of any governed object and gets a machine-readable refusal reason.

#### SM-02 [P1] Add `js/lib/machine.js` and `js/lib/url-state.js`; adopt in the notes workspace first

- **Labels**: `architecture`, `frontend`, `state-machine`. **Confidence**: design proposal.
- **Scope**: `createMachine` as in 4.2; `url-state` generalizing the DCR codec; JSDoc types;
  a Jest suite for the kernel. First adopter is U-1 because FE-01 needs a `conflict` state
  that cannot be expressed today.
- **Accept**: the kernel has full branch coverage; the notes workspace has no boolean state
  flags left; E2E selectors use `[data-state]`.
- **Compat**: no visual change; existing class names kept as aliases driven from
  `data-state` until CSS is migrated.

#### SM-03 [P1] One outcome vocabulary: "negative" and "null" currently mean opposite things

- **Labels**: `bug`, `scientific-integrity`, `state-machine`. **Confidence**: CONFIRMED
  (read), LEAD-VERIFIED for the literals.
- **Evidence**: the outcome tuple is redeclared in six modules, and the same words are
  assigned by different rules:

  | Module | "negative" is returned when | "null" is returned when |
  | --- | --- | --- |
  | `neural_timing_analysis.py:131-137` | the interval lies inside the ±minimum-effect band (a negligible effect was shown) | anything else (inconclusive) |
  | `equipment_response_analysis.py:307-316` | the interval lies below −threshold (an effect in the negative direction) | the interval lies inside the band (a negligible effect was shown) |
  | `reachability_protocol.py:373-378` | the point estimate got worse by the margin (no interval) | the change is within the margin |
  | `model_ladder_protocol.py:218` | treated together with "null" as "not sufficient" | same |

  So "negative" in the neural-timing module is what the equipment-response module calls
  "null", and "null" in neural timing is what equipment response calls "indeterminate". Also
  declared separately:
  `Outcome`, `LedgerStatus`, `ResultOutcome`, `HypothesisOutcome`, `ResultStatus`. The
  synthetic-data origin is spelled five ways (E-13). `EvidenceTier` and `EvidenceOrigin`
  exist both as `StrEnum` and as `Literal`.
- **Impact**: a reader or an aggregation script comparing outcomes across protocols will
  combine results that mean different things.
- **Fix**: two orthogonal enums, because two questions are being conflated:
  `HypothesisVerdict` (`SUPPORTED`, `REFUTED`, `EQUIVALENT_TO_NO_EFFECT`, `INCONCLUSIVE`,
  `NOT_EVALUATED`) and `EffectDirection` (`POSITIVE`, `NEGATIVE`, `NEGLIGIBLE`,
  `UNDETERMINED`). Each module maps its current
  strings through `LEGACY_ALIASES` with an explicit per-module table reviewed by a human,
  since the same string maps differently depending on its source module.
- **Accept**: one definition of each enum in `src/`; a table in the docs showing every legacy
  string per module and its mapping; cross-protocol summaries use only the new types; no
  `Literal` duplicate of an existing enum.
- **Compat**: stored files keep their strings. The module-aware reader is the compatibility
  layer. A later schema version (EV-08) writes the unambiguous form.

#### SM-04 [P2] Publication and maturity vocabulary: `validated` and `experimental` each mean two things

- **Labels**: `state-machine`, `docs`. **Confidence**: CONFIRMED (read).
- **Evidence**: `experimental` is a maturity level for pages and tools, while
  `evidence_class: experimental` (from an experiment) maps to `VALIDATED_EVIDENCE`. Only about
  33 `.qmd` pages carry a front-matter `status`.
- **Fix**: `Maturity` (`DRAFT`, `EXPERIMENTAL`, `STABLE`, `DEPRECATED`) and `EvidenceClass`
  (`EMPIRICAL`, `SIMULATION`, `ANALYTIC`, `NONE`) with no shared words; the reader-facing
  label for `EMPIRICAL` is not "experimental"; a gate requiring `status` on every page, with
  a ratchet for the existing gap.
- **Accept**: no value shared between the two enums; rendered badges reviewed for the
  ambiguity; page-status coverage ratchet in place.

#### SM-05 [P1] Typed solver and analysis results: `SolveStatus`, `OptimizationResult`, `Trajectory`, `SwingPhase`

- **Labels**: `architecture`, `state-machine`. **Confidence**: design proposal backed by
  NC-03, NC-07, NC-08.
- **Scope**: the tagged-union half of decision 4.2 for machines N-2, N-5, N-8: frozen result
  types shared by LQR, iLQR and the swing optimizer; `SwingKinematics`/`SwingDynamics`
  returned by pure functions with the current `SwingAnalysis` object kept as a facade;
  `SwingPhase` with `phase_at(s)` exported into the frame JSON consumed by the viewers so
  Python and JavaScript stop deriving phases separately.
- **Accept**: every solver returns `OptimizationResult`; `converged` is derived everywhere;
  the viewers read phase from data; mypy exhaustiveness (`assert_never`) on `SolveStatus`.
- **Compat**: facade and derived properties as described in 4.2.

#### SM-06 [P2] Golf simulation phases and outcomes as types

- **Labels**: `state-machine`, `modeling`. **Confidence**: design proposal backed by GS-01,
  GS-02, GS-04.
- **Scope**: `BallPhase` with typed trajectory segments, `HoleOutcome`, `Stroke` union,
  `LieState`, `PuttOutcome` (machines G-1 to G-4).
- **Accept**: a shot is a list of segments each with a phase; the round summary is built from
  outcomes, not from a counter.

#### SM-07 [P2] Repository-process lifecycles: derive status from facts instead of hand-editing it

- **Labels**: `process`, `state-machine`, `ax`. **Confidence**: CONFIRMED (read) for the 49
  stuck entries.
- **Evidence**: 49 development-log entries remain `in_review` after their PRs merged (P-2).
  SPEC rows, change fragments and deferred-work records each carry a hand-set status.
- **Fix**: status that mirrors an external fact (PR merged, tag exists) is computed by a
  script from that fact and never stored; where storing is required, the writer is the
  automation that observed the fact. Hand edits of derived fields fail a gate.
- **Accept**: the 49 entries are reconciled by script; a gate recomputes derived statuses and
  fails on drift.
- **Compat**: the log format keeps the field; it becomes generated.

### 5.8 Epic PK: packaging and public API

#### PK-01 [P1] The distribution installs a top-level package named `src`

- **Labels**: `packaging`, `architecture`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED.
- **Evidence**: `pyproject.toml:6,43-45`. 319 files import `from src.…`. After
  `pip install affinedrift`, `import affinedrift` fails and `import src` succeeds, colliding
  with any other project that made the same choice.
- **Fix**: a real import package, `affinedrift`, under `src/affinedrift/` (the directory
  `src` becomes a layout directory, not a package). Subpackages keep their names:
  `affinedrift.affine_control`, `affinedrift.core`, and so on. A codemod rewrites imports. A
  compatibility package `src` that re-exports with a `DeprecationWarning` is kept in the
  repository (not in the wheel) for one release so in-flight branches and `.qmd` pages keep
  working.
- **Accept**: in a clean virtual environment with the wheel installed and the repository not
  on `sys.path`, `import affinedrift` works and `import src` fails; all 29 `sys.path` hacks
  and the `PYTHONPATH=.` requirement for gates (GT-05) are gone.
- **Compat**: the largest mechanical change in this document. It cannot fit under 500 lines.
  Either request the `large-pr-approved` label for one codemod PR that contains nothing but
  the generated rewrite, or land the shim first and migrate by directory. See open question
  Q1.
- **UX/DX/AX**: `pip install` gives a usable library; agents stop needing to know about
  `PYTHONPATH`.

#### PK-02 [P1] Library code reads repository files through `Path(__file__).parents[N]`

- **Labels**: `packaging`, `bug`. **Confidence**: CONFIRMED (read) for the 18 sites;
  PLAUSIBLE that each fails from a wheel (not executed).
- **Evidence**: 18 sites, for example `ztcf_explorer.py:51-53` and `option_a_trace.py:23`,
  resolve `data/` and `schemas/` relative to the source tree. Package data is not declared in
  the build configuration.
- **Fix**: data the library needs ships as package data and is read with
  `importlib.resources`; data that belongs to the site stays in the repository and is passed
  in as an argument by the script that needs it. Library functions take paths or file
  objects; they do not discover the repository.
- **Accept**: `rg "parents\[" src/` is empty; PK-03's test exercises each previously affected
  entry point from an installed wheel.

#### PK-03 [P1] The "installed wheel" smoke test does not install the wheel

- **Labels**: `packaging`, `testing`. **Confidence**: CONFIRMED (read).
- **Evidence**: `scripts/smoke_test_installed_wheel.py:103,131-132` unzips the wheel and sets
  `PYTHONPATH`. It never runs `pip install`, so missing dependencies, missing package data
  and bad metadata all pass.
- **Fix**: build sdist and wheel; create a fresh virtual environment; `pip install` the
  wheel; run from an empty temporary directory; import the public API, run the CLI
  `--version` and one numerical example; repeat from the sdist.
- **Accept**: deleting a runtime dependency from `pyproject.toml` makes the test fail;
  removing a package-data file makes it fail.

#### PK-04 [P1] `requires-python >= 3.11` is false: the code uses 3.12-only syntax

- **Labels**: `packaging`, `bug`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED for the
  count.
- **Evidence**: 42 PEP 695 `type` statements in `src/`, which are a syntax error on 3.11.
  CI does not run 3.11. `CONTRIBUTING` says Python 3.8+.
- **Fix**: decide the floor (recommended: 3.12, since the code already depends on it), state
  it once in `pyproject.toml`, and test the floor and the newest supported version in CI.
  Generate the version statement in docs from `pyproject.toml`.
- **Accept**: a CI matrix job on the minimum version; no other document states a version.
- **Compat**: raising the declared floor is a correction, not a break: 3.11 never worked.

#### PK-05 [P2] No public API, no CLI, no stability policy

- **Labels**: `architecture`, `dx`, `ax`. **Confidence**: CONFIRMED (read).
- **Evidence**: no `__all__`, no `[project.scripts]` despite 24 modules with a `__main__`
  block and 203 scripts; no SemVer statement, no deprecation policy; three ADRs in total.
- **Fix**: a curated public surface in `affinedrift/__init__.py`; an `affinedrift` console
  command with subcommands (`simulate`, `lifecycle`, `gates`, `validate`), each with `--json`
  output and documented exit codes; `docs/policies/api-stability.md` (what is public, SemVer,
  one-minor deprecation window, how to deprecate); an ADR for each decision in section 4.2
  and for PK-01.
- **Accept**: API snapshot test (AR-04); `affinedrift --help` in the wheel smoke test;
  every subcommand has a `--json` schema under `schemas/cli/`.
- **UX/DX/AX**: a stable, discoverable command surface is what lets an agent use the suite
  without reading its source.

#### PK-06 [P2] Dependencies: four surfaces, three tool-version sets, GUI code with no extras (split)

- **Labels**: `packaging`, `supply-chain`. **Confidence**: CONFIRMED (read).
- **Evidence**: CI installs `ruff==0.15.6 black==26.3.1 mypy==1.19.1`; `requirements.txt`
  pins `0.17.3`, `26.10.1`, `2.4.1`; pre-commit pins a third set. The hashed lock file is
  used only by Docker; CI and deploy install unhashed. Runtime dependencies include site
  tooling (`requests`, `bs4`). PyQt6 (11 files), Streamlit (5) and Tkinter (2) are imported
  with no extras declared. `requirements.txt` mixes runtime, development and site needs.
  Dependabot does not cover every ecosystem and its `reviewers:` entry contradicts the
  no-human-reviewer policy. `package.json` lists `jsdom` as a runtime dependency and lacks
  `"private": true`.
- **Fix**: `pyproject.toml` is the only declaration: minimal runtime dependencies, extras
  `gui`, `apps`, `site`, `dev`; one lock (`uv lock` or `pip-compile --generate-hashes`) used
  by CI, deploy and Docker with `--require-hashes`; tool versions in one place that
  pre-commit and CI both read; Dependabot groups per ecosystem.
- **Accept**: a gate that tool versions agree across CI, lock and pre-commit; CI installs
  with hashes; `pip install affinedrift` pulls no GUI or scraping packages.
- **Compat**: `requirements.txt` kept as a generated file for one release.

### 5.9 Epic RL: release and deploy

#### RL-01 [P1] The release workflow has never run, and there are five version numbers

- **Labels**: `release`. **Confidence**: CONFIRMED (read).
- **Evidence**: `release.yml` has no runs; the `v1.0.1` release has zero assets. Versions:
  `pyproject.toml` 1.0.9, `VERSION` 1.0.1, `package.json` 1.0.0, `SPEC.md` 1.0.9 with a
  separate "Spec 1.0.300", and a `CHANGELOG` section headed `[2.0.0]`. No sdist, SBOM,
  attestation or tag-against-version check.
- **Fix**: one source (`pyproject.toml`, or the tag via `setuptools-scm`); everything else
  generated or deleted; the release workflow builds sdist and wheel, runs PK-03 against the
  built artifacts, produces an SBOM and a build-provenance attestation, checks that the tag
  equals the version, and uploads assets. Exercise it with a release candidate before
  relying on it. Release lifecycle P-4 recorded in one manifest.
- **Accept**: a gate that all version statements agree; a dry-run of the workflow on every
  PR that touches it; an `rc` release with assets and attestation exists.
- **Compat**: decide which number is true first (open question Q2).

#### RL-02 [P1] Deploy has no rollback or preview, and change collation drives a third of commits on `main`

- **Labels**: `release`, `ci`. **Confidence**: CONFIRMED (read): 20 of the last 40 deploy
  runs succeeded; 67 of the last 200 commits on `main` are collation commits; merge-queue
  runs failed 22% of the time.
- **Evidence**: `deploy-website.yml` grants `id-token: write` and `pages: write` to the whole
  workflow, has `|| true` at `:129`, keeps no last-good artifact, and has no preview
  deployment. Each collation commit triggers a full CI run and a deploy.
- **Fix**: job-level permissions; retain the last successful Pages artifact and add a manual
  "redeploy last good" workflow; post-deploy smoke check that triggers it automatically;
  PR preview builds as artifacts; collate change fragments at release time, or mark
  collation commits to skip deploy and heavy CI (P-1, P-6).
- **Accept**: a failed post-deploy check restores the previous site without a human;
  collation commits no longer deploy; deploy success rate is tracked as a ratchet.
- **Note**: classify the 20 failures first. If most are runner infrastructure, the fix is in
  the fleet, not here.

### 5.10 Epic CI: CI integrity

Workflow paths are under `.github/workflows/`.

#### CI-01 [P0] The required check "Reject hosted runner routing" is satisfied by a job that runs `echo "Bypass"`

- **Labels**: `ci`, `integrity`, `fleet`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED.
- **Evidence**: `ci-standard.yml:896-907` defines a job whose name is identical to the real
  guard in `local-only-runner-guard.yml:44` and whose only step is `echo "Bypass"`. The real
  guard runs only for PRs that touch workflow paths and for `merge_group`. Branch protection
  matches on the check name, so on every other PR the required check is reported green by the
  placeholder.
- **Impact**: the pattern is a known workaround for "a required check that is path-filtered
  never reports". The risk is not this one check; it is that a green required check no longer
  implies the guard ran, and that the same pattern can be copied for any other check.
- **Fix**: run the real guard on every PR (it is cheap) and remove the placeholder; or make
  the guard a job inside the always-running workflow with an internal path condition that
  reports "skipped, not applicable" as its own conclusion under the same job, so there is one
  producer of the check name.
- **Accept**: exactly one job in the repository produces each required check name (add a gate
  that parses workflows and fails on duplicate job names across files); no step named or
  echoing "Bypass".
- **Note**: this looks like a fleet-level decision that may be deliberate. It is drafted as
  P0 because it is a gate that does not gate, but the panel should treat it as a question to
  the owner (Q3), not as an accusation.

#### CI-02 [P1] CI type-checks `src/tools` and two scripts only, with four error codes disabled

- **Labels**: `ci`, `typing`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED.
- **Evidence**: `ci-standard.yml:378`. The numerical packages, where shape and unit mistakes
  are most costly, are not type-checked. Root documents claim strict mypy.
- **Fix**: `mypy src/` with a per-module strictness table in `pyproject.toml`; a baseline of
  current errors as a ratchet that may only go down (GT-03); new modules strict from the
  start; `scripts/` added after `src/`. Correct the documents until the claim is true.
- **Accept**: CI runs mypy on all of `src/`; the error count is recorded and enforced as a
  ratchet; documents state the measured state.
- **Compat**: no code change needed to turn it on with a baseline.

#### CI-03 [P2] Gates that cannot fail

- **Labels**: `ci`, `integrity`. **Confidence**: CONFIRMED (read).
- **Evidence**: `continue-on-error` at `ci-standard.yml:279,397,418`, `ci-benchmarks.yml:160`,
  `link-checker.yml:47,61`; `|| true` at `ci-standard.yml:472` and `deploy-website.yml:129`;
  a MATLAB check step that points at a script that does not exist; `website-lint` missing
  from `quality-gate.needs` (`ci-standard.yml:828`); `bandit` installed and never invoked;
  `spec-check` documented as blocking but not required; `paths-ignore` on a required
  workflow, so some PRs never receive the required check.
- **Fix**: each site becomes one of three explicit kinds: blocking; advisory with a visible
  annotation and an owner; or deleted. No silent third state. Advisory steps write a summary
  line so their failure is seen.
- **Accept**: a workflow lint (GT-01 can host it) that fails on `continue-on-error` or
  `|| true` without an adjacent `# advisory: <reason> <owner>` comment; every job listed in
  the docs as blocking is in `quality-gate.needs`.

#### CI-04 [P2] Runner mutation, stale triggers and cache-seed state

- **Labels**: `ci`, `fleet`. **Confidence**: CONFIRMED (read).
- **Evidence**: `ci-standard.yml:457` removes dpkg locks with `sudo rm` on a shared
  self-hosted runner; workflows carry triggers for branches and events that no longer exist;
  the inventory of workflows in `.github/` documentation has drifted; the Quarto cache seed
  is reused with no input-hash key (P-7); Dependabot gaps (PK-06).
- **Fix**: no host mutation from a job (wait for the lock with a timeout, or run in a
  container); remove dead triggers; generate the workflow inventory; key caches on input
  hashes and log hit or miss.
- **Accept**: `rg "sudo rm" .github/` is empty; the inventory is generated and diffed.

### 5.11 Epic DOC: documentation

#### DOC-01 [P1] Onboarding documents contradict each other and the tooling

- **Labels**: `docs`, `dx`, `ax`. **Confidence**: CONFIRMED (read).
- **Evidence**: one document says `ruff format`, CI enforces Black, and 111 files would be
  reformatted by `ruff format`; "run `mypy .`" against CI-02; Python 3.8+ against PK-04;
  reviewer policy stated two ways; directories referenced that do not exist. `AGENTS.md` is
  51 kB and includes a retired Jules architecture, C++ and MATLAB standards for a repository
  with neither as a product, and a "PR Compiler" consolidation flow that conflicts with the
  owner's "never consolidate" rule. `CLAUDE.md` references `.logging-standard.md` and
  `.dry-improvements.md`, which are missing. Development-environment entry points disagree
  (Docker, devcontainer, bare venv).
- **Impact**: an agent that follows the documents faithfully does the wrong thing. This is
  the most direct AX defect in the repository.
- **Fix**: one short `AGENTS.md` (target under 8 kB) that contains only repository-specific,
  currently true instructions and links to generated references; every command in it is
  produced from the gate manifest (GT-01) and exercised in CI; fleet-wide policy is linked,
  not copied; `CLAUDE.md` and `CONTRIBUTING.md` include or link the same source.
- **Accept**: a gate that every repository path and command quoted in the root documents
  exists and exits zero with `--help` or a dry run; no statement of Python version, formatter
  or type-check scope outside the generated block.
- **Compat**: `AGENTS.md` may be fleet-synced. If so the change belongs upstream (Q3).

#### DOC-02 [P1] `SPEC.md` is 80% append-only log, with stale normative sections and duplicate keys

- **Labels**: `docs`, `process`. **Confidence**: CONFIRMED (read).
- **Evidence**: most of the file is change rows; normative sections describe behaviour that
  has changed; row keys repeat; two version numbers appear in it (RL-01).
- **Fix**: split into a normative specification that is reviewed like code and a generated
  change log built from `changes/` fragments (P-3). The spec-freshness gate checks the
  normative part against code facts (public API snapshot, CLI schema, lifecycle tables)
  instead of requiring a new row per PR.
- **Accept**: the normative spec has no dated rows; the change log is generated; the gate
  compares against generated facts.
- **Compat**: the current "every source PR adds a SPEC row" rule is replaced. That is a
  process change needing owner approval (Q4).

#### DOC-03 [P2] `docs/api-reference.md` documents symbols that do not exist; three ADRs for a project this size

- **Labels**: `docs`. **Confidence**: CONFIRMED (read).
- **Evidence**: `DDPSolver`, `compute_residual`, `SwingState`, `TrajectoryResult`,
  `DynamicsProtocol`, `CostProtocol`, `BallFlightModel`, `DoublePendulum` are documented and
  absent from `src/`. `docs/testing-guide.md` is stale in the same way.
- **Fix**: generate the API reference from docstrings of the public surface (PK-05) with
  `quartodoc` or `griffe`, and run doctests; delete the hand-written file; write ADRs for the
  decisions in this document as they are accepted.
- **Accept**: the reference is generated in CI and fails on a missing symbol; doctests run.

#### DOC-04 [P2] Repository weight and tracked machine-local files

- **Labels**: `repo-hygiene`. **Confidence**: CONFIRMED (read).
- **Evidence**: 333 MiB pack; multi-megabyte screenshots; tracked
  `.benchmarks/Windows-CPython-3.14-64bit` and `.jules/*.md`.
- **Fix**: stop tracking machine-local output; size limits in pre-commit for new binaries;
  large reference media in release assets or LFS. Do not rewrite history without an explicit
  owner decision.
- **Accept**: a pre-commit size gate; the listed paths are untracked and ignored.

### 5.12 Epic FE: frontend

Paths are under `js/` unless stated.

#### FE-01 [P0] Notes workspace: a stale tab overwrites newer notes

- **Labels**: `bug`, `data-loss`, `frontend`. **Confidence**: CONFIRMED (read),
  LEAD-VERIFIED.
- **Evidence**: `notes-workspace.js:345-349` saves the in-memory text on `visibilitychange`.
  There is no `storage` event listener and no version check. Sequence: open tab A and tab B;
  type in B; switch to A and away again; A writes its older copy over B's. Restore and clear
  also lose text (`:123-135,419-424`): restore replaces the current text with no undo, and
  clear has no recovery.
- **Impact**: silent loss of what the user wrote. This is the only user-authored data the
  site holds.
- **Fix**: store `{version, updatedAt, text}`; on save, re-read and compare the version; if
  it changed, enter `conflict` (state machine U-1) and show both copies with a choice; listen
  for `storage` events and update clean documents live; keep the previous revision for one
  undo of restore and clear; versioned storage key with a migration from the current format.
- **Accept**: a Playwright test with two pages in one context reproduces the sequence and
  ends with no text lost; a unit test for each transition in the document machine; existing
  stored notes load after the migration.
- **Compat**: reads the old key and format, writes the new one, keeps the old one until the
  first successful save.
- **UX/DX/AX**: the user sees `saved`, `saving`, `conflict` and `error` states; tests assert
  on `data-state`.

#### FE-02 [P1] Pop-out Save runs in the opener's realm and fails when the opener is gone

- **Labels**: `bug`, `frontend`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED.
- **Evidence**: `notes-workspace.js:316-318` dereferences `window.opener` from the pop-out.
  If the original tab was closed or navigated, Save throws and the text exists only in the
  pop-out's textarea.
- **Fix**: the pop-out is a peer: it reads and writes storage itself with the same module
  and the same conflict handling as FE-01, and coordinates through `storage` events or a
  `BroadcastChannel`. Open with `noopener`.
- **Accept**: a test that closes the opener and saves from the pop-out.

#### FE-03 [P1] Service worker: the offline page can be evicted, slow networks become failures, updates skew versions

- **Labels**: `bug`, `frontend`, `offline`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED
  for eviction.
- **Evidence**: `service-worker-utils.js:10-22` trims the cache first-in-first-out to 100
  entries with no exemption, so `/offline.html` and the shell can be removed; after that,
  offline navigation has nothing to show. `:30-77` gives network-first requests 3 seconds and
  then treats them as failed, which on a slow connection serves stale or offline content
  while the network would have answered. `skipWaiting` with `clients.claim` swaps the worker
  under open pages, so a page can run old JavaScript against new cached assets.
- **Fix**: a separate, never-trimmed precache for the offline page and shell; trim only the
  runtime cache, least-recently-used; on timeout, serve cache if present but let the network
  request finish and update the cache, and only show offline when there is neither; replace
  unconditional `skipWaiting` with an "update available, reload" prompt (U-2), or version
  asset URLs so skew is harmless.
- **Accept**: unit tests for trim (the offline page survives 1,000 insertions) and for the
  slow-network path; a Playwright offline test after cache pressure.
- **Compat**: bump the cache name and delete old caches on activate.

#### FE-04 [P1] Bibliography fallback search never debounces, and it is the production path

- **Labels**: `bug`, `frontend`, `a11y`. **Confidence**: CONFIRMED (read), LEAD-VERIFIED.
- **Evidence**: `bibliography.js:40-46`: the fallback debounce never assigns its `timeout`
  variable, so `clearTimeout` clears nothing and every keystroke runs a full filter. The
  shared debounce helper it falls back from is not loaded on that page, so the fallback is
  what runs in production. Related: result count is not announced; no empty state.
- **Fix**: import one debounce from a shared module (FE-07); `loading` and `empty` states
  (U-5); a polite live region with the result count, updated after the debounce.
- **Accept**: a fake-timer test that ten keystrokes produce one filter pass; an axe check on
  the page.

#### FE-05 [P1] History links are stored by basename and 404 from subdirectories

- **Labels**: `bug`, `frontend`. **Confidence**: CONFIRMED (read).
- **Evidence**: `history.js:33,234` stores only the file name of each visited page and builds
  links relative to the current page.
- **Fix**: store site-root-relative paths; resolve with the site base URL; versioned storage
  with a migration that drops entries it cannot resolve (U-24); guard every storage access
  (private mode throws).
- **Accept**: a test that visits a page in `articles/`, opens history from a page in another
  directory and follows the link.

#### FE-06 [P1] Accessibility defects in shared components

- **Labels**: `a11y`, `frontend`. **Confidence**: CONFIRMED (read).
- **Evidence**: viewers write to an `aria-live` region on every animation frame
  (`motion-clip-viewer.js:92,109`, `swing-viewer.js:109-113`, `arm-viewer.js:158,176`), which
  floods screen readers; the lightbox replaces an image's alternative text with "Zoom image"
  (`ui-components.js:426-429`); dialogs lack correct role, labelling, focus trap or focus
  return; `forms.js:162-164` adds landmark roles to many elements; a keyboard-modality body
  class duplicates `:focus-visible` (U-13); several animations ignore
  `prefers-reduced-motion`.
- **Fix**: announce on pause, on scrub end and at phase changes only; the lightbox keeps the
  original `alt` and puts "zoom" in the control's accessible name; native `<dialog>` with
  `showModal()`; remove the extra landmarks; delete the modality class; a reduced-motion
  media query in the shared playback module (FE-08).
- **Accept**: axe at zero serious or critical findings on a page of each template in light
  and dark themes; a test that the live region changes at most once per second during
  playback.

#### FE-07 [P2] Three module systems, no lint or type check, duplicated behaviour code (split)

- **Labels**: `frontend`, `architecture`, `dx`. **Confidence**: CONFIRMED (read).
- **Evidence**: classic scripts, ES modules and CommonJS-for-Jest coexist; there is no ESLint
  and no `tsc --checkJs`; physics engines load as classic scripts and declare colliding
  top-level names (`drift-control-sandbox.js`, `ztcf-explorer.js`); debounce, focus trap,
  disclosure, playback and history code each exist more than once; dead code remains.
- **Fix**: ES modules everywhere, loaded with `type="module"`; `js/lib/` for shared pieces
  (`machine`, `url-state`, `debounce`, `focus-trap`, `disclosure`, `playback`, `storage`);
  ESLint flat config and `tsc --checkJs --noEmit` in CI, starting from a baseline ratchet;
  Jest reads ES modules natively.
- **Accept**: no top-level `var`/`function` globals in `js/` apart from one documented
  namespace; one implementation of each shared behaviour; lint and type check in CI.
- **Compat**: classic-script globals that pages rely on are kept as a thin shim module until
  the pages are migrated.

#### FE-08 [P2] Widgets: no loading or error states, parity gaps with Python, animation and canvas defects

- **Labels**: `frontend`, `numerics`. **Confidence**: CONFIRMED (read).
- **Evidence**: JavaScript-to-Python numerical parity is tested for three of five engines;
  animation loops do not clamp `dt` and keep running in hidden tabs, so returning to a tab
  integrates one very large step; canvases ignore `devicePixelRatio`; a synchronous RK4 run
  on every input event; widgets show nothing while loading and nothing on failure; the
  `AffineDriftWidgets` registry is used inconsistently.
- **Fix**: one `createPlayback` (U-22) with `dt` clamp, `visibilitychange` pause and
  reduced-motion support; one `createWidget` wrapper that provides `loading`, `error` and
  `ready` states and registers with the registry; device-pixel-ratio-aware canvas helper;
  debounce or move heavy integration to `requestIdleCallback` or a worker; parity fixtures
  generated from Python for all five engines.
- **Accept**: parity tests for five engines with a stated tolerance; a test that a
  60-second hidden-tab gap produces a bounded state change; every widget root has a
  `data-state`.

#### FE-09 [P2] Page-wide costs and fragile global hooks

- **Labels**: `frontend`, `performance`. **Confidence**: CONFIRMED (read). **Overlaps open
  issue #5253 for math rendering.**
- **Evidence**: every page pays for notes, search-badge and feedback fetches whether or not
  they are used; the search lazy loader has no failure state and monkey-patches
  `document.addEventListener`; `navigation.js:438-469` overrides `offsetTop` and runs two
  scroll-spies; theme handling is two-state and duplicated (U-14); `localStorage` access is
  unguarded and unversioned; local metrics grow without bound (U-25).
- **Fix**: load features on first interaction or when their root element exists; the search
  loader becomes a four-state machine with retry (U-4); one scroll-spy built on
  `IntersectionObserver`; theme as `system`/`light`/`dark` in one module; one `storage`
  module with try/catch, versioned keys and size caps.
- **Accept**: a performance budget (script bytes and request count on a plain article page)
  enforced in CI; no assignment to DOM prototype properties in `js/`.

#### FE-10 [P2] Frontend tests exercise copies of the code, and E2E checks can pass on an empty page

- **Labels**: `testing`, `frontend`. **Confidence**: CONFIRMED (read).
- **Evidence**: several Jest suites test functions re-implemented inside the test file
  instead of importing the shipped module; there is no coverage threshold; 14 Playwright
  checks are wrapped in `if (await locator.count() > 0)` and so pass when the element is
  absent; 15 use `waitForTimeout`; Chromium only; no tests for notes conflict, service-worker
  trimming, or offline behaviour.
- **Fix**: tests import the real modules (enabled by FE-07); a coverage threshold with a
  ratchet; replace vacuous guards with `expect(locator).toBeVisible()`; replace sleeps with
  web-first assertions; add Firefox and WebKit for a smoke subset; add the missing
  high-risk tests listed in FE-01 and FE-03.
- **Accept**: a lint rule forbidding `waitForTimeout` and `count() > 0` guards in `tests/`;
  mutation of a shipped function fails a Jest test.

### 5.13 Epic TS: test adequacy

Headline numbers: 684 Python test files, 6,688 tests, about 100,000 lines; 663 files flat in
`tests/`; 244 files import `src`, 157 import `scripts`, 214 only read repository content;
about 3,300 assertions of the form `assert "<string>" in`.

#### TS-01 [P0] Six mutants of the iLQR backward pass survive the test suite

- **Labels**: `testing`, `numerics`. **Confidence**: CONFIRMED (ran).
- **Evidence**: on a copy of the repository, six mutations of the backward pass (sign flips
  in the gain computation and zeroed feedback gains) were applied one at a time; the iLQR
  tests reported 57 passed each time. `tests/test_ilqr_solver.py:23,56,88` replace
  `_backward_pass` with a monkeypatch, so the function under test is not executed in those
  tests. No mutation testing runs anywhere.
- **Impact**: the solver could be broken by a one-character change and CI would stay green.
  The correctness evidence that does exist (agreement with LQR on a double integrator) was
  produced by the reviewer, not by the suite.
- **Fix**: oracle tests that run the real backward pass: (1) on a linear-quadratic problem,
  one iLQR iteration equals the Riccati solution to 1e-10; (2) the gradient of the cost with
  respect to controls from the backward pass matches finite differences; (3) cost decreases
  monotonically on a standard nonlinear problem. Then `mutmut` or `cosmic-ray` on
  `ilqr_solver.py`, `lqr.py`, `reachability.py`, `correction_authority_evaluator.py`,
  `rnea.py`, `dynamics.py`, run nightly, with a mutation-score ratchet.
- **Accept**: the six listed mutants are killed; a mutation score is recorded for the six
  modules and may only go up.
- **UX/DX/AX**: an agent editing a solver gets a failing test when it breaks the mathematics,
  which is the feedback loop agents most depend on.

#### TS-02 [P1] Coverage measures `src` only, without branches, against a floor 17 points below the measured value

- **Labels**: `testing`, `ci`. **Confidence**: CONFIRMED (read).
- **Evidence**: CI passes `--cov=src`, overriding the configured `["src", "scripts"]`;
  branch coverage is off; `fail_under` is 75 against a measured 92.6; `PYTHONPATH: src` is
  set in CI, which makes a second import root; the critical-module coverage gate is loose and
  duplicated; 28 `src` modules are never imported by any test.
- **Fix**: branch coverage on; one coverage configuration in `pyproject.toml` and no
  overriding flags; the floor set from the measured value as a ratchet; per-package floors
  with higher values for numerical modules; `scripts/` measured separately; the 28
  unimported modules either tested or deleted (cross-check with AR-02's dead list).
- **Accept**: CI reports branch coverage for `src` and for `scripts`; the ratchet file
  records both.

#### TS-03 [P1] About 1,034 tests (15.6%) never execute repository code

- **Labels**: `testing`, `tech-debt`. **Confidence**: CONFIRMED (ran): static import analysis
  over the collected tests.
- **Evidence**: 83 `*_rigor.py` files and others assert properties of Python, NumPy or
  constants defined inside the test. They pass regardless of the state of the repository.
- **Fix**: classify each as (a) convert to test the library function it re-implements, (b)
  move to documentation as a worked example with a doctest against the library, or (c)
  delete. A collection-time check fails any new test module that imports nothing from
  `affinedrift`, `scripts` or a repository data loader.
- **Accept**: the count of such tests is a ratchet starting at the measured value and ending
  at zero; the collection check is active for new files.
- **Compat**: the reported test count falls. That is the intended, honest result; reset the
  count baseline (TS-05) in the same change.

#### TS-04 [P1] Change-detector tests pin prose and ticket numbers

- **Labels**: `testing`, `tech-debt`. **Confidence**: CONFIRMED (read).
- **Evidence**: about 3,300 `assert "<literal>" in <file text>` assertions; files such as
  `tests/test_ops_doc_5317.py` assert that a document contains particular sentences and issue
  numbers. They fail on rewording and pass on wrong content.
- **Impact**: high maintenance cost for near-zero defect detection, and they train agents to
  edit the test string to match, which is the opposite of the intended discipline.
- **Fix**: replace with structural checks: front matter validated against a schema; required
  sections by identifier; links and cross-references resolved; values compared with their
  generating data. Keep a literal assertion only for legally or scientifically required
  wording, tagged with a reason.
- **Accept**: a ratchet on the count of prose-literal assertions; each remaining one carries
  a `# required-wording: <reason>` marker.

#### TS-05 [P2] Marker taxonomy, network guard and test-count baseline are not real

- **Labels**: `testing`, `ci`. **Confidence**: CONFIRMED (read).
- **Evidence**: 10 to 11 declared markers are never used; the network guard in
  `tests/conftest.py:137,146-150` does not block connections as written;
  `BASELINE_TEST_COUNT: 2282` against about 6,700 collected; 23 unconditional skips; 36 tests
  with no assertion; a stale lint exemption for `test_critical_physics_fixes.py`.
- **Fix**: `--strict-markers`; derive `unit`/`integration`/`content` from directory
  (TS-06); block sockets with `pytest-socket` or a correct fixture, opt-in per test; the
  baseline derived from the last green run on `main`, or removed; a gate on unconditional
  skips and assertion-free tests.
- **Accept**: a test that opens a socket without the marker fails; unused markers removed.

#### TS-06 [P2] Structure, speed, property tests and benchmarks (split)

- **Labels**: `testing`, `dx`. **Confidence**: CONFIRMED (read).
- **Evidence**: 663 files in one directory; 272 definitions of a repository-root constant;
  about 10 minutes serial; property-based tests are 1.2% of the suite; benchmarks never gate
  and some time re-implementations (TL-05).
- **Fix**: `tests/unit/<package>/`, `tests/integration/`, `tests/content/`, `tests/gates/`
  mirroring the source tree; one `repo_root` fixture; `pytest-xdist` with a measured worker
  count for the runners; Hypothesis strategies for systems, trajectories and schemas shared
  from `tests/strategies/`; benchmark gates on five named kernels with a tolerance band.
- **Accept**: a unit subset that runs in under 60 seconds locally and is documented as the
  inner loop; no test file directly under `tests/` except `conftest.py`.
- **Compat**: file moves only; use `git mv` so history follows. Many small PRs by package.

#### TS-07 [P2] Quarto-dependent tests probably skip in CI

- **Labels**: `testing`, `ci`. **Confidence**: PLAUSIBLE. The runner image was not inspected.
- **Evidence**: 18 files and 145 tests skip when the `quarto` executable is absent.
- **Check before filing**: read the skip summary of a recent `main` CI run.
- **Fix if confirmed**: a dedicated job with Quarto installed where a skip of these tests is
  a failure (`-p no:skip` equivalent via a `--require-quarto` option).
- **Accept**: CI log shows these tests ran.

### 5.14 Epic GT: gates and agent tooling

Headline numbers: 203 scripts, 164 `main()` functions, 112 argparse parsers, 18 with `--json`.

#### GT-01 [P1] There is no gate framework and no machine-readable gate list

- **Labels**: `architecture`, `dx`, `ax`, `ci`. **Confidence**: CONFIRMED (read).
- **Evidence**: 55 to 70 gates exist only as YAML steps. There is no way to ask "which gates
  apply to this change and how do I run them". Output formats and exit codes differ per
  script. A developer or agent learns a gate exists when CI fails.
- **Fix**: `gates.toml` listing each gate: identifier, command, inputs (path globs), kind
  (`blocking` or `advisory`), owner, expected duration. A runner,
  `affinedrift gates run [--changed] [--id X] [--json]`, that executes the applicable gates
  locally with uniform result records (`pass`, `fail`, `not_applicable`, `unavailable`,
  `misconfigured`, matching P-12) and exit codes (0 pass, 1 fail, 2 usage or configuration).
  CI calls the same runner, so the workflow shrinks to a matrix over the manifest. A small
  `Gate` base (argument parsing, `--json`, finding records with `file:line`) that scripts
  adopt incrementally.
- **Accept**: `gates run --changed` on a PR branch reproduces the CI verdict for the gates it
  covers; `gates list --json` is the source for the documentation table (DOC-01); a test
  that every gate in the manifest exists and supports `--json`.
- **Compat**: existing script entry points keep working; the manifest wraps them first and
  the base class is adopted over time. CI changes one gate at a time.
- **UX/DX/AX**: the inner loop becomes "run the gates for my change" with structured
  findings. For agents this replaces guessing from a 51 kB document.

#### GT-02 [P1] Named gates that check nothing

- **Labels**: `ci`, `integrity`. **Confidence**: CONFIRMED (read).
- **Evidence**: `check_dry_adoption.py:37-41` passes unconditionally on its main path; the
  contract-coverage gate scans zero files because its glob matches nothing;
  `check_security_audit.py` verifies that a document exists, not that an audit ran; the
  tech-debt budget does not count `TODO` or `FIXME`; budgets have been loosened in past
  changes.
- **Fix**: every gate has a self-test: a fixture that must fail it and one that must pass.
  The manifest runner (GT-01) reports the number of inputs examined and treats zero as
  `misconfigured`.
- **Accept**: a meta-test that runs each gate against its failing fixture and expects exit 1;
  no gate reports success with zero inputs.

#### GT-03 [P1] Five independent baseline ratchets with no monotonicity rule

- **Labels**: `ci`, `process`. **Confidence**: CONFIRMED (read).
- **Evidence**: five baseline files in different formats; nothing prevents a PR from raising
  a budget; fingerprint sets can collide so a new finding hides behind an old one; the
  claim-audit inventory can be reset with `--initialize-from-manifest`.
- **Fix**: one `ratchets.toml` with direction per metric; a gate that compares against the
  merge base and fails on any loosening unless the PR carries a `ratchet-loosen` label and a
  reason recorded in the file; fingerprints that include path and a stable content hash;
  reset commands require an explicit `--i-understand-this-resets-history` style flag and
  write an audit record.
- **Accept**: a test PR that loosens a budget fails; one that tightens passes and updates the
  file automatically.
- **Compat**: start each ratchet at today's measured value so nothing turns red on adoption.

#### GT-04 [P2] Parsing helpers duplicated across gates have already drifted

- **Labels**: `dry`, `tech-debt`. **Confidence**: CONFIRMED (read).
- **Evidence**: `strip_latex_comments` exists four times with different behaviour on escaped
  percent signs; front-matter, citation-key and cross-reference parsing are each implemented
  several times. Two gates can disagree about the same file.
- **Fix**: `sitekit.parsing` (not shipped in the wheel, AR-03) with one implementation of
  each, with Hypothesis round-trip tests; gates import it.
- **Accept**: one definition of each helper; a characterization test recording where the old
  copies disagreed and which behaviour was chosen.

#### GT-05 [P2] Gates need an undeclared `PYTHONPATH`, are exempt from lint and types, and 57 scripts are orphaned

- **Labels**: `tech-debt`, `dx`. **Confidence**: CONFIRMED (read).
- **Evidence**: gates fail without `PYTHONPATH=.` (resolved by PK-01); `scripts/` is exempt
  from the complexity rule and from mypy; 57 scripts have no caller in workflows, hooks,
  documents or other scripts; some Python files have hyphenated names and cannot be imported
  or tested; 19 scripts have no tests; 41 of 46 subprocess calls have no timeout; 94
  non-atomic file writes; 14 file opens without an encoding.
- **Fix**: delete or archive the orphans with a list in the PR; rename hyphenated files;
  bring `scripts/` under lint and types with a baseline ratchet; shared `run()` with a
  default timeout and `write_atomic()` in the gate base.
- **Accept**: every script is referenced by the manifest, a workflow or a document; the
  lint exemption is removed or reduced to a named list.

#### GT-06 [P2] Agent tooling: hooks enforce the wrong formatter, missing tools pass, handoff and deferred-work schemas conflict

- **Labels**: `ax`, `tooling`, `fleet`. **Confidence**: CONFIRMED (read).
- **Evidence**: the agent hook manifest runs `ruff format` while CI enforces Black (111 files
  differ); a hook whose tool is not installed reports success; the vendored
  `handoff_validator` is not wired in and the repository fails it; two deferred-work files
  use incompatible schemas (P-9, P-10); `scripts/automerge_guard.py` drops the reason when it
  refuses to arm (P-5); `requeue_stalled_merges` can loop.
- **Fix**: hooks call the gate runner (GT-01) so there is one definition of "formatted";
  result states per P-12 so a missing tool is `unavailable`, not `pass`; wire or remove the
  handoff validator; one deferred-work schema and lifecycle; the guard returns a `Verdict`
  with a reason and a bounded retry count.
- **Accept**: with Black uninstalled the hook reports `unavailable` and a non-zero exit; a
  refused arm prints the reason in `--json`.
- **Note**: `automerge_guard.py` is byte-synced from Repository_Management. Its part of this
  draft must be filed there (Q3).

## 6. Overlap with open issues and prior audits

Checked against open issue titles on 2026-11-09. Bodies were not all read; the panel should
confirm before filing.

| Draft | Existing item | Relationship |
| --- | --- | --- |
| SEC-04, FE-09 (CSP, SRI) | `docs/audits/sri-csp-adr0002-5252.md` (#5252) | Same work. Fold the three new sites into it; do not file separately. |
| SEC-03, CI-03 | `docs/audits/workflow-hardening-5249.md` (#5249) | Partly covered. File only what that document lacks: CI-01 and the gate-neutering list. |
| SM-02, FE-08 (URL state) | `docs/audits/widget-url-hash-state-spec-5255.md` (#5255) | This review adopts that specification as the URL half of decision 4.2. |
| PK-02, EV-08 | `docs/audits/asset-manifest-provenance-spec-5251.md` (#5251) | Adjacent. Schema and provenance conventions should be decided once. |
| FE-09 (math cost) | #5253 math-rendering cost | Same. Reference only. |
| EV-01 to EV-06 | #5248 evidence-first platform audit epic | These are concrete defects under that epic. File as children. |
| FE epic | #5171 UX overhaul epic | FE-06 and FE-08 are children; FE-01 to FE-05 are bugs and should not wait for the overhaul. |
| NC-11 | #5122 ZTCF and ZVCF | Check whether the contract comparison is already in scope. |
| AR-01 | #5187, #5186 tangent-space; #5172 humanoid | New models should land on the AR-01 protocol, so AR-01 step 2 should precede them. |
| (none) | #5459 to #5465, #5550, #5209, #5203, #5093 | No overlap found. |
| Whole document | `docs/audits/AFFINEDRIFT_ADVERSARIAL_REVIEW.md`, `docs/assessments/adversarial_review_2026_05_21.md` | Earlier reviews. Not re-derived here; a panel member should diff their open items against this list. |

## 7. Open questions for the panel and the owner

- **Q1. PK-01 size.** The import rename touches 319 files. Options: (a) one generated codemod
  PR with the `large-pr-approved` label; (b) shim first, then per-directory PRs under 500
  lines (about 15 PRs, with both import styles live for the duration). Recommendation: (a),
  because a half-migrated tree is worse for agents than one large mechanical diff, and the
  diff is verifiable by re-running the codemod.
- **Q2. Which version is true?** 1.0.9 (`pyproject.toml`), 1.0.1 (last tag) or 2.0.0
  (changelog heading). Recommendation: treat the next release as 2.0.0, since PK-01, NC-01
  and NC-02 change import paths and published numbers.
- **Q3. Fleet-owned files.** CI-01, SEC-03, DOC-01 (`AGENTS.md`), GT-06 (`automerge_guard`)
  and parts of CI-04 concern files synced from Repository_Management. Should those drafts be
  filed there, with this repository only tracking adoption? Recommendation: yes.
- **Q4. SPEC process.** DOC-02 replaces "every source PR adds a SPEC row" with a normative
  spec plus generated change log. This changes a rule in the repository `CLAUDE.md`. Owner
  decision.
- **Q5. Corrections to published results.** NC-01, NC-02, NC-03, GS-01, GS-02, EV-01, EV-02
  and TL-01 change numbers or labels on published pages. Is a public corrections note
  wanted, and should affected pages carry an "under correction" banner until regenerated?
  Recommendation: yes to both; it is consistent with the project's evidence-first position.
- **Q6. Golf simulation scope.** Is `golf_simulation` meant to be a calibrated simulator or
  an illustrative model? If illustrative, GS-01 to GS-04 can be met more cheaply by labelling
  outputs as such and removing score claims. The drafts assume calibrated.
- **Q7. Severity of CI-01.** P0 as drafted, on the principle that a required check must
  imply its guard ran. If the placeholder is a deliberate, documented fleet pattern, P2 with
  a documentation fix.
- **Q8. Mutation testing cost.** TS-01 proposes nightly mutation runs on six modules. The
  self-hosted runners are bandwidth- and I/O-constrained. Is a weekly run on one runner
  acceptable?

## 8. Suggested sequencing

Ordered so that each wave makes the next one safer, and so that corrections to published
claims are not held behind refactors. Every item is one issue and one PR unless marked
(split).

**Wave 0: stop the bleeding (independent, small, no design decision needed).**
SEC-01 (private advisory), EV-01, EV-02, NC-03, FE-01, TL-03, TL-04, CI-01 (after Q3/Q7),
SEC-02.

**Wave 1: make the safety nets real, before changing numerics.**
TS-01 oracle tests (they should fail against nothing yet and then protect Wave 2), NC-05,
CI-02 with a baseline, PK-03, PK-04, GT-02, GT-03 (ratchets start at measured values),
CI-03.

**Wave 2: correct the numbers, each with artifact regeneration.**
NC-01, NC-02, NC-09, NC-07, NC-08, NC-04, GS-02, GS-04, GS-01, GS-03, TL-01, EV-07. Publish
the corrections note (Q5) with this wave.

**Wave 3: foundations.**
SM-01, SM-02, SM-03, SM-05, PK-01 (after Q1), PK-02, AR-01 (split), GT-01, RL-01.

**Wave 4: consolidation on the foundations.**
AR-02, AR-03, AR-04, PK-05, PK-06, EV-03 to EV-06, EV-08 to EV-10, SM-04, SM-06, SM-07,
FE-02 to FE-10, TS-02 to TS-06, GT-04 to GT-06, DOC-01 to DOC-04, RL-02, CI-04, NC-06,
NC-10 to NC-14, GS-05, GS-06, TL-02, TL-05, SEC-03, SEC-04, EV-11, TS-07.

Dependencies that constrain the order:

| Draft | Needs first | Reason |
| --- | --- | --- |
| NC-01, NC-02, NC-08 | TS-01 oracle tests | Fix numerics under tests that can detect a wrong fix |
| GS-01 | GS-02, GS-04 | Holing out depends on rollout and putting |
| EV-05, EV-10, EV-09 | SM-01 | They use `Lifecycle.replay` |
| FE-01, FE-02 | SM-02 | The `conflict` state needs the machine kernel |
| FE-10 | FE-07 | Tests can import real modules only once they are modules |
| GT-05, PK-03 | PK-01 | `PYTHONPATH` removal and a real install test need a real package |
| DOC-01 | GT-01 | Commands in the docs are generated from the gate manifest |
| NC-10, SM-05 | AR-01 step 1 | Shared `Trajectory` and integrator |
| EV-08 enum generation | SM-01, SM-03 | Schemas generated from the enums |

What "done" looks like for the stated goal, as checkable facts:

1. `pip install affinedrift` in a clean environment gives an importable package, a CLI with
   `--json`, and a passing example, on the declared minimum Python.
2. Every number on a published page can be regenerated by one command, and the generating
   function has an oracle or property test and a recorded mutation score.
3. Every trust label is reachable only through a recorded, legal lifecycle transition from
   real inputs.
4. Every lifecycle in section 4.3 has a named type and a table, and
   `affinedrift lifecycle show` lists it.
5. `affinedrift gates run --changed` reproduces the CI verdict locally.
6. The root onboarding document is under 8 kB and every command in it is executed in CI.

## 9. Method and provenance

- Six reviewers worked in parallel on: numerics and control core; golf simulation and tools;
  evidence, protocols and registry; packaging, CI, release and documentation; frontend; tests
  and gate scripts. Each was instructed to be adversarial, to cite `file:line`, to run a
  probe where one was possible, and to label confidence.
- The lead reviewer re-read the cited source for the items marked LEAD-VERIFIED: NC-01,
  NC-02, NC-03, NC-05, NC-09, CI-01, CI-02, FE-01, FE-02, FE-03 (eviction), FE-04, EV-01,
  EV-02, SEC-01 (code path), TL-01 (ignored limit), TL-04, AR-02 (import side effect), GS-02
  (formula), PK-01, PK-04 (count), SM-03 (literals).
- Everything else rests on a single reviewer's reading or run. Line numbers refer to
  `df3c2a0ec` and will drift.
- Checked and found correct, so that the panel does not re-open them: RNEA against the
  Lagrangian formulation (2.1e-8); iLQR against exact finite-horizon LQR on a linear-quadratic
  problem; unforced `GolfModel` energy conservation (about 1e-10 over 0.2 s); the
  `quality-gate` fan-in logic; companion transport URL policy and size bounds; absence of
  `shell=True`; absence of attacker-influenced HTML sinks in `js/`.
- This review was produced by an AI system (Claude) at the owner's request. It has not been
  reviewed by a human. Treat every finding as a claim to verify, in the order of section 3.
