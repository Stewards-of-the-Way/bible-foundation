# SOTW Biblical People / Genealogy / Time / Place - manual migration package

Target repository: Stewards-of-the-Way/bible-foundation (default branch, after owner review).
This ZIP contains repository-root paths: upload/merge folders into the repository root, preserving the hierarchy.

## Scope
- Three **unchanged bytes** from the CGBC 2026-10-25 pinned master; exact SHA-256 values are in SHA256SUMS.txt.
- Original rights/attribution documentation, applicable license texts, and source lock/policy.
- No generated master regeneration, schema edits, CGBC deletion, application integration, or GitHub changes.
- The source lock's historical `repositoryPath`, `policyStatus`, and `githubStatus` are **historical metadata**, not destinations/status of this new SOTW copy. Never edit the locked master files or lock manifest merely to reflect relocation.

## Install safely
1. In `Stewards-of-the-Way/bible-foundation` confirm the proposed `data/biblical-history/people-time-place/` and `docs/biblical-history/people-time-place/` paths are empty or reconcile conflicts without overwrite.
2. Upload the ZIP's folders to the **repository root**; do not upload the ZIP itself as data.
3. Verify all file hashes listed in SHA256SUMS.txt. Verify data references, IDs and licenses after publication and ensure public redistribution is permitted for every included item.
4. Only after comparing the installed shared copy and testing downstream SOTW/CGBC consumers, separately update CGBC reference paths. Keep the original CGBC files as fallback until every dependent reader and script is migrated and tested.
5. Any deletion or changing the canonical owner of the locked master requires its own explicit migration approval and rollback plan. Do not delete the original based only on this ZIP.

## Architectural notes
This is a pinned historical **snapshot**, not an automatically growing master. Biblical people, genealogy, time, place and event IDs are shared references; CGBC sermon-specific insights stay in its canonical Info Map and passage registries. Missing history should not trigger master rewriting. Any future correction is a separately reviewed version with stable IDs, evidence, rights, and migration notes.

## Publication caution
The sources have distinct licenses and attribution obligations, including CC BY 4.0 for OpenBible-derived geography and MIT/ISC notices for designated material. The license and rights review must be performed before publication; original source documentation is preserved here. The GitHub repo being public does not make excluded data permissible to distribute.
