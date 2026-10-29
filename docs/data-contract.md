# Data contract v0.1: reference-only verse records

This seed defines one intentionally narrow object type, `scripture_reference_set`, validated with `schemas/scripture-reference.schema.json` and `scripts/validate.py`.

- `schema_version`: literal `0.1.0`.
- `record_type`: literal `scripture_reference_set`.
- `book_code`: uppercase OSIS-style book code, here `JHN`.
- `references[]`: a canonical `id`, integer `chapter`, integer `verse`, and `verse_text_present: false`.

References are *not* Bible quotation content. A later version will separately define verified edition verse objects, source manifests, cross-reference evidence, and indexed views. No source-verified translation text is authorized by this fixture.

Source IDs and content IDs must remain independent of publication URLs. A schema change requiring new semantics is versioned; existing IDs are not silently repurposed.
