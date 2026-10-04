# Volume II Title-Card Investigation Resolution

Issue #4868, under epic #4009 / corpus #4021, resolves as a correction to the
review record. Earlier assertions that the desktop dark screenshots lacked
the title, description and reading time were mistaken interpretations of
displayed previews. The preserved PNGs contain those texts. No CSS, JavaScript
or publication source correction is justified by this investigation.

## Evidence and Correction

The [Pixel Corrigendum](title-card-pixel-corrigendum.json) records image hashes,
half-open pixel bounds and SHA-256 hashes of decoded RGB regions. The lead
independently read the preserved PNGs rather than inferring paint from DOM text
or computed visibility. Exact comparisons passed for all three text regions:

| Case                             | Captures                                                                   | Result                                                |
| -------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------- |
| Deployment baseline, desktop     | Eight viewports: headed/headless, light/dark, before/after locator capture | Identical region bytes within each browser mode       |
| Earlier partial build, desktop   | Four light/dark before/after viewports                                     | Identical region bytes                                |
| Ordinary reader, UI theme toggle | Two light/dark viewports, service workers allowed                          | Identical region bytes                                |
| Native screen recording          | 100 frames                                                                 | One unique RGB hash per text region across all frames |

The native regions contain 6,971, 2,416 and 474 pixels with all RGB components
above 200, respectively. Counts alone would not prove text legibility; exact
region equality and original-resolution visual reinspection supply the relevant
comparison. Frame 64 overlaps the Playwright capture interval. Other windows
occlude the right side of the native browser; these three regions are in the
exposed part. This does not establish full-window correctness or simultaneous
capture of every pixel.

Original-resolution reinspection also confirms visible text in the two original
dark card images from the Volume II review. Their light/dark region hashes are
not identical; they are preserved as legible visual references, not included
in the equality claims above. Six unmodified reference PNGs are committed in
[Title-Card Evidence](title-card-evidence/), including those four original cards
and the ordinary-reader light/dark pair. Additional raw captures and logs remain
in the local QA directories identified in the earlier reports.

The earlier claims that locator captures restored missing text, network-idle
waiting improved paint, and a native frame proved an on-screen failure are
retracted. In particular, the network-idle first-image hashes equal the v3
desktop dark first-image hashes previously described as blank. No browser or
preview-system implementation cause has been established. This is bounded
evidence about the recorded cases, not a universal visual-quality guarantee.

## Baseline Provenance and Failed Attempts

The comparison uses deployment workflow
[37181787221](https://github.com/D-sorganization/AffineDrift/actions/runs/37181787221),
source `ecc23b233e54349981db6622238341c6866a298f`, and artifact `11296206954`.
Its manifest identifies 251 public pages. Full rendering, publication gates,
pre-deployment browser verification and live verification actually executed and
passed. The separate PR #4870 CI browser steps were filtered out; those two
validation accounts must not be conflated.

The local full-build driver timed out after 3,600 seconds. Its child later
reported completed rendering, but its exit code was not observed and five
subsequent pipeline commands never ran. That local pipeline is not accepted as
successful. The earlier one-route build had missing resources and an AnchorJS
error, so it cannot represent a complete deployment.

CLI v1 had a syntax error despite shell exit zero; the result body must also be
checked. Concurrent v2 captures encountered localhost connection refusals and
were excluded. Sequential v3 cases reported no resource or execution errors.
Later caret trials with failed requests were excluded too. A queued local
preview server passed 64 resource requests with 32 workers. Temporary stacking
and caret experiments establish no fix, because no missing-text baseline was
demonstrated. No experimental style was adopted into source.

## Review and Remaining Scope

Nine supplied-text agy CLI Gemini 3.8 Flash invocations supported planning,
inventory scripts and the final corrigendum checklist. The lead rejected or
amended unsupported helper claims, reviewed code before execution and owns the
incorrect visual conclusions corrected here. A separate helper's exact algebra
for queued #4871 remains preparation for the next article review.

Future visual investigations should compare preserved pixel data when preview
readings conflict, verify original-resolution images, distinguish resource
failures from layout defects and record the actual CLI result. This correction
closes the alleged missing-text finding without inventing a source fix. It does
not reopen or broaden the accepted Volume II scientific source review, clear
the remaining corpus, or provide empirical golf validation. Continue with the
queued tangent-framework lay summary, #4871, after this checkpoint is delivered.
