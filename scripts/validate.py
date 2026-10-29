#!/usr/bin/env python3
"""Zero-dependency validation for the v0.1 reference-only fixture."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fixture = json.loads((ROOT / 'examples/john-1-1-to-5.references.json').read_text(encoding='utf-8'))
schema = json.loads((ROOT / 'schemas/scripture-reference.schema.json').read_text(encoding='utf-8'))
assert schema['properties']['record_type']['const'] == 'scripture_reference_set'
assert set(fixture) == {'schema_version', 'record_type', 'book_code', 'references'}
assert fixture['schema_version'] == '0.1.0'
assert fixture['record_type'] == 'scripture_reference_set'
assert re.fullmatch(r'[A-Z0-9]{3,8}', fixture['book_code'])
seen = set()
for ref in fixture['references']:
    assert set(ref) == {'id', 'chapter', 'verse', 'verse_text_present'}
    assert type(ref['chapter']) is int and ref['chapter'] > 0
    assert type(ref['verse']) is int and ref['verse'] > 0
    assert ref['verse_text_present'] is False
    assert ref['id'] == f"{fixture['book_code']}.{ref['chapter']}.{ref['verse']}"
    assert re.fullmatch(r'[A-Z0-9]{3,8}\.[1-9][0-9]*\.[1-9][0-9]*', ref['id'])
    assert ref['id'] not in seen, f"Duplicate reference: {ref['id']}"
    seen.add(ref['id'])
assert len(seen) == 5
print(f'PASS: {len(seen)} unique reference-only Scripture IDs; no verse text.')
