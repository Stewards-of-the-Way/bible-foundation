# Bible Foundation

A portable, source-conscious Scripture and biblical research foundation maintained by **Stewards of the Way**.

**Status:** Architecture seed / reference-only demonstration. No Bible translation text, lexicon, commentary, or historical database has been imported or independently verified in this package.

## Purpose

Build reusable biblical reference data for Christ-centered study experiences and independent ministry tools. Preserve original editions, documented rights, precise references, and stable identifiers. Applications consume the foundation; they do not define it.

## Start here

- `docs/architecture.md`: boundaries, stable IDs, paths and data lifecycle
- `docs/sources-and-rights.md`: source intake, rights, provenance and publication rules
- `docs/data-contract.md`: the first working record contract
- `docs/roadmap.md`: bounded phases and objective acceptance checks
- `schemas/scripture-reference.schema.json`: JSON Schema for reference-only entries
- `examples/john-1-1-to-5.references.json`: five reference-only records, **no copyrighted verse text**
- `scripts/validate.py`: zero-dependency fixture and uniqueness validation

Run `python3 scripts/validate.py` from the repository root.

## Working boundaries

The foundation is independent from CGBC's production Sermon Player, the canonical sermon SPP/Info Map 3.0 system, individual pastors' rights, and churches' independently owned collections. It may establish *links* to those systems later, without merging them. No production integration or deployments are authorized by this package.

## Rights

This repository does not assert a blanket license over third-party biblical texts and datasets. See `docs/sources-and-rights.md`. Do not place unpublished, private or rights-restricted source material in public GitHub repositories.

## Stewardship

Stable, documented, independently reproducible data matters more than any single hosting provider, developer or interface. The organization can be stewarded by successors while retaining verified source identity and audit history.
