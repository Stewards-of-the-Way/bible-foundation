# Architecture 0.1 — portable, not platform-bound

## Separation of concerns

1. **Source archives (intake, restricted as required)**: immutable bytes of lawful downloads, versioned and hashed. Never assume GitHub publication rights.
2. **Canonical reference data**: verse identifiers, source/edition catalogs, dictionary entry identifiers, typed links and evidence citations.
3. **Generated projections**: search indexes, chapter shards, browser-ready resources. Rebuildable from canonical data and pinned source versions.
4. **Applications**: Bible reader, media players, tools for independently controlled congregations. The user interface is not the canonical data.

## Stable IDs

- Scripture reference: `JHN.1.1` (book/chapter/verse in a pinned book-code catalog).
- Edition-specific verse content: `KJV1769:JHN.1.1`, `ASV1901:JHN.1.1`, `BSB:JHN.1.1`, `WEBSTER1833:JHN.1.1`. These are proposed local IDs, not claims of completed edition imports.
- Lexicon entry: `strongs:G3056` or `strongs:H0430`, never an unqualified number.
- Word occurrence: edition-specific tagged-text ID, introduced only after the original-language source and numbering are pinned.
- Source: opaque stable ID bound to edition, source URL, retrieval date, original checksum, rights declaration and evidence locator.

Keep canonical IDs distinct from URLs. URL redirects are a presentation/hosting responsibility. A change of host must never change a verse's canonical ID.

## Scope of this seed

The reference-only fixture deliberately omits translations, commentary, linguistic assertions and word alignments. All links between translations and Greek/Hebrew occurrences require independently verified mapping; Strong's IDs do not automatically establish contextual sense.

## Proposed future directories (create only when needed)

`data/bible/{asv1901,kjv1769,bsb,webster1833}/`, `data/dictionaries/`, `data/original-languages/`, `data/cross-references/`, `data/historical-commentaries/`, `data/translations/histories/`, `source-archives/`, `indexes/`.

Keep generated indexes out of authoritative source directories. Source archives may belong outside this public repository if size or distribution rights require it.

## Multi-church boundary

Reusable software and permissible biblical reference datasets can be shared. Each church owns its own recordings, pastor data, configurations, quote review decisions and access controls. Shared hosting must not turn private data into publicly downloadable JSON.

## Portability

Use UTF-8 and documented JSON formats, unambiguous canonical IDs, validated schemas, pinned input versions and content hashes. Export, reindex and redeploy without needing the original maintainer's account. Keep GitHub as a hosting option, not an identity system for the biblical data.
