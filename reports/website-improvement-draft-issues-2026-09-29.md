# AffineDrift Website: Critical Review and Draft Improvement Backlog

Date: 2026-09-29
Status: **Draft for Board review.** Nothing in this document has been filed as
a GitHub issue. Every epic and issue below is a proposal awaiting approval,
re-scoping, or rejection.
Repository revision reviewed: `main` at `9af8faa`.

---

## 0. How to Read This Document

| Part | Contents                                                                            |
| ---- | ----------------------------------------------------------------------------------- |
| 1    | Scope, method, and limits of this review                                            |
| 2    | Assessment of the external "Comprehensive Technical & Architectural Review Summary" |
| 3    | Independent review of the site (findings with file-level evidence)                  |
| 4    | Guiding principles for the improvement programme                                    |
| 5    | Decisions the Board must make before implementation                                 |
| 6    | Epic and issue index (one table)                                                    |
| 7    | Draft epics and issues (full text, ready to paste into GitHub)                      |
| 8    | Proposed sequencing and milestones                                                  |
| 9    | Success measures                                                                    |
| 10   | Relationship to already-open work (do not duplicate)                                |

**Issue conventions.** Each draft issue carries a stable draft ID
(`WEB-<epic>.<n>`), a proposed priority (`P0` blocking / `P1` high / `P2`
medium / `P3` low), proposed labels following the fleet taxonomy
(`type:*`, `complexity:*`, `judgement:*`, `tier:*`), a problem statement with
evidence, the proposed change, testable acceptance criteria, and dependencies.
Tier labels follow the fleet rule: design, contested, or unclassified work is
`tier:strong`; well-specified implementation is `tier:cli`; mechanical work is
`tier:ollama`.

---

## 1. Scope, Method, and Limits

- **Scope.** The public website at affinedrift.com as defined by
  `_quarto.yml` (327 `.qmd` sources plus rendered Markdown), its supporting
  CSS/JS, CI and deploy workflows, content governance data (`data/trust/`),
  notebooks, datasets, and the `src/` code that could feed interactive
  features.
- **Method.** A source-level audit of the repository, split into five
  review streams (information architecture and onboarding, content and
  epistemic governance, interactivity and reproducibility, technical
  execution, and existing plans). The key claims from each stream were then
  checked against the source.
- **Limits.**
  - The live site could not be fetched from the review environment (the
    network egress proxy blocks it), and Quarto is not installed there, so
    no pages were rendered.
  - Findings about rendered behaviour (prev/next links, lazy math,
    breadcrumbs, the published `grip_angle_simulator.html`) are inferred from
    configuration and are marked **verify on live site**.
  - Word counts come from `wc -w` on the sources, not from rendered pages.
- **Relationship to earlier reviews.** This builds on
  `reports/website-companion-review-2026-08-29.md` (Packages A–E) and
  `reports/site-trust-surface-audit.md`. It does not re-propose work those
  reports already routed to open issues; see §10.

---

## 2. Assessment of the External Review Summary

The external summary is directionally sound and its headline diagnosis is
correct: the scholarship is strong, and the entry barrier for a newcomer is
very high. Checked against the source, however, it:

- overstates some strengths;
- understates the interactivity gap;
- is out of date on bit-rot defences and mobile math;
- misses several areas a professional research site must cover.

### 2.1 Point-by-Point

<!-- prettier-ignore -->
| # | External claim | Verdict | Evidence and correction |
| --- | --- | --- | --- |
| 1.1 | The core formalism is $\dot{x} = f(x) + g(x)u$ | **Accurate, with a notation defect the review inherited** | `NOTATION.md:342-346` makes uppercase $G(x)$ normative and forbids lowercase $g(x)$. The home page (`index.qmd:44`) uses lowercase, so the reviewer copied an inconsistency from the site's most-visited page. Lowercase also appears in `articles/superposition.qmd`, `ch03_superposition.qmd`, and 12 critique files. See WEB-11.4. |
| 1.2a | A "rigorous paradigm shift" that "bypasses hand-wavy golf instruction" | **Overstated** | The site's own scope statements (`pages/about.qmd:33`, `index.qmd:21`) deny that the model decomposition identifies muscle action, intent, or coaching advice. Framing the site as a replacement for instruction contradicts its epistemic position and would invite justified criticism. The accurate framing is that it offers a formal vocabulary and a set of model-conditioned diagnostics that instruction language lacks. |
| 1.2b | "Exceptional self-awareness" about limitations | **Accurate in intent. Execution is thinner than the review implies.** | The governance design is excellent. Populated content is sparse: `data/trust/claim_registry.json` holds **one** claim (`ad-dcr-001`), and the critique ledger has 35 critiques, of which 27 are Open, 8 Responded, and 0 Resolved. Heavy disclosure has also become a readability cost: "does not establish" appears 122 times across reader-facing pages. See §3.1 and Epic 12. |
| 1.2c | Explicit falsifiers and counterfactual tracking "mimic pre-print servers" | **Partly accurate** | There is a strong per-claim falsification atlas only for proximal–distal (`articles/proximal-distal-falsification-atlas.qmd`, 10 claims). Nothing equivalent exists for ZTCF, DCR, or ICC. There are no DOIs, no citation metadata, and no external review pathway, so the pre-print analogy does not yet hold. See Epics 5 and 7. |
| 1.3 | The in-vivo mapping gap | **Accurate and important** | The site acknowledges it, but mainly as disclaimers. "EMG" appears **zero** times in theory Parts 1–5, `affine-nature-golf-swing`, `zero-torque-counterfactual`, `controllability-drift-ratio`, `inverse-dynamics`, and `inverse-dynamics-inference`. All 8 research protocols are `simulation-ready` on synthetic data, and their falsifiers test process rather than science. See WEB-05.5 and WEB-05.6. |
| 2.1 | Rigid taxonomy, no onboarding funnel, no separation of "immutable core theorems" from working papers | **Accurate on the funnel. The remedy needs care.** | Most onboarding parts already exist but are disconnected: personas (`config/personas.yml`), "In Layman's Terms" blocks, `pages/overview.qmd`, a 12k-word glossary, and an accessible companion. The fix is mainly surfacing and wiring, not new writing. The phrase "immutable core theorems" should **not** be adopted. The site correctly avoids asserting immutability, so the right mechanism is a maturity and evidence tier (Epic 4), not a canon/non-canon split. |
| 2.2 | High risk of bit rot; needs continuous automated validation | **Largely out of date** | Validation already exists: a daily link checker (`.github/workflows/link-checker.yml`), a post-deploy verifier of every public page (#4406/#4407), a zero-baseline link gate (#4410), and SHA-pinned provider links. What remains is narrower: external-link checks do not block, the axe scan is warn-only (#4139), 10 browser tests are excluded (#4140), and a few stale root artefacts remain. See Epics 9 and 13. |
| 2.3 | Dense equations may break on mobile | **Largely addressed** | `styles.css` (~L3285-3335) wraps display math in horizontal-scroll containers with viewport font scaling, and `js/accessibility.js:295` makes scrollable math keyboard-focusable. What remains: overflow rules duplicated in `custom.scss`; inconsistent equation numbering (`tags: 'ams'` plus Quarto `{#eq-}`); lazy typesetting with an unverified effect on print and in-page find. See Epic 11. |
| 2.4 | Static; interactive widgets would help | **Accurate, and understated** | The rotation converter is the only in-site interactive model. The 42 notebooks in `notebooks/geometry_of_motion/` are two-cell stubs (≈750 bytes each), yet book pages show "Open in Colab" buttons. `pyproject.toml:7` has `packages = []`, so `src/` is not installable. The core theory pages (DCR, ZTCF, superposition) have **no figures at all**, even though `src/affine_control/` already contains the double-pendulum, DCR, and ZTCF code needed to drive them. See Epic 6. |
| 3 | Assessment matrix | **Mostly fair; see the revised matrix below** | — |

### 2.2 Material the External Review Missed

1. **Researcher infrastructure is absent.** There is no `CITATION.cff`,
   Zenodo DOI, ORCID, Google Scholar metadata, or "cite this page". Ten
   articles, including theory Parts 1–5, use `date: today`, so the displayed
   date is the build date. Issue #3604 (citation metadata) is closed, yet no
   artefact exists.
2. **Naming and identity collisions.**
   - "Volume II" refers to two different works.
   - The theory series goes by three names.
   - The manifesto exists as two pages.
   - `affine-nature-golf-swing` and `theory-part1` both claim to be "Part I".
3. **Accessibility gate is not enforced.** Serious/critical axe findings do
   not fail CI, and dark mode and mobile viewports are never scanned
   (`.github/workflows/ci-standard.yml:623-640`).
4. **SEO defects.**
   - `robots.txt` blocks `/site_libs/`, the render-critical CSS/JS.
   - There is no per-page scholarly structured data.
   - The home page title is "Home".
5. **Privacy.** Google Fonts and YouTube embeds expose visitor IP addresses to
   third parties. The datasets page loads thumbnails from a third-party
   screenshot service (`mini.s-shot.ru`).
6. **Editorial voice.** Repository-internal governance vocabulary leaks into
   reader prose: "governed" (72 occurrences), "qualified" (82),
   "provenance" (52), "protected" (16), "fail-closed" (8). Even the
   "In Layman's Terms" block in Theory Part 1 speaks of "autonomous dynamics"
   and "the declared input channel" and is collapsed by default.
7. **Content duplication and maintenance load.**
   - Proximal–distal material exists in five forms.
   - Tangent-space material exists in three.
   - A single author maintains 327 source pages plus six LaTeX books.
8. **The About page carries little authority.** A 318-word biography with no
   photo, CV, publications, ORCID, or statement of funding and conflicts,
   titled "About & Contact" while a separate Contact page also exists.
   Contact email addresses are inconsistent (`404.qmd:29` vs
   `pages/contact.qmd:47`).

### 2.3 Revised Assessment Matrix

<!-- prettier-ignore -->
| Dimension | External rating | Revised rating | Main constraint |
| --- | --- | --- | --- |
| Scientific and mathematical rigour | High | **High (long-form); uneven (short-form)** | Core theory pages lack figures, worked examples, and dated versions; the model-to-human mapping has no measurement plan attached to core claims |
| Epistemic honesty | Very High | **Very High in design; Medium in coverage** | 1 registered claim; 0 resolved critiques; caveat density hurts comprehension |
| Information architecture | Dense / expert-level | **Fragmented** | The parts exist but are disconnected; naming collisions; menus mix categories |
| Lay accessibility | (not rated) | **Low** | No start page, no audience routing, no site glossary; lay blocks written in jargon |
| Interactive reproducibility | Static | **Static, with misleading affordances** | Colab buttons open stubs; `src/` not installable |
| Researcher infrastructure | (not rated) | **Low** | No DOIs, citation metadata, real dates, or per-article changelog |
| Technical execution | (not rated) | **High engineering, soft enforcement** | axe warn-only, no performance budget, SEO/privacy defects |
| Visual communication | (not rated) | **Low** | Almost no conceptual diagrams on core pages; one 1.8 MB GIF; no animation of the central idea |

---

## 3. Independent Review

Findings are grouped by the reader's journey. Severity: **H**igh, **M**edium,
**L**ow.

### 3.1 First Contact (a Lay Visitor or Golfer)

- **H: The first call to action is a textbook.** The only primary CTA is
  "Start with The Physics of Golf" (`index.qmd:24`), and that book's preface
  reaches an equation in its second section.
- **H: The home page's second section is an equation.** The home page leads
  with a publication-state key (`index.qmd:29-37`), before the visitor knows
  what the site is for, and its next section is $\dot{x} = f(x) + g(x)u$.
- **H: No routing by audience.** The six personas in `config/personas.yml`
  appear only on `resources/learning-paths.qmd`. None of them is a golfer,
  coach, or curious non-specialist, which is the audience the Board wants to
  reach.
- **H: The best on-ramps are hidden.**
  - "How a Golf Swing Carries Energy" (the accessible companion) is item 8 of
    11 in the Read menu.
  - `pages/overview.qmd` (scope, evidence standards, reading paths) is in
    neither the navbar nor the home page.
  - The glossary is a book appendix, linked from four places.
- **M: Plain-language material is jargon-hardened.** The "In Layman's Terms"
  blocks are collapsed by default and have absorbed the same caveat
  vocabulary as the technical text. They appear on only four core pages
  (theory Part 1, affine-nature, ZTCF, proximal–distal article).
- **M: The shortest learning path takes 40–80 hours.** There is no 5-minute,
  30-minute, or 3-hour on-ramp.
- **M: Tone reads as defensive.** For example: "availability is not a
  guarantee for undeclared conventions or arbitrary invalid inputs"
  (`pages/tools.qmd`). The honesty is valuable; its placement in running
  prose is not. Caveats belong in one consistent, structured "Scope and
  limits" component (Epic 3), stated once and precisely.

### 3.2 Orientation and Navigation (All Readers)

- **H: The navbar mixes categories** (`_quarto.yml:155-222`).
  - "Read" has 11 items mixing books, hubs, series, a catalogue, learning
    paths, critiques, and the bibliography.
  - "Connect" mixes site information with five resource sub-pages.
  - Resources are split across three menus.
  - Reference Books and Research Reviews are in no menu at all.
- **H: Identity collisions.**
  - Volume II means two different works.
  - The theory series has three names.
  - The manifesto has two pages, and the navbar target has no series sidebar.
  - Two pages each title themselves "Part I".
- **M: Prev/next is probably off.** The config comment promises series
  prev/next links, but `page-navigation: true` is not set anywhere.
  **Verify on live site.**
- **M: Stubs are presented as content.**
  - Book Reviews (Planned, empty).
  - Four "research review" stubs, mostly Google Scholar search links, one of
    them promoted as a hub card.
  - `The_Geometry_of_Motion/quarto/volume2.qmd` (24 words; it includes a file
    that is excluded from render).
- **M: Category labels do nothing.** `categories:` are set on every page but
  never drive a listing, and some values are wrong (the manifesto is labelled
  `critique`).
- **L: Search is at Quarto defaults**, with an unverified `SearchAction`
  target.

### 3.3 Reading a Technical Page (Researcher)

- **H: Researchers cannot cite the work.** There are no citation metadata or
  DOIs, and the displayed dates are build dates (`date: today` on 10 core
  articles).
- **H: Core theory pages have no figures.** `controllability-drift-ratio`,
  `zero-torque-counterfactual`, and `superposition` contain zero images and
  zero interactive inputs. For work whose central idea is a vector-field
  decomposition, that is the single largest pedagogical gap.
- **M: Page structure is inconsistent.** Only the monograph has an
  `abstract:`. Prerequisites, key takeaways, "last reviewed", and version
  history are absent from article pages.
- **M: Canonical versions are unclear.** The standalone proximal–distal
  article (13k words) overlaps the monograph (≈73k words) with no
  canonical/superseded marker. `affine-nature-golf-swing` (12k words) calls
  itself the "unabridged monograph" of the theory series.
- **M: Citation health.**
  - 183 BibTeX keys are duplicated across the 7 globally loaded `.bib` files,
    so conflicts resolve silently.
  - 33 DOIs are stored under different keys with conflicting metadata (for
    example `Penner2001` vs `penner2003`).
  - 22 orphaned `*-bibliography.md` files, at least one linked from a
    rendered page (`proximal-distal-energy-transfer.qmd:1461`), which is a
    probable broken link.
- **M: Equation numbering is inconsistent.** `tags: 'ams'` makes MathJax
  number raw LaTeX environments, while Quarto numbers `{#eq-}` equations;
  five files use the raw scheme.
- **M: Notation drift.** $g(x)$ vs $G(x)$. DCR is expanded three different
  ways, and the DCR page's slug does not match its title.
  `nomenclature.tex` equates drift with "passive" and input with "active
  (muscular)", which `NOTATION.md` explicitly rejects.

### 3.4 Evidence and Critique (Reviewer)

- **H: The claim registry holds one claim**, and its reader projection
  (`_includes/generated/evidence-presentation-summary.qmd`) is included on
  no page. Its link target is raw JSON.
- **H: ZTCF pages carry no critique annotations.** `zero-torque-counterfactual`
  and `theory-part2` have none, despite three ZTCF-specific critiques (mapped
  only to affine-nature). The proximal–distal works have no ledger entries.
- **M: Critique triage is incomplete.** 3 critiques have severity "Unknown".
  The Critical "Tip Mass Omission" critique against Part 1 is Open.
- **M: Filename undermines neutrality.** `critiques/DEFENSE_STRATEGY` works
  against the neutral stance the site otherwise keeps.
- **M: No external review.** There is no peer-review or outside-review
  pathway: no reviewer invitation, open-review record, or preprint plan.

### 3.5 Doing Something (Learner, Integrator)

- **H: Colab buttons lead to empty notebooks.** The honest disclaimer does
  not make that a good experience.
- **H: No reader-facing path to run anything.** There is no installable
  package, Binder, devcontainer, or downloadable notebook.
- **M: The datasets page is thin.**
  - Four third-party cards with truncated descriptions, no licence, size,
    schema, or download link.
  - The site's own schema-validated data (`data/ztcf/`,
    `data/research_protocols/`, `schemas/`) is not listed.
- **M: The programming companion looks unfinished.** `programs.qmd` uses IDs
  as titles for all 70 records, and every engine's maturity is
  "Unspecified".
- **L: A stray executable cell.** `drift-components-wrench-double-pendulum.qmd:510`
  contradicts the CI claim that there are "no executable cells".

### 3.6 Platform Quality

- **H: axe is warn-only.**
  - It reported 247 serious/critical violations on 163 routes (#4139).
  - It scans only light theme at `desktop-small`.
  - 10 browser tests are excluded (#4140), including WCAG AA contrast in
    both themes.
  - CI runs Chromium only.
- **H: No runtime performance budget** (no Lighthouse or equivalent). Pages
  with math load ≈1 MB of MathJax.
- **M: SEO and deploy hygiene.**
  - `robots.txt` blocks `/site_libs/` and sets an ignored `Crawl-delay`.
  - Stale root `sitemap.xml` and `feed.xml`.
  - The canonical host is split between apex and `www`.
  - `_includes/article-schema.html` is dead code, and would be broken if
    used.
- **M: Privacy and weight.**
  - Google Fonts and YouTube embeds without `nocookie`.
  - `metrics.js` is preloaded on every page but used on one.
  - A 1.8 MB GIF.
- **M: Build.** The ≈14-minute full render runs twice with no cache.
- **L: Cruft and maintainability.**
  - `legacy-pages/`, the unused `_includes/home-sidebar-content.html`, and
    broken preview scripts.
  - Internal Markdown lives inside the Quarto output directory `docs/`.
  - Both `.Jules/` and `.jules/` exist, which collides on case-insensitive
    filesystems.

### 3.7 Programme-Level Observations (Easy to Overlook)

1. **Governance machinery has outrun the governed content.** The schemas,
   ledgers, generators, and verifiers are professional-grade, yet the claim
   registry has one entry. The next unit of effort buys far more if it goes
   into populating and _showing_ claims, figures, and plain-language
   explanations than into further verification layers.
2. **Surface area is a liability for a single maintainer.** Each duplicate
   rendition (five proximal–distal forms, three tangent-space forms, two
   manifestos) multiplies correction work and risks contradiction.
   Consolidation (Epic 2) is a quality measure, not a cosmetic one.
3. **Honesty needs a single home on each page.** Repeating caveats in every
   paragraph dilutes them. One precise, structured "What this shows / what it
   does not show" block, placed consistently, is both more honest and more
   readable.
4. **Accessibility for lay readers comes from layering, not dilution.** Every
   core page can keep its full rigour if it also offers a short, jargon-free
   opening layer, an intuition layer with a picture or widget, and then the
   formal layer. This is how the Board's goal ("don't dumb it down, make it
   accessible") can be met structurally (Epic 3).

---

## 4. Guiding Principles for the Programme

1. **Layer, never dilute.** Every core topic offers an opening in plain
   language, then intuition, then the formal treatment, then evidence, then
   code. The formal layer stays as rigorous as it is today.
2. **One canonical home per idea.** Other renditions either become
   derivative views generated from, or linked to, the canon, or they are
   retired.
3. **State once, precisely.** Evidence state and limitations live in one
   structured, consistent component per page, not repeated through the prose.
4. **Show before telling.** Every core concept gets a picture, an animation,
   or an interactive widget before the equations.
5. **Machine-readable first.** Status, audience, prerequisites, dates, and
   citations live in front matter or data files, so they can be rendered,
   searched, listed, and tested.
6. **Honest affordances.** A button or link never promises more than exists:
   no Colab buttons to stubs, no "Available" labels on empty hubs.
7. **Measure the reader experience.** Navigation and comprehension changes
   are validated with readers (#4088), and those results are never presented
   as scientific validation.

---

## 5. Decisions Required from the Board

These decisions gate the epics shown. Each should be recorded as an ADR in
`docs/adr/`.

<!-- prettier-ignore -->
| ID | Decision | Options | Recommendation | Gates |
| --- | --- | --- | --- | --- |
| D1 | Primary audiences and their order of priority | (a) Researcher-first with a lay on-ramp; (b) equal weight; (c) lay-first | (a). The depth is the differentiator; the on-ramp widens reach | E1, E3, E12 |
| D2 | Whether to add a golfer/coach persona | Add "Curious golfer / coach" and "Student" to `config/personas.yml` | Add both, with explicit "this is not coaching advice" framing | E1 |
| D3 | Interactive technology stack | (a) Plain JS / Observable JS (`{ojs}`); (b) Pyodide running `src/` modules; (c) Shinylive; (d) a mix | (d): OJS for lightweight widgets and Pyodide for faithful `src/` model execution, both self-hosted | E6 |
| D4 | Canonical version for each duplicated body of work | Per family: proximal–distal, tangent-space, theory series vs affine-nature, manifesto | The owner decides per family; see WEB-02.4 | E2 |
| D5 | Persistent identifiers | Zenodo DOI per release plus concept DOI; ORCID; per-page `citation:` | Adopt all three | E7 |
| D6 | Reader analytics | (a) None; (b) privacy-preserving, cookieless, self-hosted (e.g. aggregate page counts only); (c) third-party | (b), only after a written privacy policy | E14 |
| D7 | Content licence | Code MIT; text CC BY 4.0 or CC BY-NC-SA 4.0; data CC BY 4.0 or CC0 | CC BY 4.0 for text and data (maximises citation and reuse) | E7 |
| D8 | External review model | Invited expert review; open review via GitHub Discussions; preprint (arXiv/SportRxiv) | Invited review for the theory series, then a preprint | E5 |
| D9 | Visual identity investment | Keep cosmo plus custom; commission a design system; illustrate with a contractor | A light design system plus a commissioned illustration set for core concepts | E8 |
| D10 | Scope of retirement | Which stub hubs and duplicates to remove, and what the redirect policy is | Retire or hide every stub that carries no content; keep URLs with redirects | E2, E13 |

---

## 6. Epic and Issue Index

<!-- prettier-ignore -->
| Epic | Title | Issues | Priority | Primary audience |
| --- | --- | --- | --- | --- |
| E1 | Audience routing and onboarding funnel | 10 | P0 | Lay, student, golfer |
| E2 | Information architecture, naming, and consolidation | 10 | P0 | All |
| E3 | Layered page template (progressive disclosure) | 8 | P0 | All |
| E4 | Unified maturity and evidence signalling | 6 | P1 | All |
| E5 | Claims, critiques, and the validation roadmap | 10 | P1 | Researcher, reviewer |
| E6 | Interactive models and reproducibility | 13 | P1 | Learner, researcher, integrator |
| E7 | Researcher infrastructure: citation, identity, data | 11 | P1 | Researcher |
| E8 | Visual explanation and design system | 8 | P1 | All |
| E9 | Accessibility conformance | 8 | P1 | All |
| E10 | Performance, SEO, and privacy | 10 | P2 | All |
| E11 | Mathematical typesetting and notation | 7 | P2 | Researcher, student |
| E12 | Editorial voice and plain-language standard | 7 | P1 | All |
| E13 | Build, reliability, and maintainability | 9 | P2 | Maintainer |
| E14 | Reader validation, feedback, and community | 7 | P2 | All |
|   | **Total** | **124** |   |   |

---

## 7. Draft Epics and Issues

### E1 — Audience Routing and Onboarding Funnel

**Epic labels:** `type:epic`, `area:website`, `judgement:design`, `tier:strong`
**Goal:** Within 30 seconds, any first-time visitor can identify a starting
point suited to their background. A non-specialist can understand the
central idea of AffineDrift in about 5 minutes without meeting an equation
they are not prepared for.
**Done when:**

- WEB-01.1 through WEB-01.10 are closed.
- Task-based usability testing (#4088 protocol) shows ≥ 80 % of general-reader
  participants can find a suitable starting page and explain the drift/control
  idea in their own words.

**Depends on:** D1, D2.

#### WEB-01.1 — Add a "Start Here" page

- **Priority:** P0 · **Labels:** `type:feature`, `complexity:routine`, `judgement:design`, `tier:strong`
- **Problem:**
  - There is no single entry page.
  - `pages/overview.qmd` (1,100 words: scope, evidence standards, reading
    paths) is reachable from neither the navbar nor the home page.
- **Proposal:** Create `pages/start-here.qmd` with these sections:
  1. What AffineDrift is, in three sentences.
  2. The big idea in one picture (from WEB-08.2).
  3. "Choose your path", with cards per persona (WEB-01.3).
  4. How to read the evidence labels (WEB-04.4).
  5. What this site is not: not coaching advice, not peer-reviewed by
     default, not a validated human model.
- **Acceptance criteria:**
  - [ ] The page is linked as the first navbar item and as the primary CTA on
        the home page.
  - [ ] It contains no display equations.
  - [ ] Its Flesch–Kincaid grade is ≤ 10, measured by the WEB-12.5 checker.
  - [ ] An E2E test asserts the page is reachable in one click from every
        page's navbar.
- **Depends on:** WEB-02.1, WEB-08.2.

#### WEB-01.2 — Redesign the home page around audiences, not publication state

- **Priority:** P0 · **Labels:** `type:feature`, `judgement:design`, `tier:strong`
- **Problem:**
  - The home page leads with a publication-state key (`index.qmd:29-37`) and
    an equation (`:43-47`).
  - It repeats the same three books up to three times (`:24,59,94`).
  - "Latest Writing" has no dates.
- **Proposal:** Build the page from top to bottom as follows:
  1. A hero with a one-sentence value proposition and two CTAs: "New here?
     Start here" and "Researchers: go to the library".
  2. A "Three ways in" audience strip (curious reader / student / researcher).
  3. The big-idea visual with a short caption; the equation sits behind an
     "In symbols" toggle.
  4. Featured works (each book once, with its maturity badge).
  5. A dated "What's new" list generated from front-matter dates (WEB-07.3).
  6. A trust strip linking Critiques, the Claim Ledger, and Scope & Limits.
- **Acceptance criteria:**
  - [ ] No work is listed more than once.
  - [ ] The publication-state key moves to WEB-04.4 and is linked, not
        inlined.
  - [ ] "What's new" is a Quarto listing sorted by `date-modified`.
  - [ ] Layout passes at 390 px and 1440 px in light and dark themes.
  - [ ] The page `<title>` is not "Home" (WEB-10.7).
- **Depends on:** WEB-01.1, WEB-04.1, WEB-07.3.

#### WEB-01.3 — Extend personas to include curious golfer/coach and student, and render them site-wide

- **Priority:** P0 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:**
  - `config/personas.yml` defines Learner, Researcher, Integrator,
    Experimentalist, Reviewer, and Contributor. None serves golfers, coaches,
    or casual readers.
  - The personas render only on `resources/learning-paths.qmd:20-104`, which
    duplicates the "Choose a path" grid on the same page (`:108-147`).
- **Proposal:**
  - Add a `golfer-coach` persona and a `student` persona.
  - Generate a single persona card include from the YAML and use it on Start
    Here, the home page, and Learning Paths.
  - Remove the duplicated grid.
- **Acceptance criteria:**
  - [ ] Each persona has a first page, a 30-minute route, and a "go deeper"
        route.
  - [ ] The card include is generated from YAML and covered by a pytest that
        fails if a persona's link target does not render.
  - [ ] The golfer/coach persona states plainly that the site does not give
        swing instruction.

#### WEB-01.4 — Write "The Big Idea in Five Minutes" explainer

- **Priority:** P0 · **Labels:** `type:content`, `judgement:design`, `tier:strong`
- **Problem:** No page explains drift vs control, ZTCF, or DCR to a
  non-specialist without equations.
- **Proposal:** A short illustrated page (≈800–1,200 words) built on everyday
  analogies:
  - a swing on a playground;
  - a thrown ball versus a pushed one;
  - "what would happen if the golfer stopped pushing?", which is ZTCF.
    It should include one interactive toy (WEB-06.3 lite) and end with "Where
    to go next" links by persona.
- **Acceptance criteria:**
  - [ ] No display equations. At most one symbolic expression, inside an
        optional "In symbols" box.
  - [ ] Reviewed by at least two non-specialist readers, with notes recorded
        in the issue.
  - [ ] Every analogy is checked by the author for physical correctness, with
        a "where the analogy breaks" note.
  - [ ] Linked from Start Here, the home page, and the top of Theory Part 1.

#### WEB-01.5 — Build a site-wide glossary with hover definitions

- **Priority:** P1 · **Labels:** `type:feature`, `complexity:complex`, `tier:strong`
- **Problem:**
  - The only glossary is a book appendix
    (`articles/The_Physics_of_Golf/quarto/glossary.qmd`) at a technical
    level, linked from four places.
  - `NOTATION.md` is normative, not explanatory.
- **Proposal:**
  - Create `data/glossary.yml`. Each term has a one-line plain definition, a
    technical definition, related symbols, and a canonical page.
  - Render it as `pages/glossary.qmd`.
  - Provide a Quarto shortcode or Lua filter (`{{< term drift >}}`) that
    renders an accessible tooltip or popover and links to the entry.
- **Acceptance criteria:**
  - [ ] At least 60 terms at launch, covering every term used in the Start
        Here and Big Idea pages.
  - [ ] The tooltip works with keyboard and screen readers (WAI-ARIA tooltip
        or disclosure pattern) and on touch.
  - [ ] A pytest ensures every `{{< term >}}` key exists in the YAML.
  - [ ] The book glossary links to the site glossary; the two are not
        duplicated.

#### WEB-01.6 — Create a "How to Read This Site" guide

- **Priority:** P1 · **Labels:** `type:content`, `complexity:routine`, `tier:cli`
- **Problem:**
  - The six-state publication key is defined twice (`index.qmd`,
    `pages/development-roadmap.qmd`).
  - Pages use at least eight ad-hoc labels outside that key.
  - Readers are never told how books, series, articles, critiques, and
    ledgers relate.
- **Proposal:** One page that explains:
  - the site map;
  - the maturity badges (from WEB-04.1);
  - the evidence ladder (WEB-04.3);
  - how to read a critique record;
  - how to cite.
    Link to it from every badge.
- **Acceptance criteria:**
  - [ ] It is the single source of badge definitions.
  - [ ] Every badge component links to it.
  - [ ] Both existing inline definitions are removed.

#### WEB-01.7 — Add short on-ramp learning paths (5 minutes, 30 minutes, and 3 hours)

- **Priority:** P1 · **Labels:** `type:content`, `complexity:routine`, `tier:cli`
- **Problem:** The lightest current path is 40–80 hours
  (`resources/learning-paths.qmd`).
- **Proposal:** Add three short paths per persona, each a curated sequence of
  existing sections with a goal statement and a self-check question.
- **Acceptance criteria:**
  - [ ] Each path lists its pages in order with time estimates.
  - [ ] Every linked anchor resolves, enforced by the link gate.
  - [ ] Each path ends with one reflective question and its answer.
- **Depends on:** WEB-01.4, WEB-12.4.

#### WEB-01.8 — Correct learning-path contradictions and wrong chapter references

- **Priority:** P0 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:**
  - **Contradictory difficulty levels:** Control Theory is "Intermediate" in
    the hub table (`learning-paths.qmd:187`) but "Advanced" on its own page
    (`learning-path-control-theory.qmd:27`). Golf Science has a similar
    mismatch.
  - **Contradictory prerequisites:** Foundations says "No prerequisites"
    (`:14`), then lists algebra and trigonometry (`:27`).
  - **Wrong chapters:** Golf Science Module 1 assigns "Physics of Golf
    Chapters 1–3" for impact, aerodynamics, and ball flight
    (`learning-path-golf-science.qmd:41-42`). The correct chapters are
    ch28, ch19, and ch31.
  - **Duplicated resource:** the 3Blue1Brown series is listed twice in
    Foundations.
  - **Schedule mismatch:** Biomechanics is billed as "14-week", but Modules 7
    and 8 overlap.
- **Proposal:**
  - Fix each defect listed above.
  - Replace chapter-number prose with links to chapter anchors, so they
    break loudly if chapters move.
- **Acceptance criteria:**
  - [ ] All listed defects are fixed.
  - [ ] Levels come from one YAML source shared by the hub and the path pages.
  - [ ] A pytest asserts that the hub and path levels match.

#### WEB-01.9 — Make "In Layman's Terms" blocks open by default, rewrite them in plain language, and cover every core page

- **Priority:** P1 · **Labels:** `type:content`, `judgement:design`, `tier:strong`
- **Problem:**
  - The blocks exist on only four core pages.
  - They are collapsed by default (`aria-expanded="false"`).
  - They use technical vocabulary: "autonomous dynamics", "declared input
    channel" (`articles/theory-part1.qmd:46-75`).
- **Proposal:**
  - Replace the inline HTML with a shared include or shortcode.
  - Show the block open above the abstract.
  - Rewrite against the WEB-12.1 style guide.
  - Extend to theory Parts 2–5, DCR, superposition, the tangent series, and
    the falsification atlas.
- **Acceptance criteria:**
  - [ ] A single component, used on ≥ 15 core pages.
  - [ ] Each block is ≤ 250 words and reaches a readability grade ≤ 10.
  - [ ] Glossary terms are linked, not explained inline.
  - [ ] A Jest test covers the toggle.
  - [ ] The existing `LAYMAN` tangent-series variants are either merged into
        these blocks or linked from them.

#### WEB-01.10 — Make the 404 page and empty states useful

- **Priority:** P3 · **Labels:** `type:feature`, `complexity:simple`, `tier:cli`
- **Problem:**
  - `404.qmd` points to a Gmail address (`404.qmd:29`), while the site
    contact is `@AffineDrift.com`.
  - The page offers no suggested routes.
- **Proposal:**
  - Add search, Start Here, and the top five destinations.
  - Unify the contact channel (WEB-12.7).
- **Acceptance criteria:**
  - [ ] The 404 page links Start Here, search, and the Library.
  - [ ] The contact address matches the About and Contact pages.

---

### E2 — Information Architecture, Naming, and Consolidation

**Epic labels:** `type:epic`, `area:website`, `judgement:design`, `tier:strong`
**Goal:**

- Every page has one name, one canonical location, and one place in a
  navigation hierarchy with working breadcrumbs and prev/next links.
- Duplicate renditions are consolidated.

**Done when:**

- The navbar has ≤ 7 top-level entries, each menu holding one category.
- There are zero naming collisions.
- There are zero orphan rendered pages outside an allowlist.

**Depends on:** D4, D10.

#### WEB-02.1 — Restructure the navbar into single-purpose menus

- **Priority:** P0 · **Labels:** `type:feature`, `judgement:design`, `tier:strong`
- **Problem:** "Read" has 11 mixed items, "Connect" mixes about and resources,
  and resources are spread across three menus (`_quarto.yml:155-222`).
- **Proposal:** Top level:
  - **Start**: Start Here, Big Idea, How to Read This Site, Glossary.
  - **Library**: Books, Series, Article Index, Companion Guides.
  - **Evidence**: Claim Ledger, Critiques, Falsification Atlases, Validation
    Roadmap.
  - **Tools**: Interactive Models, Programming Companion, Datasets, Software.
  - **Resources**: Bibliography, Reference Books, Researchers, Papers, Videos,
    Websites.
  - **About**: About, Contact, Collaborate, Roadmap, Cite.
- **Acceptance criteria:**
  - [ ] A card-sort or tree test with ≥ 5 participants, run before merge and
        recorded in the issue.
  - [ ] No item appears in two menus.
  - [ ] Every rendered route in the public-site manifest is reachable within
        three clicks from the navbar; an E2E crawl asserts this.
  - [ ] The mobile menu passes the #4140 mobile-menu test.

#### WEB-02.2 — Resolve the "Volume II" collision and the Geometry of Motion volume pages

- **Priority:** P0 · **Labels:** `type:bug`, `judgement:design`, `tier:strong`
- **Problem:** Two different works are both called "Volume II".
  - **Book series:** `books/control-is-motion.qmd` is "Volume II: Control Is
    Motion".
  - **Geometry of Motion sidebar:** `_quarto.yml:136` labels `volume2.html`
    "Volume II: Transverse Control…".
  - **Geometry of Motion index:** calls the same page "Control Is Motion"
    (`articles/The_Geometry_of_Motion/quarto/index.qmd:55-57`).
  - **Empty page:** `volume2.qmd` has 24 words and includes a file that is
    excluded from render (`_quarto.yml:17`).
  - **Volume ranges differ:** the LaTeX source defines Volumes 0–V; the books
    pages expose I–IV.
- **Proposal:**
  - Adopt one numbering scheme across LaTeX, `books/`, and the Geometry of
    Motion site.
  - Publish a mapping table on the Books hub.
  - Hide or redirect empty volume pages.
- **Acceptance criteria:**
  - [ ] Each volume number maps to exactly one title everywhere; a pytest
        checks `_quarto.yml`, `books/*.qmd`, and the Geometry of Motion index.
  - [ ] No rendered volume page has fewer than 200 words unless it is marked
        Planned.

#### WEB-02.3 — Give the theory series a single name

- **Priority:** P0 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:** The series goes by three names.
  - **Navbar:** "Drifter Manifesto & Theory" (`_quarto.yml:163`).
  - **Sidebar:** "Theory Part N".
  - **Page titles:** "Affine Control Interpretation of the Golf Swing — Part N".
  - **Title collision:** `affine-nature-golf-swing.qmd` also titles itself
    "Part I".
- **Proposal:**
  - Adopt one series name and one title pattern.
  - Retitle `affine-nature-golf-swing` as the consolidated edition.
  - Add series metadata (`series:`, `series-part:`) to front matter.
- **Acceptance criteria:**
  - [ ] One series name is used in the navbar, sidebar, titles, Article
        Index, and home page.
  - [ ] A pytest enforces the title pattern from `series:` metadata.

#### WEB-02.4 — Consolidation plan for duplicated bodies of work

- **Priority:** P1 · **Labels:** `type:epic-child`, `judgement:contested`, `tier:strong`
- **Problem:** The same material exists in several renditions with no
  canonical marker:
  - **Proximal–distal (five forms):** monograph, standalone article (13k
    words), companion journey, atlas, workbench.
  - **Tangent-space (three forms):** series, articles with LAYMAN/CRITIC
    variants, book volume.
  - **Theory series:** the series pages vs the affine-nature consolidated
    edition.
  - **Manifesto:** `pages/` and `articles/` versions.
- **Proposal:** For each family:
  1. Declare the canonical source.
  2. Mark derivatives with a `canonical:` front-matter pointer and a visible
     "This is a companion to …" banner.
  3. Retire derivatives that add nothing.
  4. Record each decision in an ADR.
- **Acceptance criteria:**
  - [ ] An ADR per family, approved by the owner (D4).
  - [ ] Every derivative page shows a canonical banner and sets `<link
rel="canonical">` to the canon where appropriate.
  - [ ] Retired URLs redirect (WEB-02.9).

#### WEB-02.5 — Turn on series prev/next links and breadcrumbs for hub pages

- **Priority:** P1 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:**
  - `page-navigation: true` is not set, although the `_quarto.yml:79-82`
    comment relies on it.
  - Hub pages (`pages/*`, `resources/*`) have no sidebar, so they have no
    breadcrumbs. **Verify on live site.**
- **Proposal:**
  - Set `website.page-navigation: true`.
  - Add a minimal sidebar or breadcrumb context for hub sections.
- **Acceptance criteria:**
  - [ ] An E2E test asserts prev/next links on every series page, in the
        correct order.
  - [ ] Breadcrumbs render on every page except the home page.

#### WEB-02.6 — Hide, mark, or retire stub hubs

- **Priority:** P1 · **Labels:** `type:content`, `complexity:simple`, `tier:cli`
- **Problem:**
  - `pages/book-reviews.qmd` is empty and Planned, yet the Article Index
    describes it as commentary (`resources/articles.qmd:185`).
  - Four research-review stubs are mostly search links, and one is promoted as
    a hub card (`resources/resources.qmd:114-122`).
  - `pages/daydreams-doodles.qmd` has one entry.
  - A green "success" banner decorates a scaffolding page
    (`resources/research-reviews.qmd:18`).
- **Proposal:** Remove stubs from navigation and cards until they have
  content, or clearly badge them Planned with an expected date.
- **Acceptance criteria:**
  - [ ] No hub card links to a page under 300 words unless it carries a
        Planned badge.
  - [ ] Scaffolding pages never use success styling; a lint rule enforces
        this.

#### WEB-02.7 — Drive category listings from front matter

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:**
  - `categories:` are set on every page but drive no listing.
  - Some values are wrong (the manifesto is categorised `critique`).
  - The Article Index (`resources/articles.qmd`, 194 lines) is maintained by
    hand.
- **Proposal:**
  - Define a controlled vocabulary for `categories:` and `topic:`.
  - Generate the Article Index as a Quarto listing (filterable by topic,
    audience level, and maturity).
- **Acceptance criteria:**
  - [ ] The Article Index is generated.
  - [ ] Its filters work with keyboard navigation.
  - [ ] A pytest rejects categories outside the vocabulary.

#### WEB-02.8 — Align page titles, navigation labels, and descriptions

- **Priority:** P2 · **Labels:** `type:bug`, `complexity:simple`, `tier:ollama`
- **Problem:** Many pages go by different names in different places.

  | Page                      | Title                   | Other label                                            |
  | ------------------------- | ----------------------- | ------------------------------------------------------ |
  | `pages/about.qmd`         | "About & Contact"       | A separate Contact page exists                         |
  | `resources/resources.qmd` | "Resources & Links"     | Navbar: "Resources Hub"                                |
  | `pages/tools.qmd`         | "Programs & Tools"      | "Interactive Tools" and "Software and provider status" |
  | `models/models.qmd`       | "Programming Companion" | "Models"                                               |
  | Tangent-series parts      | "Tangent Hyperplanes I" | "Part 1" and "Compact Part I"                          |

  Descriptions are thin, for example "Get in touch with AffineDrift".

- **Proposal:**
  - Make the navigation label equal the page title.
  - Write descriptions of 120–160 characters.
- **Acceptance criteria:**
  - [ ] A pytest asserts that each navbar and sidebar `text` equals the
        target page `title`, or an allowlisted short form.
  - [ ] Every description is 70–160 characters.

#### WEB-02.9 — URL stability and redirect policy

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:** Consolidation and renaming will move URLs. External citations
  and search rankings depend on them staying stable.
- **Proposal:**
  - Use Quarto `aliases:` on moved pages.
  - Keep a `config/redirects.yml` ledger.
  - Add a CI check that every URL in the previous deploy manifest still
    resolves to a 200 or a redirect.
- **Acceptance criteria:**
  - [ ] Deploy fails if a previously published route disappears without an
        alias.
  - [ ] The redirect ledger is documented in `CONTRIBUTING.md`.

#### WEB-02.10 — Configure search, and include maturity in results

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:**
  - Search runs on Quarto defaults.
  - The JSON-LD `SearchAction` (`_includes/site-head.html:14`) points to
    `/?q=`, which is unverified.
  - Search snippets carry no maturity state; the 2026-08-29 review raised
    this idea, but no issue exists for it.
- **Proposal:**
  - Configure a `search:` block (overlay, result limit, keyboard shortcut).
  - Index the glossary.
  - Show the maturity badge in results.
  - Fix or remove the `SearchAction`.
- **Acceptance criteria:**
  - [ ] An E2E test: searching "ZTCF" returns the ZTCF page first, with its
        badge.
  - [ ] The `SearchAction` target actually opens search, or the action is
        removed.

---

### E3 — Layered Page Template (Progressive Disclosure)

**Epic labels:** `type:epic`, `area:website`, `judgement:design`, `tier:strong`
**Goal:** Every core technical page follows one predictable structure that
serves lay readers and experts on the same URL without diluting the formal
content.
**Done when:**

- The template is adopted on all pages listed in WEB-03.8.
- A front-matter schema is validated in CI.

#### WEB-03.1 — Define and validate the article front-matter schema

- **Priority:** P0 · **Labels:** `type:feature`, `complexity:complex`, `judgement:design`, `tier:strong`
- **Problem:**
  - No page records machine-readable status, audience level, prerequisites,
    or dates. No `status:` field exists anywhere.
  - Only the monograph has an `abstract:`.
- **Proposal:** Create `schemas/article-front-matter-v1.schema.json` with
  these fields:
  - `status` (the enum from WEB-04.1);
  - `audience-level` (intro / intermediate / advanced / research);
  - `prerequisites` (a list of page links);
  - `summary-plain` (≤ 60 words);
  - `abstract`;
  - `key-takeaways` (3–5 items);
  - `date` (the true first-publication date);
  - `date-modified`;
  - `last-reviewed`;
  - `canonical`;
  - `series` / `series-part`;
  - `evidence-rung` (WEB-04.3).
    Validate with a pytest over all rendered `.qmd` sources.
- **Acceptance criteria:**
  - [ ] The schema is committed and documented in `CONTRIBUTING.md`.
  - [ ] CI fails for core pages missing the required fields.
  - [ ] An allowlist, burned down over time, covers the remaining pages.
  - [ ] No new page may use `date: today`.

#### WEB-03.2 — Build the page header card component

- **Priority:** P0 · **Labels:** `type:feature`, `complexity:complex`, `tier:cli`
- **Problem:**
  - Status, reading level, prerequisites, and dates are either invisible or
    written as ad-hoc prose.
  - `js/accessibility.js:341` shows a 225-wpm reading-time estimate, while
    `books/roadmap.qmd:62` says reading times must not be published without
    evidence.
- **Proposal:** A Quarto partial or Lua filter that renders the following
  from front matter:
  - the maturity badge;
  - the audience level;
  - the estimated reading time, labelled "estimate";
  - prerequisites;
  - first published and last reviewed dates;
  - "Cite this page" (WEB-07.2).
- **Acceptance criteria:**
  - [ ] Rendered purely from front matter, with no hand-written HTML.
  - [ ] Accessible markup (a `dl`, with badges carrying text, not colour
        alone).
  - [ ] Jest or Playwright coverage.
  - [ ] The reading-time policy conflict is resolved and recorded in
        `books/roadmap.qmd`.

#### WEB-03.3 — Plain-language summary and key takeaways block

- **Priority:** P0 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:** "Key takeaways" are essentially absent across the site.
- **Proposal:**
  - Render `summary-plain` and `key-takeaways` beneath the header card on
    every core page.
  - Merge with the WEB-01.9 lay block, so a page does not show two summary
    boxes.
- **Acceptance criteria:**
  - [ ] One component, driven by front matter.
  - [ ] Visible without interaction.
  - [ ] Printed in the PDF/print stylesheet.

#### WEB-03.4 — Standard "What This Shows / What It Does Not Show" block

- **Priority:** P0 · **Labels:** `type:feature`, `judgement:design`, `tier:strong`
- **Problem:** Caveats are scattered through running prose ("does not
  establish" ×122), which hurts readability and dilutes the caveats
  themselves.
- **Proposal:**
  - One structured block per page, generated from front matter or the claim
    registry (WEB-05.1).
  - It lists: what the page establishes and at which evidence rung, what it
    does not establish, open critiques (auto-linked), and the next validation
    gate.
- **Acceptance criteria:**
  - [ ] A component exists and is used on all core pages.
  - [ ] An editorial pass (WEB-12.3) removes the now-redundant inline
        caveats.
  - [ ] Every limitation that is deleted from the prose is retained in the
        block, verified by a before/after diff review recorded in the PR.

#### WEB-03.5 — Standard "Where Next" footer

- **Priority:** P1 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:**
  - "Related Articles" lists are maintained by hand, sometimes link to the
    page itself (`resources/resources.qmd:149`,
    `learning-paths.qmd:275`), and vary in format.
  - Related work #3900/#3901 is open.
- **Proposal:**
  - A generated footer with "Previous / Next in series", "Go simpler",
    "Go deeper", "See the evidence", and "Try it" (an interactive link).
  - Built from front matter plus the related-links data.
- **Acceptance criteria:**
  - [ ] No page links to itself.
  - [ ] Each core page has at least one "simpler" and one "deeper" link.
  - [ ] Coordinated with #3900/#3901 so the two efforts do not duplicate.

#### WEB-03.6 — Worked-example callout convention

- **Priority:** P2 · **Labels:** `type:content`, `complexity:routine`, `tier:cli`
- **Problem:** Formal derivations rarely include a numerical worked example
  that readers can follow by hand.
- **Proposal:**
  - Adopt a `.callout-example` convention with given data, steps, and the
    result.
  - Add at least one worked example to each theory part, DCR, ZTCF, and
    superposition.
  - Numbers must be reproducible from `src/` (WEB-06.6).
- **Acceptance criteria:**
  - [ ] ≥ 8 worked examples.
  - [ ] Each is tested by a pytest that recomputes its numbers from `src/`.

#### WEB-03.7 — "What this means for golfers and coaches" box, with guardrails

- **Priority:** P2 · **Labels:** `type:content`, `judgement:contested`, `tier:strong`
- **Problem:** Lay readers want practical meaning, but the site correctly
  refuses to give coaching advice. At present there is nothing between those
  two positions.
- **Proposal:**
  - A carefully bounded box: "How to think about this".
  - It gives conceptual implications and questions a golfer or coach might
    ask a professional.
  - It is explicitly not instruction, and it links to the evidence rung.
- **Acceptance criteria:**
  - [ ] Template text approved by the owner.
  - [ ] Every box carries the evidence-rung badge.
  - [ ] Used on no more than the pages the owner approves.

#### WEB-03.8 — Roll out the template to core pages

- **Priority:** P1 · **Labels:** `type:content`, `complexity:routine`, `tier:cli`
- **Proposal:** Apply WEB-03.1 to WEB-03.5 to these pages:
  - theory Parts 1–5;
  - the consolidated edition;
  - ZTCF;
  - DCR;
  - superposition;
  - the tangent-series parts;
  - drift-components;
  - inverse-dynamics;
  - inverse-dynamics-inference;
  - the proximal–distal article;
  - the technology articles;
  - the book landing pages.
- **Acceptance criteria:**
  - [ ] ≥ 30 pages conform.
  - [ ] The CI allowlist from WEB-03.1 has shrunk accordingly.
  - [ ] No change to the substantive technical content, verified by review.

---

### E4 — Unified Maturity and Evidence Signalling

**Epic labels:** `type:epic`, `area:website`, `judgement:design`, `tier:strong`
**Goal:** One vocabulary and one visual system for how mature a work is and
how strong its evidence is, applied everywhere a work is shown.
**Coordinate with:** #4085 and #4086 (shared evidence semantics). This epic is
the reader-presentation layer over that work, not a replacement for it.

#### WEB-04.1 — Consolidate maturity vocabulary into a single enum

- **Priority:** P0 · **Labels:** `type:feature`, `judgement:design`, `tier:strong`
- **Problem:** Pages use many labels outside the six-state key:
  - "In Progress (Scaffolding Phase)";
  - "EXPLORATORY";
  - "scaffolded";
  - "canonical / reference / exploratory";
  - "Available computational publication";
  - "Supported / Extended".
- **Proposal:**
  - One enum in `config/maturity.yml`, with a plain-language definition,
    "establishes", and "does not establish" for each value.
  - Map every legacy label onto it.
- **Acceptance criteria:**
  - [ ] A pytest rejects any status string outside the enum in front matter
        or badge includes.
  - [ ] A migration table is recorded in the PR.

#### WEB-04.2 — Badge component used on cards, headers, listings, and search

- **Priority:** P1 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:** Only five `.qmd` files use banners or pills. The styles vary
  (upper-case pills, title-case banners, bold prose), and success styling
  appears on scaffolding.
- **Proposal:**
  - One badge include or shortcode (`{{< status >}}`) that reads front matter.
  - Uses both icon and text, so meaning does not depend on colour.
- **Acceptance criteria:**
  - [ ] All legacy pills are replaced.
  - [ ] Contrast is AA in both themes.
  - [ ] The badge links to WEB-01.6.
  - [ ] Visual prominence never implies a higher state; this is checked in
        design review.

#### WEB-04.3 — Evidence ladder

- **Priority:** P1 · **Labels:** `type:feature`, `judgement:design`, `tier:strong`
- **Problem:** The 2026-08-29 review proposed an evidence ladder, but no issue
  was filed. Model evidence can be read as human evidence.
- **Proposal:**
  - Rungs: mathematical identity → manufactured fixture → qualified
    simulation → measured participant result → replicated result → bounded
    application.
  - Show the current rung on every synthesis page and featured program.
- **Acceptance criteria:**
  - [ ] Rungs are defined in `config/maturity.yml`.
  - [ ] Every core page declares `evidence-rung`.
  - [ ] Validation: no page may claim a rung above "qualified simulation"
        without a linked measured-data record.

#### WEB-04.4 — Remove duplicated state keys from the home and roadmap pages

- **Priority:** P2 · **Labels:** `type:content`, `complexity:simple`, `tier:ollama`
- **Proposal:**
  - Replace `index.qmd:29-37` and `pages/development-roadmap.qmd:38-49` with
    links to WEB-01.6.
- **Acceptance criteria:**
  - [ ] Exactly one definition of each state on the site.

#### WEB-04.5 — Show maturity in the Article Index and on Books hub cards

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:simple`, `tier:cli`
- **Problem:** The Article Index shows no per-entry status.
- **Acceptance criteria:**
  - [ ] Every card or listing entry shows its badge, sourced from front
        matter.
- **Depends on:** WEB-02.7.

#### WEB-04.6 — Freshness indicator

- **Priority:** P3 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Proposal:**
  - Show "Last reviewed N months ago" from `last-reviewed`.
  - Flag pages not reviewed in 12 months on an internal dashboard; this
    extends the existing freshness work in #4027.
- **Acceptance criteria:**
  - [ ] A generated report lists stale pages.
  - [ ] No page shows a build date as a review date.

---

### E5 — Claims, Critiques, and the Validation Roadmap

**Epic labels:** `type:epic`, `area:science`, `complexity:research`, `tier:strong`
**Goal:**

- Each core thesis of AffineDrift is a registered, readable claim with its
  falsifiers, critiques, and next validation gate.
- The route from model to measured human data is published as a concrete,
  reviewable plan.

**Coordinate with:** #4084, #4087, #4032 (claim and critique explorer), #4021
(site-wide trust review), and #4253/#4255 (deferred evidence). Physical
measurement work follows the deferred-validation rule: it is never simulated
as complete.

#### WEB-05.1 — Register core theses in the claim registry

- **Priority:** P0 · **Labels:** `type:content`, `complexity:research`, `tier:strong`
- **Problem:** `data/trust/claim_registry.json` contains one claim
  (`ad-dcr-001`).
- **Proposal:** Draft claim records, reviewed by the owner, for at least:
  - the drift/control decomposition as a model identity;
  - ZTCF attribution;
  - ZVCF;
  - DCR interpretation;
  - superposition limits;
  - proximal–distal sequencing;
  - intentional constraint collapse;
  - secondary-axis stability;
  - wrist universal-joint torque transmission;
  - each tangent-space contraction claim.
- **Acceptance criteria:**
  - [ ] ≥ 12 claims, each with falsifiers, limitations, evidence rung,
        software provenance, and next validation gate.
  - [ ] Schema-valid.
  - [ ] Owner sign-off recorded per claim.

#### WEB-05.2 — Readable claim ledger page

- **Priority:** P1 · **Labels:** `type:feature`, `complexity:complex`, `tier:cli`
- **Problem:**
  - `_includes/generated/evidence-presentation-summary.qmd` is included on no
    page and links to raw JSON.
  - Its table mixes scientific claims with software-feature rows (Docker
    dialog, MCP config).
- **Proposal:**
  - A dedicated `evidence/claims.qmd` page with one card per claim: plain
    statement, formal statement, rung, falsifiers, critiques, and pages
    making the claim.
  - Software-feature rows move to the Programming Companion.
- **Acceptance criteria:**
  - [ ] Generated from the registry.
  - [ ] Human-readable anchors per claim.
  - [ ] Keyboard and screen-reader accessible.
  - [ ] Linked from every page that makes a registered claim (through the
        WEB-03.4 block).
- **Coordinate with:** #4084 (explorer); this page may be its first
  increment.

#### WEB-05.3 — Extend critique annotations to the ZTCF and proximal–distal pages

- **Priority:** P0 · **Labels:** `type:bug`, `complexity:routine`, `tier:cli`
- **Problem:**
  - `zero-torque-counterfactual.qmd` and `theory-part2.qmd` have no critique
    callouts, although `ztcf_identifiability`, `static_fallacy_zvcf`, and
    `passive_overshoot_artifact` all concern ZTCF.
  - The proximal–distal works have no ledger entries.
- **Proposal:**
  - Correct the ledger page mappings.
  - Generate annotations for all affected pages.
- **Acceptance criteria:**
  - [ ] Every critique maps to every page whose claim it targets.
  - [ ] A pytest fails if a registered claim's page lacks an annotation for a
        critique that targets that claim.

#### WEB-05.4 — Triage critique severity and publish response timelines

- **Priority:** P1 · **Labels:** `type:content`, `judgement:contested`, `tier:strong`
- **Problem:**
  - 3 critiques have severity "Unknown" (aerodynamics,
    neuromuscular/open-loop, impact evasion).
  - The Critical "Tip Mass Omission" critique against Part 1 is Open.
  - 0 critiques are resolved.
- **Proposal:**
  - Assign a severity to every critique.
  - Publish a target response window per severity.
  - Prioritise the Critical item.
  - Rename `critiques/DEFENSE_STRATEGY` to a neutral name (for example
    `adjudication-summary`) with an alias.
- **Acceptance criteria:**
  - [ ] No "Unknown" severities.
  - [ ] The Critical critique has a published response or a dated plan.
  - [ ] The file is renamed and the old URL redirects.

#### WEB-05.5 — Publish the model-to-human validation roadmap

- **Priority:** P1 · **Labels:** `type:content`, `complexity:research`, `tier:strong`
- **Problem:**
  - The in-vivo gap is acknowledged only through disclaimers.
  - EMG is absent from all core theory pages and from the research-protocol
    library.
  - `models/research-protocol-readiness.qmd` is linked from no core article.
- **Proposal:** A reader-facing roadmap page covering, for each core claim:
  - what measurement would test it (EMG timing, force plates, bilateral grip
    wrench, marker vs markerless kinematics, perturbation trials);
  - what would count as disconfirming;
  - the error-propagation analysis required;
  - the current status.
    Link it from every WEB-03.4 block.
- **Acceptance criteria:**
  - [ ] Covers every claim from WEB-05.1.
  - [ ] Distinguishes planned, deferred (per the deferred-validation catalog),
        and unavailable measurements.
  - [ ] Contains no fabricated or simulated result presented as measurement.
  - [ ] Linked from the core theory pages.

#### WEB-05.6 — Scientific (not process) falsifiers for the research protocols

- **Priority:** P2 · **Labels:** `type:content`, `complexity:research`, `tier:strong`
- **Problem:**
  - Protocol falsifiers in `data/research_protocols/library.json` test process
    (for example "a manufactured null case is reported as confirmation"), not
    the science.
  - The power plan is "Unavailable".
  - The neural-timing protocol names no measurement modality.
- **Proposal:**
  - Add a scientific falsifier and a named measurement modality to each
    protocol.
  - Add an honest statement about statistical power.
- **Acceptance criteria:**
  - [ ] Every protocol has ≥ 1 scientific falsifier and a named modality.
  - [ ] The schema is extended in a backward-compatible way.

#### WEB-05.7 — Falsification atlases for ZTCF and DCR

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:complex`, `tier:strong`
- **Problem:** Only proximal–distal has a per-claim alternative/falsifier
  atlas, and it is the best-designed evidence view on the site.
- **Proposal:** Reuse the atlas schema and generator for ZTCF and DCR, and
  later for ICC and secondary-axis stability.
- **Acceptance criteria:**
  - [ ] Two new atlases generated from JSON.
  - [ ] Each row links the claim, the alternative mechanism, and the
        discriminating measurement.
- **Coordinate with:** #4087.

#### WEB-05.8 — External review pathway

- **Priority:** P1 · **Labels:** `type:process`, `judgement:design`, `tier:strong`
- **Problem:**
  - All reviews are internal or automated.
  - `pages/collaborate.qmd` offers GitHub issues only.
  - There is no reviewer invitation, open-review record, or preprint plan.
- **Proposal:**
  - A "Review this work" page: what feedback is wanted, how reviews are
    recorded (a public review log, with reviewer consent), recognition for
    reviewers, and a conflict-of-interest statement.
  - A named first target: an invited review of theory Parts 1–3.
- **Acceptance criteria:**
  - [ ] The page is published.
  - [ ] A review-record schema exists.
  - [ ] At least one external review is solicited, with its status tracked
        (the outcome depends on the reviewer, not this issue).
- **Depends on:** D8.

#### WEB-05.9 — Resolve the "passive/active" nomenclature conflict in The Physics of Golf

- **Priority:** P1 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:** `articles/The_Physics_of_Golf/nomenclature.tex:15,41-42`
  equates drift with "passive" and input with "active (muscular)". Both
  `NOTATION.md` and the `drift_superposition` critique reject that equation.
- **Acceptance criteria:**
  - [ ] Nomenclature aligned with `NOTATION.md`.
  - [ ] A terminology-baseline check (`config/`) extended to `.tex` sources.

#### WEB-05.10 — Preprint or archival release of the theory series

- **Priority:** P2 · **Labels:** `type:process`, `judgement:contested`, `tier:strong`
- **Proposal:**
  - Prepare a preprint of the consolidated theory edition after WEB-05.4 and
    WEB-05.8.
  - Include a DOI (WEB-07.1) and a response-to-critique appendix.
- **Acceptance criteria:**
  - [ ] Owner decision recorded.
  - [ ] If approved: a submission package built reproducibly from the source.

---

### E6 — Interactive Models and Reproducibility

**Epic labels:** `type:epic`, `area:interactive`, `judgement:design`, `tier:strong`
**Goal:**

- Every core concept has an in-browser way to see it.
- Every published number can be reproduced by a reader.
- No button promises more than exists.

**Coordinate with:** #4028, #4029, #4042 (the reproducible study workbench).
These browser widgets are teaching tools, labelled "exploratory model
output". They are not governed reproductions and must never be presented as
such.
**Depends on:** D3.

#### WEB-06.1 — ADR: interactive technology stack

- **Priority:** P0 · **Labels:** `type:adr`, `judgement:design`, `tier:strong`
- **Problem:** No `{ojs}`, Pyodide, or Shinylive is in use. The one widget
  uses Three.js r147 from a CDN, and Plotly also loads from a CDN.
- **Proposal:** Decide between OJS, Pyodide, and a mix, covering:
  - self-hosting;
  - offline and PWA behaviour;
  - bundle-size budget;
  - test strategy (Jest and Playwright);
  - how widgets import `src/` code so that browser and Python results stay
    identical.
- **Acceptance criteria:**
  - [ ] ADR merged.
  - [ ] Performance budget per widget.
  - [ ] Parity-test strategy defined.

#### WEB-06.2 — Make `src/` installable and version it

- **Priority:** P0 · **Labels:** `type:build`, `complexity:routine`, `tier:cli`
- **Problem:** `pyproject.toml:7` has `packages = []`, so readers cannot
  `pip install` the models the site describes.
- **Proposal:**
  - Configure packaging for `affine_control`, `golf_simulation`, and
    `tangent_models`.
  - Build a wheel in CI.
  - Tag releases.
- **Acceptance criteria:**
  - [ ] `pip install .` works in a clean Python 3.12 environment.
  - [ ] A wheel is attached to releases.
  - [ ] Import smoke tests pass.
  - [ ] The coverage floor is unchanged.

#### WEB-06.3 — "Drift vs Control" double-pendulum sandbox

- **Priority:** P0 · **Labels:** `type:feature`, `complexity:complex`, `tier:strong`
- **Problem:** The core theory pages have no figures, and the central idea is
  never shown.
- **Proposal:**
  - **Model source:** a widget built on
    `src/affine_control/dynamics.py::planar_double_pendulum_trajectory`,
    `double_pendulum_mass_matrix`, and `double_pendulum_coriolis`.
  - **Controls:** sliders for segment lengths, masses, and torque profiles.
  - **Live output:**
    - an animated linkage;
    - the drift term and the input term as time series;
    - vector arrows on the linkage showing $f(x)$ and $G(x)u$.
  - **Content:** two preset scenarios and a "lite" mode for the Big Idea page
    (WEB-01.4).
- **Acceptance criteria:**
  - [ ] Browser output matches the Python reference within a stated
        tolerance, tested in CI.
  - [ ] Keyboard-operable controls with a text alternative (a data table).
  - [ ] Labelled "exploratory model output".
  - [ ] Within the WEB-06.1 budget.
  - [ ] Embedded on theory Part 1 and the Big Idea page.

#### WEB-06.4 — ZTCF counterfactual explorer

- **Priority:** P1 · **Labels:** `type:feature`, `complexity:complex`, `tier:strong`
- **Proposal:**
  - A widget driven by `src/affine_control/ztcf_contract.py::execute_ztcf_intervention`,
    seeded from `data/ztcf/planar_golf_forward_fixture_v2.json`.
  - The reader picks an intervention time. The widget overlays the actual and
    zero-torque trajectories and shows the attributed difference, with the
    identifiability caveats from the critique ledger displayed alongside.
- **Acceptance criteria:**
  - [ ] A parity test against Python.
  - [ ] Fixture provenance (SHA-256) displayed.
  - [ ] Critique links shown in the widget.
  - [ ] Embedded on the ZTCF page.

#### WEB-06.5 — DCR visualiser

- **Priority:** P1 · **Labels:** `type:feature`, `complexity:complex`, `tier:cli`
- **Proposal:**
  - A widget using `reachability.py::instantaneous_scalar_dcr` to show how
    the ratio changes through a swing phase.
  - It explicitly shows why DCR is not a reachability certificate (claim
    `ad-dcr-001`).
- **Acceptance criteria:**
  - [ ] A parity test.
  - [ ] Embedded on the DCR page, with the registered claim linked.

#### WEB-06.6 — Figures for core theory pages

- **Priority:** P0 · **Labels:** `type:content`, `complexity:routine`, `tier:cli`
- **Problem:** `controllability-drift-ratio`, `zero-torque-counterfactual`,
  and `superposition` have zero figures.
- **Proposal:**
  - Static, script-generated figures (matching the existing
    `scripts/build_*_figures.py` pattern).
  - Used as fallbacks for the widgets and for print.
- **Acceptance criteria:**
  - [ ] ≥ 3 figures per page.
  - [ ] Generated deterministically by script.
  - [ ] Alt text and long descriptions.
  - [ ] Within the image budget.

#### WEB-06.7 — Fill or hide the 42 stub notebooks

- **Priority:** P0 · **Labels:** `type:bug`, `complexity:routine`, `tier:cli`
- **Problem:**
  - All files in `notebooks/geometry_of_motion/` are two-cell stubs.
  - `books/control-is-motion.qmd` and `books/human-motor-control.qmd` show
    "Open Notebook in Colab" buttons that lead to them.
- **Proposal:**
  - Remove Colab buttons for stubs immediately.
  - Then fill priority notebooks from `src/`: vol1 ch3 superposition, vol1 ch7
    counterfactuals, vol2 ch5 underactuation.
- **Acceptance criteria:**
  - [ ] No Colab button links to a notebook with fewer than 5 code cells.
  - [ ] Filled notebooks execute top to bottom in CI (`nbclient`).

#### WEB-06.8 — Reader run environment (Binder, devcontainer, downloads)

- **Priority:** P1 · **Labels:** `type:build`, `complexity:routine`, `tier:cli`
- **Problem:** There is no Binder, Codespaces, devcontainer, or notebook
  download, and `code-tools: false` is set.
- **Proposal:**
  - Add `.devcontainer/` and a Binder `environment.yml` reusing
    `requirements-docker.lock`.
  - Enable per-page source download for pages with code.
- **Acceptance criteria:**
  - [ ] "Launch Binder" works for the filled notebooks.
  - [ ] The devcontainer builds in CI.
  - [ ] Download links are present on code pages.

#### WEB-06.9 — Resolve the stray executable cell

- **Priority:** P2 · **Labels:** `type:bug`, `complexity:trivial`, `tier:ollama`
- **Problem:** `articles/drift-components-wrench-double-pendulum.qmd:510` is a
  `{python}` cell that only imports numpy and scipy. It contradicts
  `ci-standard.yml:569` ("no executable cells").
- **Proposal:** Either make it a real frozen model (`freeze: auto`) or turn it
  into a non-executing block, and correct the CI comment.
- **Acceptance criteria:**
  - [ ] The site's execution state matches the CI documentation.

#### WEB-06.10 — 3D swing kinematics viewer

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:deep`, `tier:strong`
- **Proposal:**
  - A viewer on a self-hosted Three.js (r150+ ES modules, with SRI).
  - Driven by `src/affine_control/golf_model.py` kinematics (three-link plus
    shaft mode).
  - Colour-codes drift and input contributions on the segments.
- **Acceptance criteria:**
  - [ ] Reduced-motion and non-WebGL fallbacks.
  - [ ] Within the performance budget.
  - [ ] A parity test on joint trajectories.

#### WEB-06.11 — Modernise and self-host the rotation converter and grip simulator dependencies

- **Priority:** P2 · **Labels:** `type:chore`, `complexity:routine`, `tier:cli`
- **Problem:**
  - Three.js r147 uses the legacy `examples/js` path (removed in r148), loads
    from a CDN without SRI, and is not in the service-worker precache.
  - Plotly loads from `cdn.plot.ly`.
  - `grip_angle_simulator.html` is not listed in `_quarto.yml` resources.
    **Verify on live site.**
- **Acceptance criteria:**
  - [ ] Both libraries are self-hosted with pinned versions.
  - [ ] They work offline via the service worker.
  - [ ] The simulator is listed in `resources:` and passes an E2E smoke test.

#### WEB-06.12 — Fixture and dataset explorer

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:complex`, `tier:cli`
- **Proposal:**
  - A browser viewer for `data/ztcf/*.json`,
    `data/population_generalization/`, and the proximal–distal snapshots.
  - Validates each file against its schema and plots its time series.
- **Acceptance criteria:**
  - [ ] Validates in the browser against the published schemas.
  - [ ] Download buttons with SHA-256.
  - [ ] Accessible data tables.

#### WEB-06.13 — Fix programming-companion metadata and repository links

- **Priority:** P2 · **Labels:** `type:bug`, `complexity:routine`, `tier:cli`
- **Problem:**
  - `models/programming/programs.qmd` uses IDs as titles for all 70 records
    (e.g. `aip | aip`), with a uniform engine and surface.
  - `engines.qmd` shows "Unspecified" maturity everywhere.
  - `repositories/*.qmd` has 16 unpinned UpstreamDrift links and generic
    prose.
- **Proposal:** Regenerate with real metadata, or display "metadata pending"
  honestly. Pin the links.
- **Acceptance criteria:**
  - [ ] No record where the title equals the ID.
  - [ ] Every provider link is SHA-pinned or explicitly labelled
        "navigation only".
- **Coordinate with:** #4023, #4024.

---

### E7 — Researcher Infrastructure: Citation, Identity, Data

**Epic labels:** `type:epic`, `area:research-infra`, `tier:strong`
**Goal:** A researcher can cite any page or book with a persistent
identifier, see real version dates, obtain data with a licence, and trust
bibliographic metadata.
**Depends on:** D5, D7.

#### WEB-07.1 — CITATION.cff, Zenodo integration, and DOIs

- **Priority:** P0 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:** No `CITATION.cff`, `.zenodo.json`, DOI, or ORCID exists. #3604
  (citation metadata) is closed, but no artefact landed.
- **Proposal:**
  - Add `CITATION.cff` (the root allowlist from #4128 needs updating) and
    `.zenodo.json`.
  - Enable the GitHub–Zenodo release integration.
  - Mint a concept DOI plus a DOI per version.
- **Acceptance criteria:**
  - [ ] GitHub shows "Cite this repository".
  - [ ] A DOI badge appears on About and Cite.
  - [ ] The ORCID of the author is in the metadata.
  - [ ] #3604 is referenced and the gap it left is explained.

#### WEB-07.2 — Per-page citation metadata and a "Cite this page" block

- **Priority:** P0 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Proposal:**
  - Set the Quarto `citation:` block and `google-scholar: true` project-wide,
    so each page emits `citation_*` meta tags and a BibTeX/CSL download.
  - The header card (WEB-03.2) links the block.
- **Acceptance criteria:**
  - [ ] Every article emits `citation_title`, `citation_author`, and
        `citation_publication_date`.
  - [ ] BibTeX download works.
  - [ ] Validated with a Google Scholar metadata checker on three sample
        pages.

#### WEB-07.3 — Real dates and per-article change history

- **Priority:** P0 · **Labels:** `type:bug`, `complexity:routine`, `tier:cli`
- **Problem:** Ten articles use `date: today`, including theory Parts 1–5,
  the manifesto, and rotation-representations. The date shown is therefore
  the build date. There is no per-article changelog.
- **Proposal:**
  - Backfill `date` from the git first-commit date.
  - Derive `date-modified` from the last substantive change, via a script.
  - Add an optional `changes:` front-matter list rendered as a "Revision
    history" section.
- **Acceptance criteria:**
  - [ ] Zero `date: today` in rendered sources, enforced by pytest.
  - [ ] Revision history appears on core pages.
- **Enables:** "What's new" (WEB-01.2).

#### WEB-07.4 — ScholarlyArticle and Book JSON-LD

- **Priority:** P1 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:** `_includes/article-schema.html` is referenced by no file. It
  would also break if used: `{{< meta >}}` does not expand inside raw HTML,
  and its author URL is wrong.
- **Proposal:**
  - Generate per-page JSON-LD through a Lua filter or post-render script,
    using `ScholarlyArticle`, `Book`, `Chapter`, `Dataset`, and
    `SoftwareSourceCode`.
  - Delete the dead include.
- **Acceptance criteria:**
  - [ ] Valid in the Schema.org validator for sample pages of each type.
  - [ ] The dead include is removed.

#### WEB-07.5 — Deduplicate and reconcile bibliography databases

- **Priority:** P1 · **Labels:** `type:bug`, `complexity:complex`, `tier:cli`
- **Problem:**
  - 183 keys are duplicated across the seven globally loaded `.bib` files.
  - 33 DOIs sit under different keys, with conflicting metadata (e.g.
    `Penner2001`/`penner2003`, `Sprigings2005`/`sprigings2000`).
  - `club-fitting.bib`, `nullspace-rigor.bib`, and `strokes-gained-rigor.bib`
    rely on per-page loading.
- **Proposal:**
  - A canonical `references/master.bib` with key aliases.
  - A CI check for duplicate keys and DOIs.
  - Metadata verified against Crossref.
- **Acceptance criteria:**
  - [ ] Zero duplicate keys and zero duplicate DOIs.
  - [ ] The rendered citations are unchanged in meaning, verified by diffing
        the rendered bibliographies.

#### WEB-07.6 — Render or retire the orphaned per-article bibliography files

- **Priority:** P1 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:**
  - 22 `articles/*-bibliography.md` files are not rendered.
  - `proximal-distal-energy-transfer.qmd:1461` links to one of them, which is
    a probable live 404.
  - The pattern is inconsistent: some bibliographies are rendered `.qmd`.
- **Acceptance criteria:**
  - [ ] Every bibliography link resolves.
  - [ ] A single pattern is documented.
  - [ ] Files that add nothing are removed.

#### WEB-07.7 — Rebuild the Datasets page with licences, schemas, and the site's own data

- **Priority:** P1 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Problem:**
  - The page has four third-party cards with truncated descriptions ("golf
    dom", "the complex a"), no licence, size, schema, or access terms.
  - Thumbnails load from `mini.s-shot.ru`.
  - The site's own `data/ztcf/`, `data/research_protocols/`, and `schemas/`
    are not listed.
- **Proposal:**
  - A generated catalogue from `data/datasets.yml`, with licence, size,
    modality, access, citation, schema, and SHA-256 for each entry.
  - Add an "AffineDrift data artefacts" section.
  - Self-host the thumbnails.
- **Acceptance criteria:**
  - [ ] No truncated text.
  - [ ] No third-party thumbnail host.
  - [ ] Every entry has licence and access fields.
  - [ ] The site's own artefacts are listed with checksums.

#### WEB-07.8 — Content and data licensing

- **Priority:** P1 · **Labels:** `type:process`, `judgement:design`, `tier:strong`
- **Problem:** `LICENSE` is MIT (code). `COPYRIGHT.md` separates content
  types, but the site shows no licence and no data licence is declared.
- **Acceptance criteria:**
  - [ ] Owner decision (D7).
  - [ ] Footer licence notice.
  - [ ] SPDX identifiers in dataset metadata.
  - [ ] Licence shown on the Cite page.

#### WEB-07.9 — Print and PDF editions for books and core series

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:complex`, `tier:cli`
- **Problem:**
  - PDFs exist only for the proximal–distal journey and monograph.
  - `books/index.qmd:22` notes that the work is not archival or PID-qualified.
  - Two `@media print` blocks compete (`css/print.css`, `styles.css:1783`),
    and the page size is A4 only.
- **Proposal:**
  - Reproducible PDF builds per book and series, attached to releases and
    covered by the DOI.
  - Consolidate the print CSS and support Letter and A4.
- **Acceptance criteria:**
  - [ ] PDFs built in CI and linked from the header card.
  - [ ] One print stylesheet.
  - [ ] Print includes typeset math (see WEB-11.3).

#### WEB-07.10 — Render `PARAMETERS.md` and a notation quick-reference card

- **Priority:** P2 · **Labels:** `type:content`, `complexity:simple`, `tier:cli`
- **Problem:**
  - `PARAMETERS.md` is rendered nowhere.
  - Core articles link to `notation.html` only three times.
  - `pages/notation.qmd` duplicates its heading and a manual table of
    contents.
- **Acceptance criteria:**
  - [ ] Parameters page rendered.
  - [ ] A one-page printable notation card.
  - [ ] Every core page links notation from its header card.
  - [ ] Duplicate heading and table of contents removed.

#### WEB-07.11 — Author authority page

- **Priority:** P1 · **Labels:** `type:content`, `judgement:design`, `tier:strong`
- **Problem:** `pages/about.qmd` has 318 words: no photo, CV, publications,
  ORCID, statement of funding or independence, or conflict-of-interest
  statement.
- **Proposal:**
  - Separate "About the project" from "About the author".
  - Add: credentials; relevant experience; methodological stance; the
    AI-assistance disclosure policy (how agents contribute and how the author
    reviews their output); funding and independence; conflicts; ORCID.
- **Acceptance criteria:**
  - [ ] The page is published.
  - [ ] It is linked from the footer and from every "Cite" block.
  - [ ] The AI-assistance disclosure is written and approved by the owner.

---

### E8 — Visual Explanation and Design System

**Epic labels:** `type:epic`, `area:design`, `judgement:design`, `tier:strong`
**Goal:** A consistent visual language, with a small set of high-quality
explanatory graphics carrying the core ideas to every audience.
**Depends on:** D9.

#### WEB-08.1 — Design system audit and token consolidation

- **Priority:** P1 · **Labels:** `type:design`, `complexity:complex`, `tier:strong`
- **Problem:**
  - A global `* { margin:0; padding:0 }` reset sits on top of Bootstrap
    (`styles.css` ≈L50), which causes cascade fights.
  - There are 30 per-page CSS files.
  - Overflow rules for math are duplicated in `custom.scss` and `styles.css`.
- **Proposal:**
  - Document tokens (colour, type scale, spacing) and components (cards,
    badges, callouts, lay blocks, header cards).
  - Remove the global reset.
  - Consolidate per-page CSS into components.
- **Acceptance criteria:**
  - [ ] A component gallery page (internal).
  - [ ] The CSS budget does not increase.
  - [ ] Visual-regression snapshots approved.
  - [ ] The reset is removed with no regression.

#### WEB-08.2 — Signature explanatory graphic: "drift plus control"

- **Priority:** P0 · **Labels:** `type:design`, `judgement:design`, `tier:strong`
- **Proposal:**
  - A single, commissioned or carefully authored illustration that shows the
    swing as a vector field with a passive "drift" arrow and a golfer "push"
    arrow.
  - Reused on the home page, Start Here, the Big Idea page, the OG card, and
    the theory Part 1 header.
- **Acceptance criteria:**
  - [ ] SVG, accessible (a `title`/`desc` and a long description), legible in
        both themes and at 390 px.
  - [ ] The owner confirms its physical accuracy.

#### WEB-08.3 — Concept diagram set for core ideas

- **Priority:** P1 · **Labels:** `type:design`, `complexity:complex`, `tier:strong`
- **Proposal:** 10–15 diagrams, including:
  - state and state space;
  - vector field;
  - ZTCF as "what if the golfer let go";
  - DCR as a ratio gauge;
  - superposition and where it fails;
  - the kinetic chain;
  - the tangent hyperplane;
  - contraction;
  - inverse vs forward dynamics;
  - the reference-point problem.
- **Acceptance criteria:**
  - [ ] Every diagram is SVG with alt text and a long description.
  - [ ] Source files are kept in the repository.
  - [ ] Each is placed on its canonical page and in the glossary entry.

#### WEB-08.4 — Short animated explainers

- **Priority:** P2 · **Labels:** `type:design`, `complexity:complex`, `tier:strong`
- **Proposal:**
  - Two or three 30–90-second animations (for example with Manim, generated
    from `src/` trajectories): drift vs control in a swing; ZTCF.
  - Captioned, with transcripts.
- **Acceptance criteria:**
  - [ ] Captions and transcripts.
  - [ ] `prefers-reduced-motion` respected.
  - [ ] Each video under 3 MB, served as MP4/WebM with a poster image.

#### WEB-08.5 — Adopt Quarto dark theme support

- **Priority:** P2 · **Labels:** `type:chore`, `complexity:complex`, `tier:cli`
- **Problem:**
  - The theme declares only `light: [cosmo, custom.scss]`.
  - Dark mode is a custom override (`styles.css` ≈L2964-3070) that bypasses
    Quarto's dark syntax highlighting.
  - The toggle is appended after DOMContentLoaded, which can shift the layout.
- **Acceptance criteria:**
  - [ ] Quarto `dark:` theme configured.
  - [ ] Code highlighting correct in both themes.
  - [ ] No layout shift from the toggle (CLS contribution 0).
  - [ ] Existing Jest dark-mode tests pass.

#### WEB-08.6 — Typography and reading comfort

- **Priority:** P2 · **Labels:** `type:design`, `complexity:routine`, `tier:cli`
- **Proposal:**
  - Set a measure of 60–75 characters for prose.
  - Tune line height for math-heavy text.
  - Self-host fonts (see WEB-10.5).
  - Set consistent heading scales.
- **Acceptance criteria:**
  - [ ] Measured prose width within the target at 1440 px.
  - [ ] No font requests to third parties.

#### WEB-08.7 — Replace heavy GIFs with video and optimise images

- **Priority:** P3 · **Labels:** `type:chore`, `complexity:simple`, `tier:ollama`
- **Problem:** `static/images/A-Dead-Fish-Swims.gif` is 1.78 MB.
- **Acceptance criteria:**
  - [ ] GIFs over 300 KB converted to MP4/WebM.
  - [ ] Images served as responsive `srcset` or WebP where applicable.

#### WEB-08.8 — Home and Start Here visual QA across viewports and themes

- **Priority:** P2 · **Labels:** `type:test`, `complexity:routine`, `tier:cli`
- **Acceptance criteria:**
  - [ ] Approved visual snapshots at 390, 768, and 1440 px in both themes
        for the new pages.
  - [ ] Coordinated with the #4089 viewport contract.

---

### E9 — Accessibility Conformance

**Epic labels:** `type:epic`, `area:a11y`, `tier:strong`
**Goal:** WCAG 2.2 AA across all routes, both themes, and mobile and desktop,
enforced by CI.
**Coordinate with:** #4139 (the axe violations) and #4140 (excluded browser
tests). This epic adds the scope #4139 lacks; it does not replace it.

#### WEB-09.1 — Make the axe scan fail on serious and critical findings

- **Priority:** P0 · **Labels:** `type:ci`, `complexity:complex`, `tier:cli`
- **Problem:** `ci-standard.yml:623-640` runs with `--axe warn` over 247
  serious/critical violations on 163 routes (#4139).
- **Acceptance criteria:**
  - [ ] Violations are burned down under #4139.
  - [ ] The step is switched to `--axe fail`.
  - [ ] No per-rule suppressions without a linked issue.

#### WEB-09.2 — Scan dark theme and mobile viewports

- **Priority:** P1 · **Labels:** `type:ci`, `complexity:routine`, `tier:cli`
- **Problem:** The scan uses `--viewports desktop-small --themes light` only.
- **Acceptance criteria:**
  - [ ] The axe matrix includes dark theme and a 390 px viewport.
  - [ ] New violations are triaged into #4139 or new issues.

#### WEB-09.3 — Restore the ten excluded browser tests

- **Priority:** P1 · **Labels:** `type:test`, `complexity:complex`, `tier:cli`
- **Problem:** `ci-standard.yml:591` uses `--grep-invert` to exclude tests,
  among them WCAG AA contrast in both themes, the offline homepage, and the
  mobile menu (#4140).
- **Acceptance criteria:**
  - [ ] All ten tests pass and are re-enabled.
  - [ ] The `--grep-invert` list is removed.
  - [ ] The underlying defects are fixed, never the tests loosened.

#### WEB-09.4 — Cross-browser coverage

- **Priority:** P2 · **Labels:** `type:ci`, `complexity:routine`, `tier:cli`
- **Problem:** CI runs Chromium only. Firefox, WebKit, and mobile projects in
  `playwright.config.js` run locally only.
- **Acceptance criteria:**
  - [ ] A nightly job runs Firefox and WebKit on a representative route set.
  - [ ] Failures open issues automatically, deduplicated by title.

#### WEB-09.5 — Math accessibility verification

- **Priority:** P1 · **Labels:** `type:test`, `complexity:routine`, `tier:cli`
- **Problem:**
  - The CSP `connect-src 'self'` (`_includes/site-head.html`) may block
    MathJax speech-rule locale fetches.
  - The effect of lazy typesetting on screen readers is unverified.
- **Acceptance criteria:**
  - [ ] A screen-reader test (NVDA or VoiceOver) on three math-heavy pages,
        with results recorded.
  - [ ] The explorer and speech work without CSP errors, or assets are
        self-hosted.
  - [ ] Findings are filed.

#### WEB-09.6 — Skip link and focus order without JavaScript

- **Priority:** P2 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:** The skip link is injected by JS (`js/navigation.js:627-648`),
  and may duplicate Quarto's built-in link.
- **Acceptance criteria:**
  - [ ] Exactly one skip link, present in the static HTML.
  - [ ] Focus order verified on the home page, Start Here, and one article.

#### WEB-09.7 — Wire alt-text and long-description validation into CI

- **Priority:** P2 · **Labels:** `type:ci`, `complexity:simple`, `tier:cli`
- **Problem:** `scripts/validate_accessibility.py` exists but is not wired
  into CI.
- **Acceptance criteria:**
  - [ ] The check runs in `quality-gate`.
  - [ ] Complex figures and diagrams (E8) require a long description.

#### WEB-09.8 — Accessibility statement page

- **Priority:** P3 · **Labels:** `type:content`, `complexity:simple`, `tier:cli`
- **Acceptance criteria:**
  - [ ] A page stating the conformance target, known issues (linked to
        #4139), and a contact route for barriers.

---

### E10 — Performance, SEO, and Privacy

**Epic labels:** `type:epic`, `area:website`, `tier:cli`
**Goal:** Fast pages within a measured budget, correct discovery by search
engines and scholarly indexes, and no unnecessary third-party exposure of
readers.

#### WEB-10.1 — Runtime performance budget (Lighthouse CI or equivalent)

- **Priority:** P1 · **Labels:** `type:ci`, `complexity:routine`, `tier:cli`
- **Problem:** No runtime budget exists; the existing budgets are static-source
  checks. Math pages pull ≈1 MB of MathJax.
- **Acceptance criteria:**
  - [ ] LCP, CLS, TBT, and page weight measured on ten representative
        routes.
  - [ ] Budgets committed in `config/`.
  - [ ] CI fails when a budget regresses beyond the committed threshold.

#### WEB-10.2 — Fix robots.txt

- **Priority:** P0 · **Labels:** `type:bug`, `complexity:trivial`, `tier:ollama`
- **Problem:** `robots.txt` has `Disallow: /site_libs/` (render-critical CSS
  and JS) and `Crawl-delay: 1`, which Google ignores.
- **Acceptance criteria:**
  - [ ] Both lines removed.
  - [ ] The page is confirmed renderable in a search-console URL inspection.

#### WEB-10.3 — Remove stale root sitemap.xml and feed.xml

- **Priority:** P2 · **Labels:** `type:chore`, `complexity:trivial`, `tier:ollama`
- **Problem:** Deploy regenerates both into `docs/`. The root copies are stale
  (feed dated 10 Jun 2026) and misleading.
- **Acceptance criteria:**
  - [ ] Root copies deleted or git-ignored.
  - [ ] The generators are documented.
  - [ ] The feed carries real article dates (after WEB-07.3).

#### WEB-10.4 — Use one canonical host

- **Priority:** P2 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:** `CNAME` and `site-url` use the apex domain, while
  `deploy-website.yml` `PUBLIC_SITE_URL` uses `www`.
- **Acceptance criteria:**
  - [ ] One host is used in all configuration.
  - [ ] The other host 301-redirects.

#### WEB-10.5 — Self-host fonts and use privacy-preserving embeds

- **Priority:** P1 · **Labels:** `type:privacy`, `complexity:simple`, `tier:cli`
- **Problem:** Google Fonts (Playfair Display) and YouTube frames expose
  visitor IP addresses to third parties.
- **Acceptance criteria:**
  - [ ] Fonts served from the site.
  - [ ] YouTube embeds use `youtube-nocookie.com`, or a click-to-load facade.
  - [ ] The CSP is updated accordingly.

#### WEB-10.6 — Remove the unused metrics.js preload

- **Priority:** P3 · **Labels:** `type:bug`, `complexity:trivial`, `tier:ollama`
- **Problem:** `_includes/site-head.html` preloads `/js/metrics.js` on every
  page, but only `resources/bibliography.qmd:76` uses it.
- **Acceptance criteria:**
  - [ ] No unused-preload console warnings on any route.

#### WEB-10.7 — Titles and meta descriptions for every page

- **Priority:** P1 · **Labels:** `type:bug`, `complexity:simple`, `tier:ollama`
- **Problem:** The home page title is "Home", and many descriptions are too
  thin for search previews.
- **Acceptance criteria:**
  - [ ] Every page has a unique title and a 70–160-character description.
  - [ ] A pytest enforces both.
- **Related:** WEB-02.8.

#### WEB-10.8 — Privacy policy page

- **Priority:** P2 · **Labels:** `type:content`, `complexity:simple`, `tier:cli`
- **Problem:** `metrics.js` stores data only in localStorage and is
  privacy-safe, but nothing tells readers what is and is not collected.
- **Acceptance criteria:**
  - [ ] A page covering local storage, the service worker, embeds, and
        analytics (per D6).
  - [ ] Linked from the footer.

#### WEB-10.9 — Performance of MathJax-heavy pages

- **Priority:** P2 · **Labels:** `type:perf`, `complexity:complex`, `tier:cli`
- **Proposal:** Evaluate a smaller MathJax component build (the TeX input and
  CHTML output actually used), or build-time pre-rendering of static
  equations to SVG or MathML for large chapters.
- **Acceptance criteria:**
  - [ ] Measured before and after on the three heaviest chapters.
  - [ ] No change in rendering or accessibility (see WEB-09.5).

#### WEB-10.10 — Social cards per page

- **Priority:** P3 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Proposal:** Generate per-series or per-book OG images (title, badge, and
  the signature graphic) instead of one site-wide card.
- **Acceptance criteria:**
  - [ ] Generated at build time.
  - [ ] Validated with a social-card debugger on three pages.

---

### E11 — Mathematical Typesetting and Notation

**Epic labels:** `type:epic`, `area:math`, `tier:cli`
**Goal:** Consistent, cross-referenceable, accessible mathematics that obeys
`NOTATION.md` everywhere.

#### WEB-11.1 — Use one equation-numbering scheme

- **Priority:** P1 · **Labels:** `type:bug`, `complexity:complex`, `tier:cli`
- **Problem:**
  - `_includes/mathjax-loader.html` sets `tags: 'ams'`, so MathJax numbers raw
    `equation`/`align` environments.
  - 70 files use Quarto `{#eq-}` numbering.
  - Five files use raw `\label{eq:...}`: `ch05_optimal_control.qmd` (21
    environments), `ch09_parallel_mechanisms_constrained_dynamics.qmd` (32),
    `ch03b_*`, `volume2_content.qmd`, and `superposition.qmd`.
- **Acceptance criteria:**
  - [ ] All five files converted to `{#eq-}`.
  - [ ] `tags` set to `'none'`.
  - [ ] Cross-references verified by a pytest over the sources.

#### WEB-11.2 — Remove duplicate math overflow rules

- **Priority:** P3 · **Labels:** `type:chore`, `complexity:simple`, `tier:cli`
- **Problem:** Display-math overflow is defined in both `custom.scss` and
  `styles.css`, with different values.
- **Acceptance criteria:**
  - [ ] One rule set.
  - [ ] The 390 px mobile math snapshots are unchanged.

#### WEB-11.3 — Verify lazy typesetting for print and in-page find

- **Priority:** P2 · **Labels:** `type:test`, `complexity:routine`, `tier:cli`
- **Problem:** `loader.load: ['ui/lazy']` leaves off-screen math as raw TeX
  until it is scrolled into view. **Verify on live site.**
- **Acceptance criteria:**
  - [ ] A Playwright print-to-PDF test shows typeset math on a long chapter.
  - [ ] If it fails, typesetting is forced before print (`beforeprint`
        handler).

#### WEB-11.4 — Enforce $G(x)$ notation and add a notation lint

- **Priority:** P1 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:** Lowercase $g(x)$ appears on the home page (`index.qmd:44`),
  `superposition.qmd`, `ch03_superposition.qmd`, the Unified Thesis, and
  12 critique files. `NOTATION.md:342-346` forbids it.
- **Acceptance criteria:**
  - [ ] All occurrences fixed, or allowlisted where a critique quotes
        external notation.
  - [ ] A pytest lint over `.qmd`, `.md`, and `.tex` sources.

#### WEB-11.5 — Standardise the DCR name

- **Priority:** P1 · **Labels:** `type:bug`, `complexity:simple`, `tier:cli`
- **Problem:** DCR is expanded three ways: "drift-control ratio" (28 files),
  "controllability-drift ratio" (4), and "drift-to-control ratio" (2). The DCR
  slug is `controllability-drift-ratio`, but its title is "Drift, Control
  Capacity and Golf-Swing Correction".
- **Acceptance criteria:**
  - [ ] One expansion in `NOTATION.md` and everywhere else.
  - [ ] Slug aligned with an alias (WEB-02.9).
  - [ ] Term added to the terminology baseline.

#### WEB-11.6 — Symbol hover references

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:complex`, `tier:strong`
- **Proposal:**
  - Extend the glossary shortcode (WEB-01.5) to key symbols ($f$, $G$, $u$,
    $x$, $M(q)$, $C(q,\dot q)$) using MathJax `\class{}` or `\href{}`.
  - Interacting with a symbol shows its definition from `NOTATION.md`.
- **Acceptance criteria:**
  - [ ] Works with keyboard and screen readers.
  - [ ] Opt-in per page.
  - [ ] No effect on MathJax performance beyond the budget.

#### WEB-11.7 — Harden the MathJax integration against Quarto upgrades

- **Priority:** P3 · **Labels:** `type:chore`, `complexity:routine`, `tier:cli`
- **Problem:** `html-math-method` points to an inert, comment-only
  `js/equation-runtime-gate.js`, while the real configuration lives inline in
  a header include. This is fragile across Quarto upgrades.
- **Acceptance criteria:**
  - [ ] A render test on a Quarto version bump confirms a single MathJax
        runtime and correct typesetting.
  - [ ] The mechanism is documented in `docs/MATHJAX-MOBILE.md`.

---

### E12 — Editorial Voice and Plain-Language Standard

**Epic labels:** `type:epic`, `area:content`, `judgement:design`, `tier:strong`
**Goal:** Reader-facing prose that is precise, confident, and readable. Epistemic
limits are stated once, in structured form, and repository-internal
vocabulary is kept out of reader text.

#### WEB-12.1 — Write the editorial style guide

- **Priority:** P0 · **Labels:** `type:process`, `judgement:design`, `tier:strong`
- **Proposal:** `docs/development/editorial-style-guide.md` covering:
  - voice (confident about the mathematics, explicit about scope);
  - where caveats go (the WEB-03.4 block);
  - glossary linking;
  - readability targets per layer (lay block ≤ grade 10; body unconstrained);
  - analogy rules ("say where the analogy breaks");
  - banned internal vocabulary in reader prose (WEB-12.2);
  - capitalisation, which the title-case hook already covers.
- **Acceptance criteria:**
  - [ ] Guide approved by the owner.
  - [ ] Referenced from `CONTRIBUTING.md` and the new-article issue template.

#### WEB-12.2 — Keep internal governance vocabulary out of reader prose

- **Priority:** P1 · **Labels:** `type:content`, `complexity:routine`, `tier:cli`
- **Problem:** Reader-facing pages use "governed" (72 occurrences),
  "qualified" (82), "provenance" (52), "protected" (16), and "fail-closed"
  (8) in repository-specific senses.
- **Proposal:**
  - Replace these with plain equivalents, or link them to a glossary entry.
  - Add a lint that warns when the terms appear outside evidence and
    developer pages.
- **Acceptance criteria:**
  - [ ] At least a 75 % reduction on reader pages.
  - [ ] The lint runs in CI in warning mode, then blocks.

#### WEB-12.3 — Caveat consolidation pass on core pages

- **Priority:** P1 · **Labels:** `type:content`, `judgement:contested`, `tier:strong`
- **Problem:** "Does not establish" appears 122 times, and scope caveats
  repeat within paragraphs, for example on `pages/tools.qmd`.
- **Proposal:** After WEB-03.4 lands, move repeated caveats into the
  structured block and keep only the caveats needed locally for correctness.
- **Acceptance criteria:**
  - [ ] No limitation is lost; a reviewer checks the before/after diff.
  - [ ] A measurable reduction in inline caveat phrases on each converted
        page.

#### WEB-12.4 — Plain-language rewrite of entry pages

- **Priority:** P1 · **Labels:** `type:content`, `judgement:design`, `tier:strong`
- **Proposal:** Rewrite the home page, Start Here, Overview, About, Tools,
  Learning Paths, the Books hub, and the Resources hub to the style guide.
- **Acceptance criteria:**
  - [ ] Readability grade ≤ 10 on hub pages.
  - [ ] Owner approval.
  - [ ] No loss of scope statements.

#### WEB-12.5 — Readability measurement tool

- **Priority:** P2 · **Labels:** `type:tooling`, `complexity:routine`, `tier:cli`
- **Proposal:** `scripts/check_readability.py` computes the grade level for
  lay blocks, `summary-plain`, and hub pages, excluding math and code.
- **Acceptance criteria:**
  - [ ] Tested with pytest.
  - [ ] Advisory in CI, with a report artefact.
  - [ ] Thresholds from WEB-12.1.

#### WEB-12.6 — Consolidate the manifesto

- **Priority:** P2 · **Labels:** `type:content`, `complexity:simple`, `tier:cli`
- **Problem:**
  - `pages/drifter-manifesto.qmd` ("Series Index") and
    `articles/drifter-manifesto.qmd` ("Single-File Edition") coexist.
  - Both are categorised `critique`.
  - The navbar target lacks a series sidebar.
- **Acceptance criteria:**
  - [ ] One canonical page, per WEB-02.4.
  - [ ] Category corrected to `opinion` or `editorial`.
  - [ ] Clearly labelled Opinion.

#### WEB-12.7 — Unify the contact channel and split About from Contact

- **Priority:** P2 · **Labels:** `type:bug`, `complexity:trivial`, `tier:ollama`
- **Problem:** Contact is `@AffineDrift.com` on About and Contact but a Gmail
  address on the 404 page. About is titled "About & Contact" while a separate
  Contact page exists.
- **Acceptance criteria:**
  - [ ] One address everywhere.
  - [ ] About retitled.
  - [ ] Contact is the single contact page.

---

### E13 — Build, Reliability, and Maintainability

**Epic labels:** `type:epic`, `area:infra`, `tier:cli`
**Goal:** Faster feedback, fewer stale artefacts, and a site that one
maintainer can sustain.

#### WEB-13.1 — Cache Quarto renders in CI

- **Priority:** P2 · **Labels:** `type:ci`, `complexity:complex`, `tier:cli`
- **Problem:** The ≈14-minute full render runs in both the PR end-to-end job
  and in deploy, with no cache.
- **Acceptance criteria:**
  - [ ] Cache `.quarto/` keyed on source hashes, or render incrementally for
        PRs.
  - [ ] Median PR end-to-end time reduced by ≥ 30 %.
  - [ ] Deploy still does a clean full render.

#### WEB-13.2 — Report broken external links as issues

- **Priority:** P2 · **Labels:** `type:ci`, `complexity:routine`, `tier:cli`
- **Problem:**
  - In `link-checker.yml`, the external-URL check does not block and reports
    to no one.
  - The internal step uses a convoluted `continue-on-error`.
- **Acceptance criteria:**
  - [ ] The weekly external-link report opens or updates a single tracking
        issue (one issue, not one per link).
  - [ ] DOI links are checked through doi.org.
  - [ ] archive.org fallbacks are suggested for dead links.

#### WEB-13.3 — Separate internal documentation from the Quarto output directory

- **Priority:** P2 · **Labels:** `type:chore`, `complexity:complex`, `tier:cli`
- **Problem:**
  - `output-dir: docs` is also where 182 tracked internal files live (ADRs,
    development docs, CSS plans).
  - They are pruned at deploy by `scripts/prune_internal_docs_from_deploy.py`.
- **Acceptance criteria:**
  - [ ] Either the output directory or the internal docs move, for example to
        `_site/` or `dev-docs/`.
  - [ ] The prune script is retired or simplified.
  - [ ] All references and the CSS-mirror rule updated.
  - [ ] The CLAUDE.md and AGENTS.md sources updated in Repository_Management
        where the managed sections mention paths.

#### WEB-13.4 — Remove legacy cruft

- **Priority:** P3 · **Labels:** `type:chore`, `complexity:simple`, `tier:ollama`
- **Items:**
  - `legacy-pages/`;
  - `_includes/home-sidebar-content.html` (unused, with stale names);
  - `js/pdf.js` (dead; overlaps `ui-components.js:303`);
  - `listings.json` (`[]`);
  - the broken `preview-articles.sh` (serves `_site/`);
  - the stale `start-preview.sh`;
  - duplicate `.Jules/` and `.jules/` directories.
- **Acceptance criteria:**
  - [ ] Each item removed or fixed.
  - [ ] The root allowlist (#4128) updated.
  - [ ] No broken references.

#### WEB-13.5 — Consolidate the 15 inline "Recent" history scripts

- **Priority:** P3 · **Labels:** `type:chore`, `complexity:routine`, `tier:cli`
- **Problem:** Fifteen `.qmd` files carry inline copies of a localStorage
  history script that reimplement `js/history.js`. On the Datasets page it
  records only the page itself.
- **Acceptance criteria:**
  - [ ] All inline copies replaced by `js/history.js`, or the feature removed
        where it adds nothing.
  - [ ] Jest tests for `history.js` and `home.js`.

#### WEB-13.6 — Service-worker cache busting by content hash

- **Priority:** P3 · **Labels:** `type:chore`, `complexity:routine`, `tier:cli`
- **Problem:** The content-hash cache-busting note (#1459) in `service-worker.js` is unresolved. The offline test is
  excluded (#4140).
- **Acceptance criteria:**
  - [ ] Content-hash precache manifest.
  - [ ] The offline test re-enabled and passing.

#### WEB-13.7 — Align Node versions

- **Priority:** P3 · **Labels:** `type:chore`, `complexity:trivial`, `tier:ollama`
- **Problem:** The `Dockerfile` uses `NODE_MAJOR=20`; CI uses 22.
  `CLAUDE.md` also says Node 20.
- **Acceptance criteria:**
  - [ ] One Node version, pinned in one file (for example `.nvmrc`) and read
        by both CI and the Dockerfile.

#### WEB-13.8 — Content inventory and ownership map

- **Priority:** P2 · **Labels:** `type:process`, `complexity:routine`, `tier:cli`
- **Proposal:**
  - A generated inventory of every rendered page: word count, status,
    last-reviewed date, canonical pointer, inbound links, and outbound broken
    links.
  - Used to pick consolidation and retirement candidates, and to track
    burndown.
- **Acceptance criteria:**
  - [ ] A CSV/JSON artefact produced in CI.
  - [ ] A dashboard page, internal or public.
  - [ ] Pages with fewer than 300 words and no Planned badge are flagged.

#### WEB-13.9 — Content deprecation and archive policy

- **Priority:** P3 · **Labels:** `type:process`, `judgement:design`, `tier:strong`
- **Proposal:**
  - A written policy: when a page is Deprecated, how it is bannered, when it
    is removed, and how URLs are preserved.
  - Applied to the proximal–distal and tangent-space derivatives (WEB-02.4).
- **Acceptance criteria:**
  - [ ] Policy published in `CONTRIBUTING.md`.
  - [ ] Deprecated banner component.
  - [ ] Applied to at least one family.

---

### E14 — Reader Validation, Feedback, and Community

**Epic labels:** `type:epic`, `area:website`, `judgement:design`, `tier:strong`
**Goal:** Improvements are guided by evidence from real readers, and readers
have low-friction ways to respond, follow, and contribute.
**Coordinate with:** #4088 (reader validation protocols). This epic supplies
the site surfaces those protocols need.

#### WEB-14.1 — Run the #4088 usability study against the new onboarding

- **Priority:** P1 · **Labels:** `type:research`, `complexity:research`, `tier:strong`
- **Proposal:**
  - Run the preregistered tasks before and after E1 and E2 land.
  - Tasks:
    - find a starting page for your background;
    - explain drift vs control;
    - find the evidence state of the ZTCF claim;
    - cite a page.
  - Use separate lay and technical cohorts.
- **Acceptance criteria:**
  - [ ] Results published, including negative findings.
  - [ ] Never presented as scientific validation.

#### WEB-14.2 — Per-page "Was this helpful? / Report a problem" control

- **Priority:** P2 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Proposal:**
  - A footer control that opens a prefilled GitHub issue from the
    content-correction template, with page URL and revision, or a privacy-safe
    form.
  - No third-party tracking.
- **Acceptance criteria:**
  - [ ] Works without a GitHub account through a fallback email link.
  - [ ] Keyboard accessible.
  - [ ] The template receives the page URL and commit.

#### WEB-14.3 — Privacy-preserving navigation analytics

- **Priority:** P3 · **Labels:** `type:feature`, `judgement:contested`, `tier:strong`
- **Proposal:** Implement per D6: cookieless, aggregate, self-hosted counts
  of key transitions, such as Start Here → path and article → evidence.
- **Acceptance criteria:**
  - [ ] The privacy page (WEB-10.8) is updated first.
  - [ ] No personal data is collected.
  - [ ] Results are treated as interface evidence only.

#### WEB-14.4 — "What's new" feed and optional newsletter

- **Priority:** P3 · **Labels:** `type:feature`, `complexity:routine`, `tier:cli`
- **Proposal:**
  - A dated changelog of substantive content updates, drawn from front-matter
    `changes:` (WEB-07.3).
  - An RSS feed with real dates.
  - An optional email digest through a privacy-respecting provider.
- **Acceptance criteria:**
  - [ ] The RSS feed validates.
  - [ ] Items link to revision history.

#### WEB-14.5 — Contributor and reviewer guide on the site

- **Priority:** P2 · **Labels:** `type:content`, `complexity:routine`, `tier:cli`
- **Problem:** `pages/collaborate.qmd` offers GitHub issues only.
- **Proposal:** A reader-facing guide covering how to propose a correction,
  critique a claim (linking the critique-response template), contribute a
  dataset, or review a chapter.
- **Acceptance criteria:**
  - [ ] Linked from Collaborate and from every WEB-03.4 block.

#### WEB-14.6 — Issue template for website and UX problems

- **Priority:** P2 · **Labels:** `type:process`, `complexity:simple`, `tier:cli`
- **Problem:** `.github/ISSUE_TEMPLATE/` has content, critique, article,
  resource, and textbook templates, but no website/UX template.
- **Acceptance criteria:**
  - [ ] A template with page URL, viewport, theme, browser, and expected
        versus actual behaviour.

#### WEB-14.7 — Educator resources

- **Priority:** P3 · **Labels:** `type:content`, `judgement:design`, `tier:strong`
- **Proposal:**
  - For instructors in biomechanics, sport science, or control courses: a
    page with suggested modules, problem sets drawn from worked examples
    (WEB-03.6), and widget-based exercises.
  - Licensing terms per D7.
- **Acceptance criteria:**
  - [ ] At least three teaching modules, each with learning objectives and
        exercises with solutions.

---

## 8. Proposed Sequencing

<!-- prettier-ignore -->
| Phase | Theme | Issues (draft IDs) | Why this order |
| --- | --- | --- | --- |
| **0: Decide** | Board decisions and ADRs | D1–D10, WEB-06.1, WEB-12.1, WEB-03.1 | Everything later depends on the audience model, stack, canonical choices, and schema |
| **1: Quick wins** (≈2 weeks) | Defects with outsized effect | WEB-10.2, WEB-01.8, WEB-06.7 (remove stub Colab buttons), WEB-07.3, WEB-11.4, WEB-12.7, WEB-02.3, WEB-10.6, WEB-10.7, WEB-01.10 | Low risk; each removes a visible credibility problem |
| **2: Front door** | Onboarding and navigation | WEB-01.1–01.6, WEB-02.1, WEB-02.2, WEB-02.5, WEB-02.6, WEB-04.1, WEB-04.2, WEB-08.2 | The biggest improvement for lay readers; needs Phase 0 |
| **3: Page model** | Layered template | WEB-03.2–03.5, WEB-01.9, WEB-12.2, WEB-12.3, WEB-03.8 | Converts the core pages; the lay and expert layers coexist |
| **4: Show it** | Visuals and interactivity | WEB-06.2, WEB-06.3, WEB-06.6, WEB-08.3, WEB-06.4, WEB-06.5, WEB-06.8 | The central idea becomes visible and runnable |
| **5: Researcher grade** | Citation and evidence | WEB-07.1, WEB-07.2, WEB-07.4–07.8, WEB-07.11, WEB-05.1–05.5 | Citable, dated, licensed, with claims registered |
| **6: Harden** | Enforcement | WEB-09.1–09.3, WEB-10.1, WEB-10.5, WEB-11.1, WEB-13.1–13.3 | Turns quality into gates so improvements do not regress |
| **7: Validate and extend** | Reader evidence and growth | WEB-14.1, WEB-05.7, WEB-05.8, WEB-05.10, WEB-06.10, WEB-08.4, WEB-14.* | Measure, then invest further where the data says to |

Phases 5 and 6 can run in parallel with Phases 3 and 4 if capacity allows.
The fleet WIP limit for this repository is 2 (`DEVELOPMENT_LOG.md`), so the
default is serial delivery in the order above.

---

## 9. Success Measures

<!-- prettier-ignore -->
| Measure | Baseline (2026-09-29) | Target |
| --- | --- | --- |
| Clicks from home to a lay-appropriate starting page | No such page exists | 1 |
| General readers able to explain drift vs control after 5 minutes (#4088 protocol) | Not measured | ≥ 80 % |
| Registered claims with falsifiers | 1 | ≥ 12 |
| Critiques with unknown severity / resolved critiques | 3 / 0 | 0 / tracked with response windows |
| Core pages with ≥ 1 figure or widget | DCR, ZTCF, superposition: 0 | 100 % of core pages |
| Colab buttons pointing to stub notebooks | All | 0 |
| Pages using `date: today` | 10 | 0 |
| Pages with citation metadata / DOI | 0 / 0 | All articles / every release |
| axe serious and critical violations (CI-enforced) | 247 on 163 routes, warn-only | 0, blocking |
| Browser tests excluded from CI | 10 | 0 |
| Navbar top-level menus with mixed categories | 2 of 5 | 0 |
| Naming collisions (volumes, series, "Part I") | ≥ 4 | 0 |
| Internal governance vocabulary on reader pages | ≈230 occurrences | ≥ 75 % reduction |
| Runtime performance budget | None | Committed and enforced |

---

## 10. Relationship to Existing Work (Do Not Duplicate)

<!-- prettier-ignore -->
| Existing issue(s) | Topic | How this backlog relates |
| --- | --- | --- |
| #4008 (epic), #4010, #4022–#4030 | Governed companion dashboard (Package B) | Out of scope here. WEB-06.13 only fixes display metadata and coordinates with #4023/#4024 |
| #4084, #4086, #4087, #4032 | Claim, critique, falsification explorer (Package C) | WEB-05.2 and WEB-05.7 are candidate first increments. They must be implemented inside those issues, not beside them |
| #4028, #4029, #4042 | Reproducible study workbench (Package D) | E6 widgets are **teaching** tools, labelled exploratory. The governed reproductions stay in Package D |
| #4088 | Reader validation (Package E) | WEB-14.1 runs that protocol against the new onboarding |
| #4085, #4086 | Shared evidence semantics | E4 is the presentation layer over those semantics |
| #4089 | Whole-site desktop viewport contract | WEB-08.8 extends snapshots to the new pages |
| #4139, #4140 | axe violations; excluded browser tests | WEB-09.1 and WEB-09.3 close them; WEB-09.2 extends the scope |
| #3900, #3901 | Related-articles coverage | WEB-03.5 generalises and must absorb, not duplicate, this work |
| #3904 (epic #3896) | Series navigation | WEB-02.5 completes the prev/next piece if #3904 has not |
| #4409 / PR #4411 | Persona start paths | WEB-01.3 extends the delivered personas |
| #4021, #4054–#4063 | Site-wide scientific trust review | E5 depends on those reviews' findings; it does not re-audit content |
| #4128 | Root-file allowlist | WEB-07.1 and WEB-13.4 must update it |
| #3604 (closed) | Citation metadata | WEB-07.1 and WEB-07.2 deliver what #3604 described; the closure reason should be checked |
| #4253, #4255, deferred-validation catalogue | Physical evidence | WEB-05.5 and WEB-05.6 record plans only; no measurement is simulated |

---

_Prepared as a Board review draft. After approval, file each epic first and
link its child issues as sub-issues. Apply the proposed labels (or the
current fleet taxonomy if it has changed), and replace each draft ID with its
GitHub number in this file._
