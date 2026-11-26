"""Regression tests for the offline checker: python3 -m unittest discover -s tests"""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
spec = importlib.util.spec_from_file_location("check_site", Path(__file__).resolve().parents[1] / "scripts/check_site.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class CheckerTests(unittest.TestCase):
    def test_page_read_failures_report_without_stopping_other_checks(self):
        for failure in ("encoding", "directory", "permission"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                bad = root / "bad.html"
                (root / "index.html").write_text(
                    '<html lang="en"><main><h1>Fixture</h1>'
                    '<a href="javascript:fixture()">Other</a></main></html>', encoding="utf-8")
                if failure == "directory":
                    bad.mkdir()
                else:
                    bad.write_bytes(b"\xffPRIVATE_FIXTURE" if failure == "encoding" else b"fixture")
                original_read = Path.read_text
                def read(path, *args, **kwargs):
                    if path == bad and failure == "permission":
                        raise PermissionError("PRIVATE_FIXTURE")
                    return original_read(path, *args, **kwargs)
                with patch.object(Path, "read_text", read):
                    errors = checker.check(root)
                self.assertIn("bad.html: unable to read UTF-8 HTML file", errors)
                self.assertTrue(any("insecure" in error for error in errors))
                self.assertNotIn("PRIVATE_FIXTURE", str(errors))
                self.assertTrue(bad.exists())

    def run_case(self, extra="", html_attrs='lang="en"'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text('<!doctype html><html '+html_attrs+'><main id="main"><h1>Example</h1>'+extra+'</main></html>', encoding="utf-8")
            return checker.check(root)
    def test_null_local_paths_report_without_stopping_validation(self):
        for href in ("%00", "/%00.html", "asset%00.webp", "%00/"):
            with self.subTest(href=href):
                errors = self.run_case('<a href="' + href + '">Fixture</a>'
                                       '<a href="javascript:fixture()">Other</a>')
                self.assertTrue(any("malformed local link path" in error for error in errors))
                self.assertTrue(any("insecure" in error for error in errors))
                self.assertFalse(any(href in error for error in errors))
    def test_malformed_url_reports_error(self):
        self.assertTrue(any("malformed link" in e for e in self.run_case('<a href="https://[broken">Broken</a>')))
    def test_valueless_metadata_does_not_hide_other_validation_errors(self):
        errors = self.run_case('<meta http-equiv><a href="javascript:fixture()">Fixture</a>')
        self.assertTrue(any("insecure" in error for error in errors))
    def test_valueless_duplicate_ids_report_without_crashing(self):
        errors = self.run_case('<div id></div><span id></span>')
        self.assertTrue(any("duplicate id" in error for error in errors))
    def test_missing_image_is_rejected(self):
        self.assertTrue(any("missing link target" in e for e in self.run_case('<img src="missing.webp" alt="Illustration">')))
    def test_missing_responsive_image_candidates_are_rejected(self):
        for markup in (
            '<picture><source srcset="missing-mobile.webp"><img src="index.html" alt="Fixture"></picture>',
            '<img src="index.html" srcset="index.html 1x, missing-large.webp 2x" alt="Fixture">',
        ):
            with self.subTest(markup=markup):
                self.assertTrue(any("missing link target" in e for e in self.run_case(markup)))
    def test_responsive_candidates_keep_commas_inside_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("small.webp", "large,wide.webp"):
                (root / name).write_bytes(b"fixture")
            (root / "index.html").write_text('<html lang="en"><main><h1>Fixture</h1><picture><source srcset="small.webp 1x, large,wide.webp 2x"><img src="small.webp" alt="Fixture"></picture></main></html>')
            self.assertEqual(checker.check(root), [])
    def test_responsive_image_schemes_require_review(self):
        self.assertTrue(any("insecure" in e for e in self.run_case('<img src="index.html" srcset="http://example.test/image.webp 2x" alt="Fixture">')))
    def test_responsive_candidate_url_tokenization(self):
        for value, expected in (
            ("small.webp, large.webp 2x", ["small.webp", "large.webp"]),
            ("small.webp 1x,large,wide.webp 2x", ["small.webp", "large,wide.webp"]),
            ("data:image/png;base64,AAAA 1x, large.webp 2x", ["data:image/png;base64,AAAA", "large.webp"]),
            ("small.webp future(a,b), large.webp 2x", ["small.webp", "large.webp"]),
            ("", []),
        ):
            with self.subTest(value=value):
                self.assertEqual(checker.image_candidate_urls(value), expected)
    def test_base_url_requires_review(self):
        self.assertTrue(any("base URL" in e for e in self.run_case('<base href="https://other.example/"><a href="#main">Content</a>')))
    def test_missing_css_background_is_rejected(self):
        self.assertTrue(any("missing link target" in e for e in self.run_case("<style>body{background:url(\'missing.webp\')}</style>")))
    def test_missing_inline_css_background_is_rejected(self):
        for markup in (
            '<div style="background:url(missing.webp)"></div>',
            '<div STYLE="background:URL(&quot;missing.webp&quot;)"></div>',
            '<div style="background:url(index.html),url(missing.webp)"></div>',
        ):
            with self.subTest(markup=markup):
                self.assertTrue(any("missing link target" in e for e in self.run_case(markup)))
    def test_inline_css_urls_use_existing_safety_checks(self):
        for url, error in (
            ('http://example.test/image.webp', 'insecure'),
            ('/%2e%2e/private.webp', 'escapes site root'),
        ):
            with self.subTest(url=url):
                self.assertTrue(any(error in e for e in self.run_case('<div style="background:url('+url+')"></div>')))
    def test_inline_css_existing_urls_and_comments(self):
        self.assertEqual(self.run_case('<div style="background:url(/index.html); /* url(missing.webp) */ color:gold"></div>'), [])
    def test_heading_outside_main_is_rejected(self):
        for html in ('<h1>Title</h1><main></main>', '<main></main><h1>Title</h1>'):
            with self.subTest(html=html):
                self.assertTrue(any("h1 outside main" in e for e in checker.Page(html).errors))
    def test_valid_page(self):
        self.assertEqual(self.run_case('<a href="#main">Content</a>'), [])
    def test_duplicate_attributes_cannot_hide_unchecked_values(self):
        for markup in (
            '<a href="javascript:fixture()" href="#main">Fixture</a>',
            '<a HREF="http://example.test" href="#main">Fixture</a>',
            '<img src="missing.webp" src="index.html" alt="Fixture">',
            '<div id="main" id="other"></div>',
            '<div style="background:url(missing.webp)" style="color:gold"></div>',
        ):
            with self.subTest(markup=markup):
                self.assertTrue(any("duplicate HTML attribute" in e for e in self.run_case(markup)))
    def test_attributes_can_repeat_across_separate_elements(self):
        self.assertEqual(self.run_case('<a href="#main">One</a><a href="#main">Two</a>'), [])
    def test_site_root_links_resolve_inside_package(self):
        self.assertEqual(self.run_case('<a href="/index.html#main">Home</a><a href="/#main">Home</a>'), [])
    def test_encoded_parent_path_still_cannot_escape_root(self):
        self.assertTrue(any("escapes site root" in e for e in self.run_case('<a href="/%2e%2e/private.txt">Invalid</a>')))
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
    def test_hyperlink_auditing_requires_privacy_review(self):
        for markup in (
            '<a href="#main" ping="https://audit.example.test/track">Link</a>',
            '<area href="#main" ping="/audit" alt="Link">',
            '<A HREF="#main" PING="https://audit.example.test/one https://audit.example.test/two">Link</A>',
        ):
            with self.subTest(markup=markup):
                self.assertTrue(any("hyperlink auditing" in e for e in self.run_case(markup)))
    def test_meta_refresh_requires_review(self):
        self.assertTrue(any("refresh" in e for e in self.run_case('<meta http-equiv="refresh" content="0;url=https://example.test">')))
    def test_active_embeds_require_review(self):
        for markup in ('<object data="https://example.test"></object>', '<embed src="https://example.test">'):
            with self.subTest(markup=markup):
                self.assertTrue(any("embedded" in e for e in self.run_case(markup)))

if __name__ == "__main__": unittest.main()
