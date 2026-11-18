#!/usr/bin/env python3
"""Offline release-gate regression tests; original sources must remain immutable."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publish_accepted_people_place as gate  # noqa: E402

ROUTES = ROOT / "vendor/sotw-route-map/study-data/v1/route-map.json"


class AcceptanceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def test_scope_validation(self):
        routes = {"GEN": 50, "EXO": 40, "MAT": 28}
        for s in ("GEN.4.17", "EXO.7", "EXO.12", "MAT.19", "MAT.20"):
            gate.validate_scope(s, routes)
        for s in ("EXO.99", "MAT.0", "GEN.4.0", "BAD.1", "EXO.7.-2"):
            with self.assertRaises(ValueError):
                gate.validate_scope(s, routes)

    def test_published_corpus_is_source_pinned_and_conservative(self):
        # The pinned route map is checked out by the publication workflow.
        self.assertTrue(ROUTES.exists(), "Pinned canonical SOTW route-map checkout is required")
        before = {name: hashlib.sha256((ROOT / gate.MASTER / name).read_bytes()).hexdigest()
                  for name in ("CGBC_PEOPLE_TIME_PLACE_LIBRARY.json",
                               "CGBC_HISTORICAL_EVENT_TIME_PLACE_LINKS.json",
                               "CGBC_SOURCE_ATTRIBUTED_MAP_FEATURES.geojson")}
        out = self.folder / "stage"
        report = gate.publish(ROOT / gate.MASTER, ROOT / gate.LOCK, ROOT / gate.PROJECTION,
                              ROOT / gate.REVIEW, ROUTES, out)
        counts = report["counts"]
        self.assertEqual((counts["people"], counts["places"], counts["events"],
                          counts["relationships"], counts["alternatives"]),
                         (185, 65, 6, 257, 2))
        published = json.loads((out / "accepted-source.json").read_bytes())
        audit = json.loads((out / "audit.json").read_bytes())
        self.assertEqual(audit["counts"]["withheldEvents"], 180)
        self.assertEqual(audit["counts"]["withheldRelationships"], 70)
        self.assertEqual(audit["counts"]["withheldPeople"], 84)
        self.assertEqual(audit["ownerDecisionCounts"]["EXCLUDE_NO_EVIDENCE"], 1)
        events = {x["id"]: x for x in published["events"]}
        rels = {x["id"]: x for x in published["relationships"]}
        people = {x["id"]: x for x in published["people"]}
        self.assertNotIn("event-theonize-sumerian-writing", events)
        self.assertEqual(events["event-theonize-ten-plagues"]["scriptureScopes"],
                         ["EXO." + str(n) for n in range(7, 13)])
        self.assertEqual(events["event-cgbc-matthew20-vineyard-parable-setting"]
                         ["scriptureScopes"], ["MAT.19", "MAT.20"])
        self.assertEqual(rels["family-danielhug-father-cain-enoch"]["scriptureScopes"],
                         ["GEN.4.17"])
        self.assertIn("person-danielhug-enoch", people)
        self.assertIn("person-enoch", people)
        self.assertNotEqual(people["person-danielhug-enoch"]["id"],
                            people["person-enoch"]["id"])
        self.assertNotIn("person-danielhug-havilah", people)
        self.assertTrue(all(x["dateStatus"] == "NOT_ESTABLISHED_BY_SCRIPTURE_LINK"
                            for x in events.values()))
        self.assertTrue(all(x["mapWarning"].startswith("Modern identification")
                            for x in published["places"]))
        self.assertTrue(all(x["disposition"] == "RETAIN_ALTERNATIVES"
                            for x in published["alternatives"]))
        self.assertIn("event-theonize-sumerian-writing", audit["excludedSourceClaimIds"])
        self.assertEqual(before, {name: hashlib.sha256(
            (ROOT / gate.MASTER / name).read_bytes()).hexdigest() for name in before})
        for file in report["files"]:
            raw = (out / file["path"]).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                             (file["bytes"], file["sha256"]))
        with self.assertRaisesRegex(ValueError, "Output already exists"):
            gate.publish(ROOT / gate.MASTER, ROOT / gate.LOCK, ROOT / gate.PROJECTION,
                         ROOT / gate.REVIEW, ROUTES, out)

    def test_unreviewed_new_claim_cannot_auto_pass(self):
        doc = json.loads((ROOT / gate.REVIEW).read_text())
        doc["decisions"].append({
            "entityId": "family-danielhug-father-aram-gether",
            "facet": "father_child_relationship",
            "disposition": "ACCEPT_DIRECT",
            "source": "Gen 10:23",
            "from": "person-danielhug-aram",
            "to": "person-danielhug-gether",
            "scriptureScopes": ["GEN.10.23"]
        })
        candidate = self.folder / "tampered-decisions.json"
        candidate.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, "Unvalidated family evidence"):
            gate.publish(ROOT / gate.MASTER, ROOT / gate.LOCK, ROOT / gate.PROJECTION,
                         candidate, ROUTES, self.folder / "output")
        self.assertFalse((self.folder / "output").exists())

    def test_changed_lock_refuses_publication(self):
        doc = json.loads((ROOT / gate.REVIEW).read_text())
        doc["master"]["sha256"] = "0" * 64
        candidate = self.folder / "wrong-master.json"
        candidate.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, "Decision master SHA mismatch"):
            gate.publish(ROOT / gate.MASTER, ROOT / gate.LOCK, ROOT / gate.PROJECTION,
                         candidate, ROUTES, self.folder / "output")
        self.assertFalse((self.folder / "output").exists())


if __name__ == "__main__":
    unittest.main()
