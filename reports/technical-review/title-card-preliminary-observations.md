# Volume II Title-Card Paint Investigation

Issue #4868 follows the Volume II review under epic #4009 / corpus #4021. These preliminary observations do not establish a publication defect, a browser defect, or an accepted correction. No publication, CSS, or JavaScript source has changed for this investigation.

## Observations From the Partial Build

The preserved one-route build at localhost:8877 is incomplete: its initial navigation logged 17 missing generated resources and an AnchorJS `TypeError`. The missing resources include Quarto, Bootstrap, search, navigation, and annotation dependencies. This is a limitation of the local baseline, not evidence that those resources are missing in production.

In headed Chrome 154.0.8037.59 at an emulated 1440 × 900 viewport, the first light viewport capture shows the title, description, and reading time. After the UI dark toggle, the first dark viewport capture omits all three texts. The following title-card locator capture, title-only capture, and second viewport capture show them. The capture sequence used `animations: allow`; layout and style metadata were collected afterward and cannot establish the earlier paint state.

A fresh reload followed by an independent native-window capture shows all three texts in dark mode. This was a different navigation, so it is not a simultaneous comparison with the missing-text capture. The actual browser window was 945 pixels wide and clipped the emulated 1440-pixel layout. The three texts fit within the visible region, but this does not verify the entire desktop card on screen. A later viewport-only capture also shows the text, approximately five minutes after reload, with a new-content notification.

The current headed session allowed service workers. The older headless evidence blocked them and initialized the theme through local storage. Timing, navigation history, service-worker state, window geometry, and capture order therefore remain comparison variables. Neither DOM text nor computed visibility establishes that text reached the captured pixels.

## Preserved Evidence

Raw files are retained in `C:/Users/diete/Repositories/Worktrees/AffineDrift-title-card-review`:

- `output/playwright/title-card/baseline-headed-1440-unset-*.png`: four light captures.
- `output/playwright/title-card/baseline-headed-1440-dark-*.png`: four dark captures, in the recorded before/card/title/after sequence.
- `output/playwright/title-card/baseline-headed-dark-single-after-native.png`: later viewport-only control.
- `docs/development/technical-review/title-card-preliminary-artifact-inventory.json`: SHA-256 values for the eight sequential browser captures and the separate native capture; this is an inventory, not a visual pass.
- `docs/development/technical-review/title-card-headed-*-capture.txt`: browser version, capture paths, and post-capture metadata.
- `docs/development/technical-review/title-card-native-baseline-capture.txt`: native screenshot path in the Windows temporary directory.
- `.playwright-cli/console-2026-10-04T06-18-44-134Z.log`: accumulated console output across navigations; its aggregate line counts are not counts of unique missing resources.

The original headless evidence remains in the separate `AffineDrift-dof-chapter-review` worktree. No original screenshots were overwritten. Raw local evidence is not implied to be committed by these references.

## Clean-Build Comparison Still Required

A fresh Git archive of remote-main commit `ecc23b233e54349981db6622238341c6866a298f` is being rendered with pinned Quarto 1.8.26, without a prior render cache. The source archive SHA-256 is `a4c0c5fd7781ccb66fc68cd0b7c3f689ee75849c39ed9c18863775272cf39369`. The scratch site is `C:/Users/diete/AppData/Local/Temp/affine-title-card-clean-iwq8zm00/site`.

The pipeline comprises full HTML rendering, frontend synchronization, CSS bundling, deployment pruning, an explicit-source public manifest, and the publication gate. At this checkpoint rendering is still running; none of the subsequent steps is claimed complete. Preserve the running process and inspect its actual exit before deciding on recovery.

After successful completion, serve this build on a fresh origin and compare fresh headed/headless contexts across desktop/mobile and light/dark. Match browser version, service-worker policy, reduced-motion preference, and theme initialization before varying them individually. Record viewport and actual window dimensions separately. Preserve viewport captures before locator captures, and inspect title, description, and reading-time pixels directly. Record measurement and capture times without implying that asynchronous measurements are simultaneous.

A confirmed source defect requires a focused failing regression and the smallest justified fix. A capture-workflow correction requires evidence that the revised method reliably captures the intended state. Current observations accept neither conclusion.

## Delegation and Review

Four supplied-text agy CLI Gemini 3.8 Flash invocations supported observation planning, inventory drafting, and this note. The first inventory draft was rejected without execution; the revised script was reviewed, amended, and successfully used to hash nine images. The lead removed invented selectors and causal claims from planning advice. The note was revised to distinguish the full-site build from a single-volume build and to avoid claiming measurements at a toggle instant prove paint. Scientific judgments and acceptance remain with the lead.
