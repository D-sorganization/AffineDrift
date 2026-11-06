# Alpha War v0 — source clearance pending (Dieter action list)

Do **not** contact subjects. Clear or redact before any publication beyond this unpublished draft.

| ID     | Source                                                                                     | Status in draft                                                   | Clearance action                                                                              |
| ------ | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| CLR-01 | Private coaching Facebook forum (formerly cited with numeric group ID)                     | Paraphrase only; ID removed                                       | Written permission from forum admins **or** remove all non-public thread references           |
| CLR-02 | VRF-05 Croker (2019) monograph                                                             | Limited circulation                                               | Confirm quotation rights / paraphrase                                                         |
| CLR-03 | VRF-06 Jacobs (2020) _Look Inside the Swing_                                               | Limited circulation                                               | Library copy + page-level quote audit                                                         |
| CLR-04 | VRF-07 Manzella webinars / technical notes                                                 | Private archive                                                   | Archival video review + quote clearance                                                       |
| CLR-05 | VRF-08 Sinclair workshop slides                                                            | Unpublished slides                                                | Written permission or paraphrase                                                              |
| CLR-06 | VRF-09 Facebook corpus exports in `corpus/`                                                | Git-excluded local JSON                                           | Verify exports match paraphrases; no raw posts in repo                                        |
| CLR-07 | Golf Biomechanists public permalinks                                                       | Public URLs in working registry                                   | Optional: screenshot archive for dispute resolution                                           |
| CLR-08 | Named third-party Facebook posts (Jacobs, Manzella, Sinclair)                              | Paraphrased in digest                                             | Per #5206: cleared quote or paraphrase without identifying private individuals                |
| CLR-09 | Permalinks into the private _Post Modern Golf_ group (`work/01_corpus_digest.md`, 4 items) | URLs withheld in the working digest; paraphrase only; not cleared | Written permission from group admins **or** keep withheld; never restore the URLs to the repo |

**Repository rule:** `research/alpha-war/corpus/` must remain untracked (see `test_corpus_gitignore.py`).

## Clearance status register (#5366)

Each social-media source is tagged **cleared** or **not cleared**. Nothing is
cleared by this file: only Dieter can clear a source (written permission). The
status below records what the repository may contain today.

| ID     | Status                     | What the repository may contain                                                          |
| ------ | -------------------------- | ---------------------------------------------------------------------------------------- |
| CLR-01 | not cleared                | Paraphrase only; no group ID, no thread URL                                              |
| CLR-06 | not cleared                | Nothing from `corpus/`; the directory stays untracked                                    |
| CLR-07 | unverified (stated public) | Public Golf Biomechanists permalinks; public status is asserted above, not verified here |
| CLR-08 | not cleared                | Paraphrase without identifying private individuals                                       |
| CLR-09 | not cleared                | No URL; a withheld-marker only                                                           |

CLR-02 to CLR-05 cover non-social sources and keep the actions listed above.
`calcs/test_alpha_war_source_clearance.py` pins this register, the absence of
private-group URLs and numeric group IDs in tracked text, and an untracked
`corpus/`.
