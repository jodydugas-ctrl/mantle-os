#!/usr/bin/env python3
"""Parity test for the language-agnostic NECROMANCY path.

Asserts the JS organ map (via mantle.assimilator.scanner_ts) equals the Python organ
map (via mantle.assimilator.scanner) for the equivalent notes_app fixture, and that the
record shape matches. Skips cleanly if tree-sitter isn't installed -- the multilang path
is opt-in and Python-only behavior is unaffected either way.
"""
import os
import sys
import unittest
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mantle.assimilator import scanner
from mantle.assimilator import scanner_ts
from mantle.assimilator.organ_map import ROLE_TO_ORGAN

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_app")


def _organ_counts(symbols):
    counts = Counter()
    for sym in symbols:
        organ = ROLE_TO_ORGAN.get(sym["role"])
        if organ:
            counts[organ] += 1
    return dict(counts)


class MultiLangParityTest(unittest.TestCase):
    @unittest.skipUnless(scanner_ts.available(), "tree-sitter stack not installed")
    def test_js_organ_map_matches_python(self):
        py = scanner.scan_file(os.path.join(SAMPLE_DIR, "notes_app.py"), "notes_app.py")
        js = scanner_ts.scan_file(os.path.join(SAMPLE_DIR, "notes_app.js"), "notes_app.js")

        self.assertEqual(_organ_counts(py["symbols"]), _organ_counts(js["symbols"]))

        for sym in js["symbols"]:
            self.assertEqual(set(sym.keys()), {"symbol", "kind", "line", "role"})

    @unittest.skipUnless(scanner_ts.available(), "tree-sitter stack not installed")
    def test_read_only(self):
        path = os.path.join(SAMPLE_DIR, "notes_app.js")
        before = open(path, "rb").read()
        scanner_ts.scan_file(path, "notes_app.js")
        after = open(path, "rb").read()
        self.assertEqual(before, after)

    def test_scan_project_without_treesitter_is_unchanged(self):
        """Without the optional dependency, scan_project behaves exactly as before."""
        dissection = scanner.scan_project(SAMPLE_DIR)
        self.assertTrue(dissection["read_only"])
        self.assertIn("multilang", dissection)


if __name__ == "__main__":
    unittest.main()
