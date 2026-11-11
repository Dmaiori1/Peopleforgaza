"""Regression tests for the offline checker: python3 -m unittest discover -s tests"""
import importlib.util
from pathlib import Path
import tempfile
import unittest
spec = importlib.util.spec_from_file_location("check_site", Path(__file__).resolve().parents[1] / "scripts/check_site.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class CheckerTests(unittest.TestCase):
    def run_case(self, extra="", html_attrs='lang="en"'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text('<!doctype html><html '+html_attrs+'><main id="main"><h1>Example</h1>'+extra+'</main></html>', encoding="utf-8")
            return checker.check(root)
    def test_malformed_url_reports_error(self):
        self.assertTrue(any("malformed link" in e for e in self.run_case('<a href="https://[broken">Broken</a>')))
    def test_missing_image_is_rejected(self):
        self.assertTrue(any("missing link target" in e for e in self.run_case('<img src="missing.webp" alt="Illustration">')))
    def test_valid_page(self):
        self.assertEqual(self.run_case('<a href="#main">Content</a>'), [])
    def test_broken_fragment(self):
        self.assertTrue(any("missing fragment" in e for e in self.run_case('<a href="#absent">Broken</a>')))
    def test_missing_file(self):
        self.assertTrue(any("missing link target" in e for e in self.run_case('<a href="missing.html">Broken</a>')))
    def test_duplicate_id(self):
        self.assertTrue(any("duplicate id" in e for e in self.run_case('<div id="main"></div>')))
    def test_collection_controls(self):
        for markup in ('<form></form>', '<input>', '<script></script>', '<iframe></iframe>'):
            with self.subTest(markup=markup): self.assertTrue(self.run_case(markup))
    def test_arabic_direction(self):
        self.assertTrue(any("RTL" in e for e in self.run_case(html_attrs='lang="ar"')))
        self.assertEqual(self.run_case(html_attrs='lang="ar" dir="rtl"'), [])
    def test_regional_arabic_requires_rtl(self):
        self.assertTrue(any("RTL" in e for e in self.run_case(html_attrs='lang="ar-PS"')))
        self.assertEqual(self.run_case(html_attrs='lang="ar-PS" dir="rtl"'), [])
    def test_missing_alt(self):
        self.assertTrue(any("missing alt" in e for e in self.run_case('<img src="picture.png">')))
    def test_insecure_link(self):
        self.assertTrue(any("insecure" in e for e in self.run_case('<a href="http://example.test">Link</a>')))

    def test_inline_event_handlers_require_review(self):
        self.assertTrue(any("event handler" in e for e in self.run_case('<img alt="" onerror="alert(1)">')))
    def test_meta_refresh_requires_review(self):
        self.assertTrue(any("refresh" in e for e in self.run_case('<meta http-equiv="refresh" content="0;url=https://example.test">')))
    def test_active_embeds_require_review(self):
        for markup in ('<object data="https://example.test"></object>', '<embed src="https://example.test">'):
            with self.subTest(markup=markup):
                self.assertTrue(any("embedded" in e for e in self.run_case(markup)))

if __name__ == "__main__": unittest.main()
