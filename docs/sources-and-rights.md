# Source identity, rights and attribution

## Before importing a source

For each exact edition/dataset, record title, responsible author/editor/publisher, edition/year, lawful acquisition URL, retrieval timestamp, source format, SHA-256 of original bytes, source locator, rights statement and its supporting evidence, modifications, attribution obligations, jurisdictional caveats where material, and release decision. Never infer a dataset's rights from a site's reputation or similarly titled edition.

Original Webster **1828** is an historical public-domain text, distinct from later edited or modern presentations; provenance and transcription accuracy still require verification, not recurring relicensing. Original Strong's **1890** dictionaries must be distinguished from later enriched editions. Preserve specific notices for sources distributed under CC BY. BibleHub may be a research/link-out resource, not a bulk content source absent permission.

The repository as a whole is **not** automatically placed under one license: historical public-domain underlying material, third-party CC BY content, independent editorial contributions and application code can have different rights.

## Candidate editions, not ingested

- ASV 1901 (exact printing and electronic transcription to be selected)
- KJV (identify exact standardized 1769-based edition/transcription)
- Berean Standard Bible (use official public-domain declaration and verified distribution files)
- Webster's Bible 1833 (verify original text identity and exact digital edition)

Do not publish translations, editor-added footnotes, images, databases or corpus material until the relevant edition's rights and provenance are recorded.

## Minimal manifest fields

`source_id`, `title`, `edition`, `original_author_or_editor`, `publisher`, `origin_url`, `retrieved_at_utc`, `original_sha256`, `rights_status`, `rights_evidence_locator`, `attribution_text`, `modifications`, `publication_status`.

A planned source has `publication_status: "not_ingested"`; empty or unverified rights fields cannot be treated as release permission.
