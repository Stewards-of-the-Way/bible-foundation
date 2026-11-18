#!/usr/bin/env python3
"""Offline regression tests for read-only people/time/place search projection."""
import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_people_place_search.py"
spec = importlib.util.spec_from_file_location("people_place_projection", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / "locked"
        self.source.mkdir()
        self.lock = self.base / "lock.json"
        self.map = self.base / "route-map.json"
        self.map.write_text(json.dumps({"books": [{"code": code, "chapter_count": 150}
                             for code in sorted(set(mod.BOOK_CODES.values()))]}))
        self.person = {"id": "person-nehemiah", "name": "Nehemiah", "aliases": [],
                       "sources": ["Nehemiah 1:1-3"], "geographicContexts": [
                           {"placeId": "place-jerusalem", "role": "wall_rebuilding",
                            "source": "Nehemiah 2:11-17"}]}
        self.place = {"id": "place-jerusalem", "name": "Jerusalem",
                      "precision": "ancient_city", "source": "Nehemiah 2:11"}
        self.event = {"id": "event-nehemiah-wall", "name": "Nehemiah rebuilds Jerusalem wall",
                      "source": "Nehemiah 2:11-18; 6:15",
                      "participants": ["person-nehemiah"], "locationRefs": ["place-jerusalem"]}
        self.evidence = {"eventId": "event-nehemiah-wall", "sourcePassage": "Nehemiah 2:11-18; 6:15",
                         "time": {"displayPolicy": "MODEL_DEPENDENT"},
                         "place": {"placeIds": ["place-jerusalem"],
                                   "displayPolicy": "NOT_PRECISE_EVENT_GPS"}}
        self.feature = {"id": "place-jerusalem", "geometry": {"type": "Point",
                        "coordinates": [35.234167,31.776667]},
                        "properties": {"name": "Jerusalem", "source": "openbible_geocoding_ccby4_via_bsb"}}

    def test_parser_is_conservative_and_shorthand_keeps_book_context(self):
        routes = mod.routes_from_file(self.map)
        scopes = mod.parse_scopes("Nehemiah 2:11-18; 6:15", routes)
        self.assertIn("NEH.2.11", scopes)
        self.assertIn("NEH.6.15", scopes)
        self.assertNotIn("ACT.6.15", scopes)
        self.assertEqual(mod.parse_scopes("unknown 3:16", routes), [])

    def test_source_hash_fail_closed(self):
        self.source.joinpath(mod.FILES["people"]).write_text('{"test":1}')
        self.lock.write_text(json.dumps({"files": [
            {"filename": n, "bytes": 0, "sha256": "0"*64} for n in mod.FILES.values()
        ]}))
        with self.assertRaisesRegex(ValueError, "checksum"):
            mod.read_locked(self.source, self.lock)

    def test_locked_master_and_policy_projection(self):
        # Exercise production-shape source fixtures while leaving source bytes untouched.
        master = {"libraryVersion": "fixture", "people": [self.person],
                  "places": [self.place], "events": [self.event], "relationships": []}
        evidence = {"records": [self.evidence]}
        geo = {"features": [self.feature]}
        self.assertEqual(mod.parse_scopes(self.event["source"], mod.routes_from_file(self.map))[-1], "NEH.6.15")
        # Full builder requires the approved real locked counts; fixtures must not pass as production.
        for kind, doc in zip(("people","events","maps"),(master,evidence,geo)):
            self.source.joinpath(mod.FILES[kind]).write_bytes(mod.canonical_bytes(doc))
        pins=[]
        for name in mod.FILES.values():
            raw=self.source.joinpath(name).read_bytes()
            pins.append({"filename":name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
        self.lock.write_text(json.dumps({"files":pins}))
        with self.assertRaisesRegex(ValueError, "Unexpected locked-master counts"):
            mod.build(self.source,self.lock,self.map,self.base/"generated")
        self.assertFalse((self.base/"generated").exists())

if __name__ == "__main__":
    unittest.main()
