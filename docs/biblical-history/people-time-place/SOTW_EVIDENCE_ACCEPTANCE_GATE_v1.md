# SOTW People, Place & Event Evidence Acceptance Gate v1

**Owner rule adopted 2026-11-18.** Use the available evidence sensibly: accept directly supported claims and well-supported probable claims (clearly labeled as probable); where credible evidence conflicts or identity is unclear, preserve the supported alternatives and provenance; when no usable evidence exists either way, exclude the claim from public SOTW discovery and finish the review. Do not discard genuine historical alternatives simply to create a single confident answer.

**Scope:** SOTW-only, claim-level, versioned derived review of the locked CGBC 2026-10-25 people/time/place master and its separately published search projection. This is a review policy and initial decision ledger, **not a change to the frozen master**, not an automatic schema migration, and not authorization to install/deploy the live UI. The data publication is currently `READY_FOR_UI_ADAPTER_NOT_LIVE`.

## Four final dispositions

1. `ACCEPT_DIRECT`: Scripture states the exact event/relationship, or a suitable identified historical source supports the exact scoped claim. Record canonical Scripture or a specific historically attributable source; preserve stable IDs and qualifiers. Accept **only** the supported claim facet, not associated dates, places, precise geometry, unmentioned people, biological assumptions, or author identities.
2. `ACCEPT_PROBABLE_QUALIFIED`: Identified credible evidence favors a conclusion, but does not establish certainty. Record evidence, counterpoints if material, and the explicit word **probable** or **likely** in user-facing display. Do not silently promote to `ACCEPT_DIRECT`; do not make probabilistic numeric confidence out of unsupported source claims.
3. `RETAIN_ALTERNATIVES`: Two or more substantively supported models, identifications, textual forms, chronologies or readings remain unresolved. Preserve **each supported alternative with its own source and qualification**, without forced merging, invented consensus, or suggesting equal support when strengths differ. Public display can present both explicitly or defer the uncertain facet, while displaying independently verified facts.
4. `EXCLUDE_NO_EVIDENCE`: A claim has no adequate identifiable evidence, or only an unverified source label with no support. Exclude it from public search, reverse Scripture links and map/event recommendations. Keep the raw original solely in the locked historical source and a compact audited decision record. Do not create an indefinite research backlog or repeated hunting; reconsider only if substantial new evidence is supplied or the owner directs a new review.

These are **claim-facet statuses**: the same entity may have `ACCEPT_DIRECT` for an event's Scripture occurrence and `RETAIN_ALTERNATIVES` for its proposed BC date. A person can be established in Scripture without every imported family link being established. No blanket promotion of 181 withheld events or 71 genealogy edges.

## Technical and source gate (not a fifth evidence verdict)

- A valid range such as `Exodus 7–12` is **not an evidence conflict**. Validate it against canonical book/chapter bounds and emit chapter scopes `EXO.7` ... `EXO.12` before publishing a Scripture link. Cross-chapter references need proper start/end semantics; book-only references must not be exploded into every verse. An unresolved parser failure stays out of navigable links pending repair, while its original reference remains intact.
- Strings like `OpenBible.info Bible Geocoding Data...` are **source attribution**, not failed Scripture citations. Keep them in rights metadata and do not count them as Bible-parser disputes.
- Every promoted link must carry stable `from`/`to` IDs (as applicable), relation meaning, precise Scripture scopes or named historical evidence, attribution/rights, and claim-level qualification. Protect against conflating Cain's son Enoch with the Enoch of Genesis 5, the two Havilahs, or a people-group name with a known immediate biological child.
- An event's occurrence, dated chronology, participants, map-location candidate and book-composition timing each require **independent evaluation**. Proposed dates and geocodes are never proved by the fact that a biblical passage exists. Public display needs its own appropriate qualification and rights clearance.
- Source rights: original CGBC/owner research is checksum locked; Daniel-Hug, Theonize, Wazzac and KJV Study have inherited source boundaries; OpenBible geography retains CC BY 4.0 attribution and location-uncertainty warnings. Never alter the three master bytes or erase earlier source evidence.

## Initial owner-directed application (not yet applied to the published v1 projection)

- `event-theonize-sumerian-writing`, event-search facet: `EXCLUDE_NO_EVIDENCE`. The source says historical-source identification is required. Do not surface it as a biblical event; original historical record remains archived.
- `family-danielhug-father-cain-enoch`, parent-child link: `ACCEPT_DIRECT` for `GEN.4.17`. Distinguish `person-cain-adam` -> `person-danielhug-enoch` from `person-enoch` in Genesis 5. The text also mentions an unnamed wife; do not invent her personal name.
- `event-theonize-ten-plagues`, event-to-Scripture facet: `ACCEPT_DIRECT` for Exodus chapters 7 through 12. Do **not** assert a 1446 BC absolute event date or a precise geography from the citation alone.
- `event-theonize-the-exodus`, chronology facet: `RETAIN_ALTERNATIVES` for the early, later and Ussher/KJV Study-associated date proposals already qualified in the master, without accepting any as an independently established biblical calendar year.
- `family-danielhug-father-javan-dodanim`, textual-name facet: `RETAIN_ALTERNATIVES` for the imported `Dodanim` label and the current BSB Genesis 10:4 `Rodanites` form. Preserve the textual-form issue, not a forced identity merger.

## Release gate

Use `data/search/people-time-place/review/v1/owner-evidence-decisions.json` as the **initial owner-reviewed decision ledger**. This file is an overlay, not the published source/search contract. Before future consumer integration, validate decisions against the pinned master, verify Scripture text/source/rights and exact target IDs, implement deterministic claim-level filtering and derived links, and regression-check chapter bounds, identity disambiguation, attribution, geographic/date caveats and current reader behavior. A missing/invalid decision never automatically overrides existing v1 safety filters. **No live UI, master or published v1 search output is changed by creating this gate.**
