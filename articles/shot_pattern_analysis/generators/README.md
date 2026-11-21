# Shot-Pattern Figure Regeneration

AffineDrift publishes the reviewed presentation plates under this directory. Numeric tables and delivery assumptions are vendored under `../data/` and rebuilt with `python3 -m scripts.build_shot_pattern_article_artifacts`.

Full figure regeneration runs in UpstreamDrift after restoring the phase-2 data archives listed in [RELEASE_ASSETS.json](https://github.com/D-sorganization/UpstreamDrift/blob/main/docs/research/shot_pattern_analysis/phase2/RELEASE_ASSETS.json):

```bash
MPLBACKEND=Agg python -m docs.research.shot_pattern_analysis.phase2.presentation_v2.render
```

See [source_manifest.json](../source_manifest.json) for the pinned commit and simulation entrypoints. Refresh `data/headline_paired_sg.csv` from UpstreamDrift `phase2/statistics_v2/headline_dataset.json` at that commit when the study changes.
