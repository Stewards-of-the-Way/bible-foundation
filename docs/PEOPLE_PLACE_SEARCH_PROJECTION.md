# SOTW Historical People, Places, Events: read-only search projection

## Purpose and exact source
The script `scripts/build_people_place_search.py` consumes the owner-approved **2026-10-25 locked three-file historical reference** under `data/biblical-history/people-time-place/`. It validates **the SHA-256 and byte count from** `docs/biblical-history/people-time-place/CGBC_PERMANENT_LIBRARY_LOCK_2026-10-25.json` **for all three files**, not GitHub file blob SHAs. The SOTW Scripture route map is also an input.

The locked master contains **269 people, 65 places, 186 events, 327 family relationships**, a separate event/time/place joining file for all 186 events, and **64 source-attributed map point candidates**. Older `stats.places` and `stats.events` in the master are stale counters, not source-array lengths.

**Never change the locked source files, Scripture translation text, SOTW author commentary, CGBC, or existing Search v1 to run this script.** Output is an independently replaceable search projection.

## Search/UI outputs
The following files are placed in a new `data/search/people-time-place/v1/` directory when the publish option is selected.

| File | UI role |
|---|---|
| `index/search.json` | People and places by name/aliases; eligible events by title; typed `target` object for app navigation |
| `index/by-scripture.json` | Canonical SOTW chapter/verse scope ID -> associated entity IDs; only explicit parseable source citations |
| `links/typed-links.json` | Directly sourced family, person-place, event-person and event-place links, with evidence/precision fields |
| `entities/people.json` | Person IDs, names, citations, place contexts and qualified optional chronology |
| `entities/places.json` | Place IDs, citations, precision and attributed candidate map points |
| `entities/events.json` | All event records, including those **not public search eligible**, with display eligibility flags |
| `qa/report.json` | Counts and raw unparsed Scripture expressions |
| `manifest.json` | Locked source hashes, full file hashes, rights and app integration contract |

### Safety and evidence
- **181 events** explicitly marked `CONTEXTUAL_SOURCE_REVIEW_REQUIRED` are **not added to public search results, related-entity links, or Scripture reverse-link recommendations** until reviewed. Their bounded detail records remain available for owner review. Nehemiah's wall-rebuilding event is not in that withheld group.
- **71 relationships** marked `PENDING_CONTEXT_VALIDATION` are excluded from the public family-link graph. The QA report lists their source IDs. The remaining relationship evidence is still labeled by precision, not inferred to be direct paternity.
- Do not treat overlapping lives as acquaintance, all genealogical sequences as direct paternity, Ussher BC dates as absolute dates, historical event dates as composition dates, or the candidate map coordinates as precise event locations.
- A map candidate is an approximate **modern place identification**. OpenBible geographic content is **CC BY 4.0**; retain `docs/biblical-history/people-time-place/LICENSE_AND_ATTRIBUTION.md` and the bundled MIT/ISC notices. No scripture verse text or copyrighted map imagery is generated.
- Do not merge people on name alone; preserve the permanent IDs and source-specific scope. Ambiguous names such as Manasseh remain separate records.
- Search returns **typed targets**, not guessed links to an unimplemented app router. The UI must resolve `target.entityType` and `target.entityId` against its own established navigation routes.

### Reproduction / manual workflow
```bash
python3 scripts/build_people_place_search.py \
  --source-dir data/biblical-history/people-time-place \
  --lock docs/biblical-history/people-time-place/CGBC_PERMANENT_LIBRARY_LOCK_2026-10-25.json \
  --sotw-route-map vendor/sotw-route-map/study-data/v1/route-map.json \
  --output-dir data/search/people-time-place/v1
```
The command **fails if the output path already exists**. Build to an empty staging path and inspect diff before any authorized refresh. The manual GitHub workflow defaults to `stage_artifact`, which uploads the generated projection without committing it. A separate owner-selected `publish_projection` commits only the new generated directory to Bible Foundation. **Neither installs the app UI or modifies CGBC/SOTW reader code**.

The artifact is a source-derived tool for the existing search UI. Its use in a live reader is a separate app integration task.
