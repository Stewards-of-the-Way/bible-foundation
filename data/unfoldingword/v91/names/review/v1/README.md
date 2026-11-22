# unfoldingWord v91 name articles: obvious-error screen v1

**Scope:** 355 original `en_tw/bible/names` articles. Light-touch screening commissioned 2026-11-21. **Not** an exhaustive proof of historical claims, acceptance into CGBC's locked historical master, doctrinal endorsement, or permission to re-enable the retired People/Places directory.

## Results

- 332 entries: `NO_OBVIOUS_ERROR_FOUND_IN_LIMITED_SCREEN`. A screen result, not a blanket historical fact certification.
- 23 entries: `EXCLUDE_OBVIOUS_ERROR`. Each has a specific reason and identifying Scripture or historical evidence in the ledger.
- Original `names/entries/*.json`, article wording, names index, and source ZIP remain untouched. Bible Q&A (12,139 records) is not part of this screening.

## Reader instructions

1. Load `reader-eligibility.json` and require `schema=sotw-unfoldingword-name-visibility/1.0.0` and the exact v91 source/index identity.
2. Show a names article **only** if its full `utw:v91:names:...` ID appears in `eligibleIds` and does not appear in `excludedIds`. Do not fall back to a name-slug guess or article text search that bypasses this condition.
3. If the overlay is missing/invalid/mismatched, fail closed: do not show any unreviewed name article. Excluded entries must not appear in search suggestions, linked profiles, citation cards, or passage-related recommendations. Do not silently use an excluded record to populate CGBC historical entities.
4. For an allowed article, retain unfoldingWord attribution, original wording, and original Scripture citations. Use existing SOTW translation-neutral verse targets and the active Reader edition on navigation. Respect independent source rights and presentation/branding requirements.
5. Keep uncertainty and plausible alternate ancient identifications; a missing definitive historical proof was *not* a reason for exclusion in this screen.

`screening-ledger.json` contains the complete 355-row decision record and individual explanations. `reader-eligibility.json` contains the positive list and the blocked IDs for UI consumers.

**Publication does not activate a UI.** The SOTW Reader previously retired its old public People/Places directory. The integration thread must deliberately add filtering when it implements a useful new presentation, independently of the Q&A feature.
