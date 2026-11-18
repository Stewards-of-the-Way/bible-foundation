# SOTW Nave/Torrey historical topics importer (v1)

This builds a **separate reference collection** from the ready-made [NEUU Bible Topics Dataset](https://github.com/neuu-org/bible-topics-dataset), combining Nave's *Topical Bible* (1896) and Torrey's *New Topical Textbook* (1897). The imported dataset is **CC BY 4.0**. Preserve NEUU attribution and CCEL digitisation credit; see NEUU's [NOTICE](https://github.com/neuu-org/bible-topics-dataset/blob/main/NOTICE).

## What it builds

- `data/topics/nave-torrey/v1/topics/{LETTER}.json`: original source topic headings, related topics, aspect descriptions and references, with normalized SOTW verse IDs. The historical sections are source text; their content is not reinterpreted or repaired.
- `data/topics/nave-torrey/v1/index/topics.json`: title/slug lookup for **Bible Topics** search tab.
- `data/topics/nave-torrey/v1/index/by-scripture/{BOOK}.json`: reverse Scripture-to-topics links.
- `data/topics/nave-torrey/v1/manifest.json`: SHA-256 file inventory, source commit and license.
- `data/topics/nave-torrey/v1/import-report.json`: any unresolved references, retained for transparent review.

**Not included:** Bible translation text, copyrighted modern definitions, AI-enriched `data/03_pilot`, generated doctrinal conclusions, Jacob Lannom commentary, or edits to Search v1 / CGBC. SOTW's canonically keyed Scriptures remain the link destination. Lannom's authoritative `api/jacob-lannom/v1/current-commentary.json` is independent; later, approved topic associations can join on the SOTW Scripture scope IDs without rewriting either source.

## Reproduction

The upstream commit is intentionally pinned to `eeb9b7418be4d02c497d142da3b9890fad356252` (NEUU `main` checked 2026-11-18). Future upstream updates require a deliberate source pin change, not silent data replacement.

```sh
git clone https://github.com/neuu-org/bible-topics-dataset.git neuu-topics
git -C neuu-topics checkout eeb9b7418be4d02c497d142da3b9890fad356252
python3 scripts/import_neuu_topics.py \
  --source-dir neuu-topics/data/01_parsed \
  --sotw-route-map ../original-language-resources/study-data/v1/route-map.json \
  --output-dir data/topics/nave-torrey/v1 \
  --source-commit eeb9b7418be4d02c497d142da3b9890fad356252
```

Importer refuses nonempty output and incomplete datasets. This avoids replacing accepted data during concurrent or partial work. For a refresh, stage to a clean temporary output directory, inspect its manifest/diff, then replace only `data/topics/nave-torrey/v1/` if authorized. Source reference lists may contain historical or parsing errors. Unresolved records are preserved in `import-report.json` instead of producing invented Bible verse links.

## GitHub Actions

The repository workflow `Import Nave and Torrey Bible Topics` supports `stage_artifact` (default) and `publish_topics`. The first downloads the pinned NEUU dataset, runs offline tests, generates all normalized topic files and attaches them as an artifact, with **no commit**. `publish_topics` does those checks then commits **only** `data/topics/nave-torrey/v1/` to the SOTW Bible Foundation repository. Never run `publish_topics` just to test. The workflow never deploys or edits Search v1, source Bible editions, the Jacob commentary API, or the CGBC player.

## UI integration contract

Search `index/topics.json` for title and optional `see_also`; load the letter shard for the selected topic; show its labeled aspect headings and existing Scripture references, and resolve canonical IDs to the chosen SOTW Bible text. Source label: *Nave/Torrey (NEUU), CC BY 4.0*. If Jacob Lannom's approved contribution is explicitly associated with the same topic, show it as a separate author result from SOTW's primary Jacob API, not a merged citation. **Installing this data does not itself install a UI.**
