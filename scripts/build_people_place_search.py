#!/usr/bin/env python3
"""Read-only CGBC people/place/event master -> SOTW search and UI-link projections.

Never modifies the three checksum-locked source files. This is a search
projection, NOT a historical master revision or a live UI installation.
"""
import argparse
import collections
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

BASE = Path("data/biblical-history/people-time-place")
FILES = {
    "people": "CGBC_PEOPLE_TIME_PLACE_LIBRARY.json",
    "events": "CGBC_HISTORICAL_EVENT_TIME_PLACE_LINKS.json",
    "maps": "CGBC_SOURCE_ATTRIBUTED_MAP_FEATURES.geojson",
}
LOCK = Path("docs/biblical-history/people-time-place/CGBC_PERMANENT_LIBRARY_LOCK_2026-10-25.json")
ATTRIBUTION = "docs/biblical-history/people-time-place/LICENSE_AND_ATTRIBUTION.md"
# The SOTW route map governs which chapter IDs are recognized.
BOOKS = """Genesis=GEN|Exodus=EXO|Leviticus=LEV|Numbers=NUM|Deuteronomy=DEU|
Joshua=JOS|Judges=JDG|Ruth=RUT|1 Samuel=1SA|2 Samuel=2SA|1 Kings=1KI|
2 Kings=2KI|1 Chronicles=1CH|2 Chronicles=2CH|Ezra=EZR|Nehemiah=NEH|
Esther=EST|Job=JOB|Psalms=PSA|Proverbs=PRO|Ecclesiastes=ECC|
Song of Solomon=SNG|Isaiah=ISA|Jeremiah=JER|Lamentations=LAM|
Ezekiel=EZK|Daniel=DAN|Hosea=HOS|Joel=JOL|Amos=AMO|Obadiah=OBA|
Jonah=JON|Micah=MIC|Nahum=NAM|Habakkuk=HAB|Zephaniah=ZEP|
Haggai=HAG|Zechariah=ZEC|Malachi=MAL|Matthew=MAT|Mark=MRK|Luke=LUK|
John=JHN|Acts=ACT|Romans=ROM|1 Corinthians=1CO|2 Corinthians=2CO|
Galatians=GAL|Ephesians=EPH|Philippians=PHP|Colossians=COL|
1 Thessalonians=1TH|2 Thessalonians=2TH|1 Timothy=1TI|2 Timothy=2TI|
Titus=TIT|Philemon=PHM|Hebrews=HEB|James=JAS|1 Peter=1PE|
2 Peter=2PE|1 John=1JN|2 John=2JN|3 John=3JN|Jude=JUD|Revelation=REV"""
BOOK_CODES = dict(part.strip().split("=") for part in BOOKS.replace("\n", "").split("|") if part.strip())
BOOK_CODES.update({"Psalm": "PSA", "Song of Songs": "SNG", "Canticles": "SNG"})
BOOK_RE = re.compile(r"(?<![\w])(?P<book>" +
                     "|".join(re.escape(s) for s in sorted(BOOK_CODES, key=len, reverse=True)) +
                     r")\s+(?P<versepart>\d{1,3}(?:\s*[-–]\s*\d{1,3})?(?::\d{1,3}(?:\s*[-–]\s*\d{1,3})?)?)", re.I)
SHORT_RE = re.compile(r"^\s*(?P<versepart>\d{1,3}(?:\s*[-–]\s*\d{1,3})?(?::\d{1,3}(?:\s*[-–]\s*\d{1,3})?)?)\s*$")
ALIAS_BOOKS = {k.casefold(): v for k, v in BOOK_CODES.items()}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_bytes(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def emit(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(data)
    path.write_bytes(payload)
    return {"path": str(path.name), "sha256": digest(payload), "bytes": len(payload)}


def read_locked(folder, lock):
    manifest = json.loads(lock.read_text(encoding="utf-8"))
    required = {x["filename"]: x for x in manifest["files"]}
    if set(required) != set(FILES.values()):
        raise ValueError("Lock inventory does not match the three canonical inputs")
    data = {}
    pins = {}
    for kind, filename in FILES.items():
        path = folder / filename
        raw = path.read_bytes()
        expected = required[filename]
        if len(raw) != expected["bytes"] or digest(raw) != expected["sha256"]:
            raise ValueError(f"Locked master checksum or byte count mismatch: {filename}")
        data[kind] = json.loads(raw)
        pins[filename] = {"sha256": digest(raw), "bytes": len(raw)}
    return data, pins


def routes_from_file(path):
    source = json.loads(path.read_text(encoding="utf-8"))
    routes = {b["code"]: b["chapter_count"] for b in source["books"]}
    if len(routes) != 66 or set(routes) != set(BOOK_CODES.values()):
        raise ValueError("SOTW canonical route map is incomplete or incompatible")
    return routes


def parse_scopes(raw, routes):
    """Conservative exact book + chapter/verse parser. No textual interpretation."""
    scopes = set()
    if not isinstance(raw, str) or not raw.strip():
        return []
    current = None
    for section in re.split(r"[;]", raw.replace("—", "–")):
        matches = list(BOOK_RE.finditer(section))
        if matches:
            for match in matches:
                current = ALIAS_BOOKS[match.group("book").casefold()]
                scopes.update(parse_versepart(current, match.group("versepart"), routes))
        elif current:
            short = SHORT_RE.fullmatch(section)
            if short:
                scopes.update(parse_versepart(current, short.group("versepart"), routes))
    return sorted(scopes)


def parse_versepart(book, part, routes):
    # A chapter-only reference returns a chapter scope, not fabricated verse IDs.
    if book not in routes:
        return []
    pattern = r"^(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?(?::(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?)?$"
    match = re.fullmatch(pattern, part.strip())
    if not match:
        return []
    chapter, endchapter, first, last = match.groups()
    chapter = int(chapter)
    if chapter < 1 or chapter > routes[book]:
        return []
    if endchapter:
        endchapter = int(endchapter)
        if first or endchapter < chapter or endchapter > routes[book] or endchapter - chapter > 4:
            return []
        return [f"{book}.{n}" for n in range(chapter, endchapter + 1)]
    if first is None:
        return [f"{book}.{chapter}"]
    first, last = int(first), int(last or first)
    if first < 1 or last < first or last > 200 or last - first > 99:
        return []
    return [f"{book}.{chapter}.{n}" for n in range(first, last + 1)]


def unique(records, field, category):
    ids = [r.get(field) for r in records]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError(f"{category} has duplicate or missing IDs")
    return {r[field]: r for r in records}


def search_record(kind, record, aliases=()):
    title = record.get("name") or record.get("title")
    if not title:
        raise ValueError(f"Missing display title: {kind} {record.get('id')}")
    # No invented HTTP routes. Client chooses the navigation adapter.
    return {
        "type": kind, "id": record["id"], "title": title,
        "aliases": sorted({x for x in aliases if isinstance(x, str) and x.strip()}),
        "searchText": " ".join([title, *[x for x in aliases if isinstance(x, str)]]).casefold(),
        "target": {"kind": "entity", "entityType": kind, "entityId": record["id"]},
    }


def build(folder, lock_path, route_path, out_dir):
    if out_dir.exists():
        raise ValueError("Output path exists; select a new empty staging directory")
    data, fingerprints = read_locked(folder, lock_path)
    routes = routes_from_file(route_path)
    master, joined, geo = data["people"], data["events"], data["maps"]
    people = unique(master["people"], "id", "people")
    places = unique(master["places"], "id", "places")
    events = unique(master["events"], "id", "events")
    rels = unique(master["relationships"], "id", "family relationships")
    joins = unique(joined["records"], "eventId", "event evidence")
    features = unique(geo["features"], "id", "geography features")
    if (len(people), len(places), len(events), len(rels), len(features), len(joins)) != (269,65,186,327,64,186):
        raise ValueError("Unexpected locked-master counts; do not regenerate against a changed source")
    if set(events) != set(joins) or not set(features).issubset(places):
        raise ValueError("Event joins or map features do not match canonical IDs")
    for rel in rels.values():
        if rel["from"] not in people or rel["to"] not in people:
            raise ValueError(f"Orphaned family relation {rel['id']}")
    for e in events.values():
        if any(p not in people for p in e.get("participants", [])):
            raise ValueError(f"Orphaned event participant {e['id']}")
        if any(p not in places for p in e.get("locationRefs", [])):
            raise ValueError(f"Orphaned event location {e['id']}")
    for p in people.values():
        for context in p.get("geographicContexts", []):
            if context.get("placeId") and context["placeId"] not in places:
                raise ValueError(f"Orphaned person/place link {p['id']}")

    links = []
    seen_links = set()
    def link(src, dst, link_type, evidence=None, precision=None):
        if not src or not dst:
            return
        key = (src, dst, link_type, str(evidence or ""))
        if key not in seen_links:
            seen_links.add(key)
            links.append({"from": src, "to": dst, "type": link_type,
                          "evidence": evidence, "precision": precision})

    search = []
    by_scope = collections.defaultdict(set)
    detail_people, detail_places, detail_events = [], [], []
    unparsed = []
    event_hidden = 0

    def attach_scopes(entity_id, raw_evidence):
        if not isinstance(raw_evidence, str) or not raw_evidence.strip():
            return []
        resolved = parse_scopes(raw_evidence, routes)
        if not resolved:
            unparsed.append({"entityId": entity_id, "raw": raw_evidence})
        for scope in resolved:
            by_scope[scope].add(entity_id)
        return resolved

    for p in people.values():
        aliases = p.get("aliases") if isinstance(p.get("aliases"), list) else []
        search.append(search_record("person", p, aliases))
        scope_set = set()
        for source in p.get("sources", []):
            scope_set.update(attach_scopes(p["id"], source))
        locs = []
        for context in p.get("geographicContexts", []):
            place_id = context.get("placeId")
            if place_id in places:
                locs.append({"placeId": place_id, "role": context.get("role"),
                             "source": context.get("source"),
                             "timePrecision": context.get("timePrecision")})
                link(p["id"], place_id, "PERSON_PLACE_CONTEXT", context.get("source"),
                     context.get("timePrecision"))
        detail_people.append({"id": p["id"], "name": p["name"], "aliases": aliases,
                              "scriptureScopes": sorted(scope_set),
                              "sourceReferences": p.get("sources", []),
                              "places": locs,
                              "chronology": p.get("chronology"),
                              "dateDisplay": p.get("calendarDateDisplay"),
                              "chronologyWarning": "Date models are conditional, not biblical absolute chronology."})
    for rel in rels.values():
        link(rel["from"], rel["to"], "REPORTED_FAMILY_RELATIONSHIP",
             rel.get("source"), rel.get("relationshipPrecision") or rel.get("precision"))

    for pl in places.values():
        search.append(search_record("place", pl))
        f = features.get(pl["id"])
        candidate = None
        if f and f.get("geometry", {}).get("type") == "Point":
            coords = f["geometry"].get("coordinates", [])
            if len(coords) == 2 and all(type(v) in (int,float) for v in coords):
                lon, lat = coords
                if -180 <= lon <= 180 and -90 <= lat <= 90:
                    props = f.get("properties", {})
                    candidate = {"longitude": lon, "latitude": lat, "isCandidate": True,
                                 "renderPolicy": props.get("renderPolicy"),
                                 "pointSemantics": props.get("pointSemantics"),
                                 "source": props.get("source"),
                                 "modernIdentification": props.get("modernIdentification"),
                                 "identificationScoreAsSupplied": props.get("identificationScore"),
                                 "warning": "Representative modern identification, NOT a verified biblical event GPS point."}
        scope_set = attach_scopes(pl["id"], pl.get("source"))
        detail_places.append({"id": pl["id"], "name": pl["name"], "scriptureScopes": scope_set,
                              "sourceReference": pl.get("source"), "precision": pl.get("precision"),
                              "mapRepresentation": pl.get("mapRepresentation"),
                              "mapCandidate": candidate})

    for e in events.values():
        joined_evidence = joins[e["id"]]
        eligible = e.get("displayEligibility") != "CONTEXTUAL_SOURCE_REVIEW_REQUIRED"
        if eligible:
            search.append(search_record("event", e))
        else:
            event_hidden += 1
        raw_sources = list(dict.fromkeys(filter(None, [e.get("source"), joined_evidence.get("sourcePassage")])))
        scopes = set()
        for source in raw_sources:
            # Never emit an event as a public Scripture hit if it requires
            # contextual review, even when source text contains a citation.
            parsed = parse_scopes(source, routes)
            if not parsed and isinstance(source, str) and source != "Historical-source identification required before publication":
                unparsed.append({"entityId": e["id"], "raw": source})
            if eligible:
                scopes.update(parsed)
                for s in parsed:
                    by_scope[s].add(e["id"])
        person_ids = sorted(set(e.get("participants", [])))
        place_ids = sorted(set(e.get("locationRefs", [])) | set(joined_evidence.get("place", {}).get("placeIds", [])))
        for person_id in person_ids:
            link(e["id"], person_id, "EVENT_PARTICIPANT_EXPLICIT", e.get("source"))
        for place_id in place_ids:
            if place_id not in places:
                raise ValueError(f"Event source join has unknown place {place_id}")
            link(e["id"], place_id, "EVENT_PLACE_ASSOCIATION_NOT_GPS", joined_evidence.get("sourcePassage"),
                 joined_evidence.get("place", {}).get("displayPolicy"))
        detail_events.append({"id": e["id"], "name": e["name"],
                              "searchEligible": eligible,
                              "displayEligibility": e.get("displayEligibility", "UNSPECIFIED"),
                              "scriptureScopes": sorted(scopes),
                              "sourceReferences": raw_sources, "participants": person_ids,
                              "places": place_ids,
                              "timeQualification": joined_evidence.get("time", {}).get("displayPolicy"),
                              "placeQualification": joined_evidence.get("place", {}).get("displayPolicy"),
                              "warning": "Chronology, site and event associations can be model-dependent; confirm before prominent UI display."})

    search.sort(key=lambda x: (x["type"], x["title"].casefold(), x["id"]))
    links.sort(key=lambda x: (x["from"], x["to"], x["type"], str(x["evidence"])))
    report = {
        "schema": "sotw-people-time-place-qa/1",
        "counts": {"people": len(people), "places": len(places), "events": len(events),
                   "familyRelationships": len(rels), "mapCandidates": len(features),
                   "eventEvidence": len(joins), "publicSearchEntries": len(search),
                   "eventsContextReviewOnly": event_hidden, "typedLinks": len(links),
                   "indexedScriptureScopes": len(by_scope), "unparsedSourceExpressions": len(unparsed)},
        "unparsedSourceExpressions": unparsed,
        "policy": "Only direct source-backed identities/links indexed; events requiring contextual review withheld from public search; unparsed references retained for audit.",
        "passed": True,
    }
    target = out_dir
    target.mkdir(parents=True, exist_ok=False)
    inventory = []
    payloads = {
        "index/search.json": {"schema": "sotw-entity-search-v1", "records": search},
        "index/by-scripture.json": {"schema": "sotw-entity-scripture-links-v1",
                                     "scopes": {s: sorted(ids) for s, ids in sorted(by_scope.items())}},
        "links/typed-links.json": {"schema": "sotw-entity-typed-links-v1", "edges": links},
        "entities/people.json": {"schema": "sotw-entity-details-v1", "people": detail_people},
        "entities/places.json": {"schema": "sotw-entity-details-v1", "places": detail_places},
        "entities/events.json": {"schema": "sotw-entity-details-v1", "events": detail_events},
        "qa/report.json": report,
    }
    for relative, payload in sorted(payloads.items()):
        p = target / relative
        item = emit(p, payload)
        item["path"] = relative
        inventory.append(item)
    emit(target / "manifest.json", {
        "schema": "sotw-entity-search-manifest-v1",
        "status": "READY_FOR_UI_ADAPTER_NOT_LIVE",
        "sources": fingerprints, "libraryVersion": master["libraryVersion"],
        "rightsReference": ATTRIBUTION,
        "uiContract": {"search": "index/search.json", "scriptureReverse": "index/by-scripture.json",
                       "details": "entities/{people,places,events}.json",
                       "typedLinks": "links/typed-links.json",
                       "navigation": "Resolve target.entityType + entityId in the SOTW app; URLs deliberately unspecified",
                       "eventSafety": "Honor searchEligible and displayEligibility; do not show review-only events as verified",
                       "mapSafety": "Point candidate is a modern reference, not an event pin"},
        "files": inventory
    })
    return report


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--source-dir", type=Path, default=BASE)
    a.add_argument("--lock", type=Path, default=LOCK)
    a.add_argument("--sotw-route-map", type=Path, required=True)
    a.add_argument("--output-dir", type=Path, required=True)
    args = a.parse_args()
    try:
        result = build(args.source_dir, args.lock, args.sotw_route_map, args.output_dir)
        print(json.dumps(result["counts"], indent=2))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print(f"LOCKED PEOPLE/PLACE SEARCH BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
