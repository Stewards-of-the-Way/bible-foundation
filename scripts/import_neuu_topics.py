#!/usr/bin/env python3
"""Import the NEUU Nave/Torrey parsed topic index as separate SOTW topic data.

No Bible verses, sermon commentary, modern glosses, or new topical inferences
are generated. Scripture references are mapped to canonical SOTW IDs only.
"""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

SOURCE_REPO = "https://github.com/neuu-org/bible-topics-dataset"
SOURCE_LAYER = "data/01_parsed"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
ATTRIBUTION = ("Bible Topics Dataset by NEUU (https://github.com/neuu-org), "
               "used under CC BY 4.0; based on Nave (1896), Torrey (1897), "
               "with CCEL digitisation credited.")
# Explicit canonical name -> code mapping, checked against the actual SOTW route-map.
NAMES = """Genesis:GEN|Exodus:EXO|Leviticus:LEV|Numbers:NUM|Deuteronomy:DEU|
Joshua:JOS|Judges:JDG|Ruth:RUT|1 Samuel:1SA|2 Samuel:2SA|1 Kings:1KI|
2 Kings:2KI|1 Chronicles:1CH|2 Chronicles:2CH|Ezra:EZR|Nehemiah:NEH|
Esther:EST|Job:JOB|Psalms:PSA|Proverbs:PRO|Ecclesiastes:ECC|
Song of Solomon:SNG|Isaiah:ISA|Jeremiah:JER|Lamentations:LAM|
Ezekiel:EZK|Daniel:DAN|Hosea:HOS|Joel:JOL|Amos:AMO|Obadiah:OBA|
Jonah:JON|Micah:MIC|Nahum:NAM|Habakkuk:HAB|Zephaniah:ZEP|
Haggai:HAG|Zechariah:ZEC|Malachi:MAL|Matthew:MAT|Mark:MRK|Luke:LUK|
John:JHN|Acts:ACT|Romans:ROM|1 Corinthians:1CO|2 Corinthians:2CO|
Galatians:GAL|Ephesians:EPH|Philippians:PHP|Colossians:COL|
1 Thessalonians:1TH|2 Thessalonians:2TH|1 Timothy:1TI|2 Timothy:2TI|
Titus:TIT|Philemon:PHM|Hebrews:HEB|James:JAS|1 Peter:1PE|
2 Peter:2PE|1 John:1JN|2 John:2JN|3 John:3JN|Jude:JUD|Revelation:REV"""
BOOK_NAMES = dict(item.strip().split(":") for item in NAMES.replace("\n", "").split("|") if item.strip())
BOOK_NAMES.update({"Psalm": "PSA", "Song of Songs": "SNG", "Canticles": "SNG",
                   "Revelations": "REV", "The Revelation": "REV"})


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = encode(value)
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def load_routes(path, allow_partial):
    data = json.loads(path.read_text(encoding="utf-8"))
    routes = {item["code"]: int(item["chapter_count"]) for item in data["books"]}
    if len(routes) != 66 and not allow_partial:
        raise ValueError(f"SOTW route-map has {len(routes)} books, expected 66")
    if not set(routes).issubset(set(BOOK_NAMES.values())):
        raise ValueError("SOTW route-map contains unknown book codes")
    if len(routes) == 66 and set(routes) != set(BOOK_NAMES.values()):
        raise ValueError("Canonical book IDs disagree with SOTW route-map")
    return routes


def references(refs, routes, topic_id, unresolved):
    result = []
    for ref in refs:
        raw = ref.get("raw", "")
        name = ref.get("book")
        code = BOOK_NAMES.get(name)
        chapter = ref.get("chapter")
        verse_list = ref.get("verses")
        cause = None
        if code not in routes:
            cause = "unknown_book"
        elif type(chapter) is not int or not 1 <= chapter <= routes[code]:
            cause = "invalid_chapter"
        elif not isinstance(verse_list, list) or not verse_list:
            cause = "missing_verse_list"
        elif any(type(v) is not int or not 1 <= v <= 200 for v in verse_list):
            cause = "invalid_verse"
        if cause:
            unresolved.append({"topic_id": topic_id, "raw": raw, "book": name,
                               "chapter": chapter, "reason": cause})
            result.append({"raw": raw, "status": "unresolved", "reason": cause})
        else:
            ids = list(dict.fromkeys(f"{code}.{chapter}.{v}" for v in verse_list))
            result.append({"raw": raw, "status": "mapped", "verse_ids": ids})
    return result


def import_topics(source_dir, route_path, output_dir, source_commit, allow_partial=False,
                  strict_references=False):
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("--source-commit must be a pinned 40-character Git SHA")
    routes = load_routes(route_path, allow_partial)
    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()
    if source_dir == output_dir or source_dir in output_dir.parents or output_dir in source_dir.parents:
        raise ValueError("Source and output directories must be separate")
    files = sorted(p for p in source_dir.glob("[A-Z]/*.json") if p.is_file())
    if not files:
        raise ValueError("No NEUU data/01_parsed letter/topic JSON files found")
    if not allow_partial and len(files) != 5745:
        raise ValueError(f"Found {len(files)} topic files, expected 5745; aborting partial import")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Refusing to overwrite a nonempty output directory; use a fresh staging directory")
    topics_by_letter = collections.defaultdict(list)
    inverted = collections.defaultdict(lambda: collections.defaultdict(set))
    index = []
    unresolved = []
    seen = set()
    total_ref_entries = 0
    for file in files:
        data = json.loads(file.read_text(encoding="utf-8"))
        slug, title = data.get("slug"), data.get("topic")
        if not isinstance(slug, str) or not slug or not isinstance(title, str) or not title:
            raise ValueError(f"Invalid topic identity in {file}")
        key = slug.lower()
        if key in seen:
            raise ValueError(f"Duplicate topic slug {slug}")
        seen.add(key)
        srcs = data.get("sources")
        if not isinstance(srcs, list) or not srcs or not set(srcs).issubset({"NAV", "TOR"}):
            raise ValueError(f"Invalid source provenance in {file}")
        topic_id = "NEUU:TOPIC:" + slug
        original_refs = data.get("biblical_references", [])
        if not isinstance(original_refs, list):
            raise ValueError(f"Invalid references in {file}")
        mapped = references(original_refs, routes, topic_id, unresolved)
        total_ref_entries += len(original_refs)
        attached = set()
        for entry in mapped:
            for verse_id in entry.get("verse_ids", []):
                attached.add(verse_id)
                inverted[verse_id.split(".")[0]][verse_id].add(topic_id)
        payload = {
            "id": topic_id, "title": title, "slug": slug,
            "sources": srcs,
            "see_also": data.get("see_also", []),
            "aspects": data.get("aspects", []),
            "references": mapped,
            "provenance": {
                "source_repository": SOURCE_REPO,
                "source_commit": source_commit,
                "source_path": f"{SOURCE_LAYER}/{file.parent.name}/{file.name}",
                "original_sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                "license": "CC BY 4.0"
            }
        }
        topics_by_letter[file.parent.name].append(payload)
        index.append({"id": topic_id, "title": title, "slug": slug,
                      "sources": srcs, "see_also": data.get("see_also", []),
                      "verse_link_count": len(attached),
                      "shard": f"topics/{file.parent.name}.json"})
    if not allow_partial and total_ref_entries != 65485:
        raise ValueError(f"Found {total_ref_entries} source reference entries, expected 65485")
    if strict_references and unresolved:
        raise ValueError(f"Found {len(unresolved)} unresolved Scripture references")
    files_written = []
    for letter in sorted(topics_by_letter):
        path = output_dir / "topics" / f"{letter}.json"
        sha = write_json(path, {"schema": "sotw-topics-neuu-shard/1.0.0", "topics": topics_by_letter[letter]})
        files_written.append({"path": path.relative_to(output_dir).as_posix(), "sha256": sha})
    for book_code, verses in sorted(inverted.items()):
        path = output_dir / "index/by-scripture" / f"{book_code}.json"
        sha = write_json(path, {"schema": "sotw-topics-scripture-index/1.0.0", "book_code": book_code,
                                "verses": {vid: sorted(ids) for vid, ids in sorted(verses.items())}})
        files_written.append({"path": path.relative_to(output_dir).as_posix(), "sha256": sha})
    index_path = output_dir / "index/topics.json"
    files_written.append({"path": "index/topics.json", "sha256": write_json(index_path, {
        "schema": "sotw-topics-search-index/1.0.0", "topics": sorted(index, key=lambda t: (t["title"], t["id"]))
    })})
    report = {"schema": "sotw-topics-import-report/1.0.0", "source_topic_files": len(files),
              "source_reference_entries": total_ref_entries, "mapped_scripture_verses": sum(len(v) for v in inverted.values()),
              "unresolved_reference_entries": len(unresolved), "unresolved": unresolved,
              "status": "PARTIAL_TEST_ONLY" if allow_partial else "NORMALIZED_SOURCE_NOT_YET_CONNECTED_TO_SEARCH_V1"}
    files_written.append({"path": "import-report.json", "sha256": write_json(output_dir / "import-report.json", report)})
    manifest = {
        "schema": "sotw-topics-neuu-manifest/1.0.0", "version": "v1", "status": report["status"],
        "source": {"name": "NEUU Bible Topics Dataset", "repository": SOURCE_REPO,
                   "pinned_commit": source_commit, "layer": SOURCE_LAYER,
                   "authors": ["Orville J. Nave", "R. A. Torrey"],
                   "license": "CC BY 4.0", "license_url": LICENSE_URL,
                   "notice_url": SOURCE_REPO + "/blob/" + source_commit + "/NOTICE",
                   "attribution": ATTRIBUTION},
        "counts": {"topics": len(files), "reference_entries": total_ref_entries,
                   "unresolved_reference_entries": len(unresolved)},
        "author_commentary": {"authority": "SOTW-Historical-Commentaries/historical-commentary-resources",
                              "path": "api/jacob-lannom/v1/current-commentary.json",
                              "joining_rule": "Explicit approved topic associations via canonical scope keys only; not inferred or copied"},
        "disclaimer": "Source-provided historical topic associations, not SOTW doctrinal judgments; verse texts and sermons not included.",
        "files": sorted(files_written, key=lambda f: f["path"])
    }
    write_json(output_dir / "manifest.json", manifest)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True, help="NEUU data/01_parsed")
    parser.add_argument("--sotw-route-map", type=Path, required=True, help="Actual SOTW study-data/v1/route-map.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--allow-partial", action="store_true", help="Fixture/test only, never production")
    parser.add_argument("--strict-references", action="store_true")
    args = parser.parse_args(argv)
    report = import_topics(args.source_dir, args.sotw_route_map, args.output_dir,
                           args.source_commit, args.allow_partial, args.strict_references)
    print(json.dumps({k: v for k, v in report.items() if k != "unresolved"}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as err:
        print(f"TOPIC IMPORT STOPPED: {err}", file=sys.stderr)
        sys.exit(1)
