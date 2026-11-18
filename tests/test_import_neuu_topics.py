#!/usr/bin/env python3
"""Offline tests for the NEUU topics importer: no third-party network access."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "import_neuu_topics.py"
spec = importlib.util.spec_from_file_location("topic_import", SCRIPT)
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)
PIN = "eeb9b7418be4d02c497d142da3b9890fad356252"

class TopicImportTests(unittest.TestCase):
    def setUp(self):
        self.ctx = tempfile.TemporaryDirectory()
        self.addCleanup(self.ctx.cleanup)
        self.root = Path(self.ctx.name)
        self.source = self.root / "01_parsed"
        (self.source / "F").mkdir(parents=True)
        self.route = self.root / "route-map.json"
        self.route.write_text(json.dumps({"books": [
            {"code": "JHN", "chapter_count": 21},
            {"code": "ACT", "chapter_count": 28},
            {"code": "GEN", "chapter_count": 50}
        ]}))
        self.entry = {
            "topic": "FAITH", "slug": "faith", "sources": ["NAV", "TOR"],
            "see_also": ["HOPE"],
            "aspects": [{"label": "In Christ", "references": ["John 3:16"], "source": "TOR"}],
            "biblical_references": [
                {"book": "John", "chapter": 3, "verses": [16], "raw": "John 3:16"},
                {"book": "Acts", "chapter": 2, "verses": [41,42], "raw": "Acts 2:41,42"}
            ]
        }
        (self.source / "F/faith.json").write_text(json.dumps(self.entry))

    def test_offline_sample_preserves_source_and_emits_search_indexes(self):
        out = self.root / "output"
        report = importer.import_topics(self.source, self.route, out, PIN, allow_partial=True)
        self.assertEqual(report["unresolved_reference_entries"], 0)
        self.assertEqual(report["source_topic_files"], 1)
        shard = json.loads((out / "topics/F.json").read_text())
        topic = shard["topics"][0]
        self.assertEqual(topic["aspects"], self.entry["aspects"])
        self.assertEqual(topic["references"][0]["verse_ids"], ["JHN.3.16"])
        reverse = json.loads((out / "index/by-scripture/ACT.json").read_text())
        self.assertEqual(reverse["verses"]["ACT.2.41"], ["NEUU:TOPIC:faith"])
        self.assertEqual(json.loads((out / "manifest.json").read_text())["counts"]["topics"], 1)
        self.assertFalse((out / "api").exists())

    def test_ambiguous_source_reference_remains_visible_and_unlinked(self):
        self.entry["biblical_references"].append({"book": "Unknown", "chapter": 1,
                                                    "verses": [2], "raw": "Unknown 1:2"})
        (self.source / "F/faith.json").write_text(json.dumps(self.entry))
        out = self.root / "output"
        report = importer.import_topics(self.source, self.route, out, PIN, allow_partial=True)
        self.assertEqual(report["unresolved_reference_entries"], 1)
        self.assertEqual(report["unresolved"][0]["reason"], "unknown_book")
        self.assertEqual(json.loads((out / "topics/F.json").read_text())["topics"][0]
                         ["references"][-1]["status"], "unresolved")

    def test_no_partial_promotion_or_implicit_overwrite(self):
        out = self.root / "output"
        with self.assertRaisesRegex(ValueError, "expected 66"):
            importer.import_topics(self.source, self.route, out, PIN)
        importer.import_topics(self.source, self.route, out, PIN, allow_partial=True)
        with self.assertRaisesRegex(ValueError, "overwrite"):
            importer.import_topics(self.source, self.route, out, PIN, allow_partial=True)

if __name__ == "__main__":
    unittest.main()
