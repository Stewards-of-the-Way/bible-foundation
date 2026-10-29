# Translation source intake (v0.2)

**Status: planning and verified source-page discovery, NOT a Bible text import.**

1. Retain the owner-selected selector order: ASV 1901, KJV standardized 1769, BSB, Webster 1833. The Bible reader presents the 66-book Protestant canon; historic Apocrypha and deuterocanonical witnesses remain documented in a separate canon-history collection.
2. Choose a specific upstream publisher/provider release, download the original source archive, record download URI, capture timestamp, full SHA-256, exact edition identifier, format, and accompanying license/permission statement. Do not silently substitute a later release.
3. Audit source text against the stated edition and expected canon; check book coverage, chapter/verse counts, headings, poetry, translator notes, footnotes, introductions, and any Strong's markup without conflating editorial markup with original translation text. Preserve originals unmodified.
4. Only then transform into deterministic canonical IDs (e.g. `JHN.1.1`) plus translation occurrence keys (`KJV:JHN.1.1`) and check round-trip parity. Record variants or versification exceptions rather than forcing mappings.
5. Publish only a verified release and its machine-readable provenance/attribution. Scripture text, editorial history, external scholarly research, and commissioned original commentary must never be mixed or mistaken for one another.
6. For the KJV, note UK printing/Crown-rights nuances even when the source is public domain in the US. For the BSB, retain the publisher's public-domain declaration. Attribution is good practice even where not legally required.

## Reader-facing translation information
Each selected edition will eventually have (a) a short selector summary and (b) a separately researched, cited About page detailing origin, translators, manuscript/textual bases, distinctive characteristics, source edition and lineage. Historical discoveries (e.g. Dead Sea Scrolls) belong in common manuscript-history records linked to editions only where a documented influence exists, never copied as an unqualified claim on every About page.

## Canon and history
The organization presents its Protestant-oriented editorial stance openly without misdescribing Catholic and Orthodox traditions. The Septuagint is an ancient Greek corpus/translation tradition, **not** simply the name of a Catholic Bible. Historical manuscript and canon records present differing canons and evidence fairly without implying endorsement. Never describe councils as simply having invented the Bible.
