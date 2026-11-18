#!/usr/bin/env python3
"""Deterministically publish an accepted SOTW search source from pinned evidence.

This does NOT change the CGBC master, the old v1 search projection, or any UI.
Unreviewed pending claims never become accepted merely by having a citation.
"""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from build_people_place_search import read_locked, routes_from_file

MASTER = Path("data/biblical-history/people-time-place")
LOCK = Path("docs/biblical-history/people-time-place/CGBC_PERMANENT_LIBRARY_LOCK_2026-10-25.json")
PROJECTION = Path("data/search/people-time-place/v1")
REVIEW = Path("data/search/people-time-place/review/v1/owner-evidence-decisions.json")
RIGHTS = "docs/biblical-history/people-time-place/LICENSE_AND_ATTRIBUTION.md"
STATUSES = {"ACCEPT_DIRECT", "ACCEPT_PROBABLE_QUALIFIED",
            "RETAIN_ALTERNATIVES", "EXCLUDE_NO_EVIDENCE"}
EXPECTED_COUNTS = (269, 65, 186, 327)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def load_projection(folder, locked):
    manifest = json.loads((folder / "manifest.json").read_bytes())
    require(manifest.get("status") == "READY_FOR_UI_ADAPTER_NOT_LIVE", "Projection is not the approved baseline")
    require(manifest.get("sources") == locked, "Projection source master hashes changed")
    for item in manifest["files"]:
        raw = (folder / item["path"]).read_bytes()
        require(len(raw) == item["bytes"] and sha(raw) == item["sha256"],
                "Projection checksum mismatch: " + item["path"])
    result = {}
    for key in ("people", "places", "events"):
        obj = json.loads((folder / "entities" / (key + ".json")).read_bytes())
        result[key] = obj[key]
    return result, manifest


def validate_scope(scope, routes):
    segments = scope.split(".")
    require(len(segments) in (2, 3), "Invalid canonical Scripture scope: " + scope)
    book = segments[0]
    require(book in routes, "Unknown book: " + scope)
    require(segments[1].isdigit() and 1 <= int(segments[1]) <= routes[book],
            "Invalid chapter: " + scope)
    if len(segments) == 3:
        require(segments[2].isdigit() and 1 <= int(segments[2]) <= 200,
                "Invalid verse index: " + scope)


def validate_decisions(doc, master, routes):
    require(doc.get("schema") == "sotw-people-place-evidence-review/1.0.0",
            "Unknown decision schema")
    require(doc.get("status") == "OWNER_REVIEWED_DECISIONS_NOT_APPLIED_TO_PUBLISHED_PROJECTION",
            "Decision status is not reviewed and staged")
    required_master_sha = json.loads(LOCK.read_text())["files"][0]["sha256"]
    require(doc.get("master", {}).get("sha256") == required_master_sha, "Decision lock mismatch")
    people = {p["id"] for p in master["people"]}
    events = {e["id"]: e for e in master["events"]}
    relations = {r["id"]: r for r in master["relationships"]}
    ids = set()
    allowed = {
        ("event_search", "EXCLUDE_NO_EVIDENCE"),
        ("father_child_relationship", "ACCEPT_DIRECT"),
        ("scripture_event_link", "ACCEPT_DIRECT"),
        ("historical_bc_chronology", "RETAIN_ALTERNATIVES"),
        ("biblical_name_form", "RETAIN_ALTERNATIVES"),
    }
    for d in doc["decisions"]:
        pair = (d["entityId"], d["facet"])
        require(pair not in ids, "Duplicate claim/facet: " + str(pair))
        ids.add(pair)
        require(d["disposition"] in STATUSES, "Unknown disposition")
        require((d["facet"], d["disposition"]) in allowed,
                "Unimplemented claim review rule: " + str(pair))
        require(d["entityId"] in events or d["entityId"] in relations,
                "Unknown reviewed record: " + d["entityId"])
        if d["disposition"] == "RETAIN_ALTERNATIVES":
            require(len(d.get("alternatives", [])) >= 2 and all(
                x.get("label") and x.get("sourceKey") for x in d["alternatives"]),
                "Alternatives require distinct sourced labels")
        if d["disposition"] == "EXCLUDE_NO_EVIDENCE":
            require(d.get("publicAction") == "omit_from_public_search_and_scripture_links",
                    "Exclusion must suppress public search")
        if d["disposition"] == "ACCEPT_DIRECT":
            require(d.get("source") and d.get("scriptureScopes"),
                    "Direct acceptance needs source and canonical scopes")
            for scope in d["scriptureScopes"]:
                validate_scope(scope, routes)
            if d["facet"] == "father_child_relationship":
                r = relations[d["entityId"]]
                require(r["from"] == d.get("from") and r["to"] == d.get("to"),
                        "Relationship endpoint mismatch")
                require(d["from"] in people and d["to"] in people, "Unknown person")
                # The approved direct Genesis 4:17 claim must not become a name merger.
                require(d["entityId"] == "family-danielhug-father-cain-enoch" and
                        d["scriptureScopes"] == ["GEN.4.17"] and
                        r["source"] == "Gen 4:17", "Unvalidated family evidence")
            if d["facet"] == "scripture_event_link":
                e = events[d["entityId"]]
                require(d["entityId"] == "event-theonize-ten-plagues" and
                        e["source"].replace("-", "–") == "Exodus 7–12" and
                        d["scriptureScopes"] == ["EXO." + str(n) for n in range(7, 13)],
                        "Unvalidated event range evidence")
    return doc["decisions"]


def build(master, projection, decisions, routes):
    people_master = {p["id"]: p for p in master["people"]}
    rels_master = {r["id"]: r for r in master["relationships"]}
    events_master = {e["id"]: e for e in master["events"]}
    require((len(people_master), len(master["places"]), len(events_master), len(rels_master))
            == EXPECTED_COUNTS, "Master cardinality changed; stop")
    review = {(d["entityId"], d["facet"]): d for d in decisions}
    excluded_ids = {d["entityId"] for d in decisions
                    if d["disposition"] == "EXCLUDE_NO_EVIDENCE"}
    accepted_relations = []
    for rel in master["relationships"]:
        direct = review.get((rel["id"], "father_child_relationship"))
        if rel["id"] in excluded_ids:
            continue
        if rel.get("displayEligibility") == "PENDING_CONTEXT_VALIDATION" and not direct:
            continue
        if direct:
            evidence = direct["source"]
            scopes = list(direct["scriptureScopes"])
            gate = "ACCEPT_DIRECT"
            qualifier = direct.get("caveat")
        else:
            evidence = rel.get("source")
            require(evidence, "Previously accepted family relation lost source")
            scopes = []  # No new inferred verse link without independent range verification.
            gate = "PREVIOUSLY_APPROVED_SOURCE_REPORTED"
            qualifier = rel.get("relationshipPrecision") or rel.get("precision")
        accepted_relations.append({
            "id": rel["id"], "from": rel["from"], "to": rel["to"],
            "relationship": rel["relationship"], "evidence": evidence,
            "scriptureScopes": scopes, "gate": gate, "qualification": qualifier,
            "sourceDataset": rel.get("sourceDataset", "cgbc_curated_library"),
        })
    person_evidence = defaultdict(list)
    for edge in accepted_relations:
        if edge["gate"] == "ACCEPT_DIRECT":
            for endpoint in (edge["from"], edge["to"]):
                person_evidence[endpoint].append({
                    "reference": edge["evidence"], "scriptureScopes": edge["scriptureScopes"],
                    "relationshipId": edge["id"],
                })
    accepted_people = []
    for p in projection["people"]:
        original = people_master[p["id"]]
        prior = p.get("sourceReferences") or []
        joined = person_evidence.get(p["id"], [])
        # Import candidates lack verified evidence in projected details.
        # Only owner-accepted direct relationships can lift a candidate.
        if not prior and not joined:
            continue
        scopes = sorted(set(p.get("scriptureScopes", [])) |
                        {s for evidence in joined for s in evidence["scriptureScopes"]})
        for scope in scopes:
            validate_scope(scope, routes)
        accepted_people.append({
            "id": p["id"], "name": p["name"], "aliases": p.get("aliases", []),
            "sourceReferences": prior, "acceptedRelationshipEvidence": joined,
            "scriptureScopes": scopes,
            "gate": "PREVIOUSLY_APPROVED_SOURCE_REPORTED" if prior else "ACCEPT_DIRECT_LINKED",
            "chronology": p.get("chronology"), "dateDisplay": p.get("dateDisplay"),
            "dateQualification": "Date overlays are conditional models, not biblical calendar facts",
            "identityWarning": "Keep distinct stable IDs; same name does not prove identity",
            "sourceIdentifiers": original.get("sourceIdentifiers", []),
        })
    accepted_places = []
    for p in projection["places"]:
        # All 65 were already published; accepted as source-qualified place
        # identification candidates, NEVER as proved Bible-event coordinates.
        if p["id"] in excluded_ids:
            continue
        for scope in p.get("scriptureScopes", []):
            validate_scope(scope, routes)
        accepted_places.append({
            "id": p["id"], "name": p["name"],
            "scriptureScopes": p.get("scriptureScopes", []),
            "sourceReference": p.get("sourceReference"),
            "precision": p.get("precision"), "mapRepresentation": p.get("mapRepresentation"),
            "gate": "PREVIOUSLY_PUBLISHED_SOURCE_QUALIFIED",
            "mapCandidate": p.get("mapCandidate"),
            "mapWarning": "Modern identification candidate only, never an event GPS location",
        })
    accepted_events = []
    for e in projection["events"]:
        if e["id"] in excluded_ids:
            continue
        review_event = review.get((e["id"], "scripture_event_link"))
        if not e["searchEligible"] and not review_event:
            continue
        scopes = review_event["scriptureScopes"] if review_event else e.get("scriptureScopes", [])
        if not scopes and e["id"] == "event-cgbc-matthew20-vineyard-parable-setting":
            # The v1 source parser missed a real cross-chapter source range.
            # Chapter scopes are safe for navigation but do NOT assert every verse.
            require("Matthew 19:27–20:19" in e["sourceReferences"],
                    "Vineyard parable source passage changed")
            scopes = ["MAT.19", "MAT.20"]
        for scope in scopes:
            validate_scope(scope, routes)
        require(scopes, "Accepted event must have Scripture scopes: " + e["id"])
        accepted_events.append({
            "id": e["id"], "name": e["name"], "scriptureScopes": scopes,
            "sourceReferences": e["sourceReferences"], "participants": e["participants"],
            "places": e["places"],
            "gate": "ACCEPT_DIRECT_SCRIPTURE_LINK" if review_event else "PREVIOUSLY_PUBLIC",
            "scriptureQualification": review_event.get("caveat") if review_event else None,
            "dateStatus": "NOT_ESTABLISHED_BY_SCRIPTURE_LINK",
            "locationStatus": "CONTEXTUAL_ONLY_NO_EVENT_PIN",
            "sourceEligibility": e["displayEligibility"],
        })
    alternatives = [{
        "entityId": d["entityId"], "facet": d["facet"],
        "disposition": "RETAIN_ALTERNATIVES", "alternatives": d["alternatives"],
        "source": d["source"], "caveat": d.get("caveat"),
        "publicAction": d.get("publicAction"),
    } for d in decisions if d["disposition"] == "RETAIN_ALTERNATIVES"]
    person_ids = {p["id"] for p in accepted_people}
    for edge in accepted_relations:
        require(edge["from"] in person_ids and edge["to"] in person_ids,
                "Accepted relation endpoint is not a sourced person: " + edge["id"])
    reverse = defaultdict(set)
    for key, collection in (("person", accepted_people), ("place", accepted_places),
                            ("event", accepted_events)):
        for item in collection:
            for s in item["scriptureScopes"]:
                reverse[s].add(item["id"])
    results = {
        "schema": "sotw-accepted-people-place-source/1.0.0",
        "status": "PUBLISHED_ACCEPTED_SOURCE_NOT_UI_CONNECTED",
        "sourceRights": RIGHTS,
        "gate": "docs/biblical-history/people-time-place/SOTW_EVIDENCE_ACCEPTANCE_GATE_v1.md",
        "people": accepted_people, "places": accepted_places,
        "events": accepted_events, "relationships": accepted_relations,
        "alternatives": alternatives,
        "reverseScriptureScopes": {k: sorted(v) for k, v in sorted(reverse.items())},
    }
    result_counts = {k: len(results[k]) for k in
                     ("people", "places", "events", "relationships", "alternatives")}
    audits = {
        "schema": "sotw-accepted-source-audit/1.0.0",
        "status": "SOURCE_PUBLICATION_ONLY",
        "counts": {**result_counts,
                   "withheldPeople": len(people_master) - result_counts["people"],
                   "withheldEvents": len(events_master) - result_counts["events"],
                   "withheldRelationships": len(rels_master) - result_counts["relationships"]},
        "ownerDecisionCounts": {kind: sum(d["disposition"] == kind for d in decisions)
                                for kind in sorted(STATUSES)},
        "excludedSourceClaimIds": sorted(excluded_ids),
        "note": "Withheld claims stay in the original locked master, not the accepted public source. Unreviewed items are not silently promoted.",
    }
    return results, audits


def publish(source_dir, lock_path, projection_dir, review_path, route_path, out_dir):
    require(not out_dir.exists(), "Output already exists; stage to a new empty directory")
    originals, hashes = read_locked(source_dir, lock_path)
    master = originals["people"]
    require((len(master["people"]), len(master["places"]),
             len(master["events"]), len(master["relationships"])) == EXPECTED_COUNTS,
            "Pinned master count mismatch")
    proj, proj_manifest = load_projection(projection_dir, hashes)
    routes = routes_from_file(route_path)
    review = json.loads(review_path.read_bytes())
    expected_master_hash = next(x["sha256"] for x in
                                json.loads(lock_path.read_text())["files"]
                                if x["filename"] == "CGBC_PEOPLE_TIME_PLACE_LIBRARY.json")
    require(review.get("master", {}).get("sha256") == expected_master_hash,
            "Decision master SHA mismatch")
    decisions = validate_decisions(review, master, routes)
    result, audit = build(master, proj, decisions, routes)
    contents = {"accepted-source.json": encoded(result), "audit.json": encoded(audit)}
    manifest = {
        "schema": "sotw-accepted-source-manifest/1.0.0",
        "status": "PUBLISHED_ACCEPTED_SOURCE_NOT_UI_CONNECTED",
        "pinnedSources": hashes,
        "baseProjection": {"manifestSha256": sha((projection_dir / "manifest.json").read_bytes()),
                           "libraryVersion": proj_manifest["libraryVersion"]},
        "reviewSha256": sha(review_path.read_bytes()),
        "sourceRights": RIGHTS,
        "files": [{"path": name, "sha256": sha(raw), "bytes": len(raw)}
                  for name, raw in sorted(contents.items())],
        "counts": audit["counts"],
        "publicationScope": "Derived SOTW accepted source only; CGBC master, v1 projection and UI not edited",
    }
    contents["manifest.json"] = encoded(manifest)
    out_dir.mkdir(parents=True)
    for name, raw in contents.items():
        (out_dir / name).write_bytes(raw)
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, default=MASTER)
    ap.add_argument("--lock", type=Path, default=LOCK)
    ap.add_argument("--projection-dir", type=Path, default=PROJECTION)
    ap.add_argument("--review", type=Path, default=REVIEW)
    ap.add_argument("--route-map", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    report = publish(args.source_dir, args.lock, args.projection_dir,
                     args.review, args.route_map, args.output_dir)
    print(json.dumps({"status": report["status"], "counts": report["counts"]},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
