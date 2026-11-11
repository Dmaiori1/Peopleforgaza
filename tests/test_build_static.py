"""Packaging regressions: python3 -m unittest discover -s tests"""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_static import build

PAGES = ("index.html", "ar.html", "privacy.html", "editorial-policy.html")
HTML = '<!doctype html><html lang="en"><main><h1>Example</h1></main></html>'

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in PAGES: (self.root / name).write_text(HTML, encoding="utf-8")
    def test_only_public_pages_are_copied(self):
        (self.root / "private-notes.txt").write_text("not public")
        output = build(self.root)
        self.assertEqual(sorted(p.name for p in output.iterdir()), sorted(PAGES))
        for name in PAGES: self.assertEqual((output/name).read_bytes(), (self.root/name).read_bytes())
    def test_redesign_artwork_is_packaged(self):
        artwork = self.root / "people-for-gaza-artwork.webp"
        artwork.write_bytes(b"reviewed-artwork")
        output = build(self.root)
        self.assertEqual((output / artwork.name).read_bytes(), artwork.read_bytes())
    def test_funding_page_is_packaged(self):
        (self.root / "funding-transparency.html").write_text(HTML)
        (self.root / "index.html").write_text(HTML.replace("</main>", '<a href="funding-transparency.html">Funding</a></main>'))
        output = build(self.root)
        self.assertEqual((output / "funding-transparency.html").read_text(), HTML)
    def test_symlinked_asset_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            (Path(elsewhere) / "private.webp").write_bytes(b"private")
            (self.root / "assets").symlink_to(elsewhere, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"): build(self.root)
            self.assertFalse((self.root / "dist").exists())
    def test_existing_output_is_not_overwritten(self):
        output = self.root / "dist"
        output.mkdir()
        (output / "keep.txt").write_text("keep")
        with self.assertRaises(ValueError): build(self.root)
        self.assertEqual((output/"keep.txt").read_text(), "keep")
    def test_missing_page_creates_no_output(self):
        (self.root/"ar.html").unlink()
        with self.assertRaises(ValueError): build(self.root)
        self.assertFalse((self.root/"dist").exists())
    def test_invalid_page_creates_no_output(self):
        (self.root/"index.html").write_text(HTML.replace("</main>", '<form></form></main>'))
        with self.assertRaises(ValueError): build(self.root)
        self.assertFalse((self.root/"dist").exists())
    def test_symlinked_public_page_is_rejected(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            external = Path(elsewhere)/"private.html"
            external.write_text(HTML)
            (self.root/"index.html").unlink()
            (self.root/"index.html").symlink_to(external)
            with self.assertRaisesRegex(ValueError, "symlink"): build(self.root)
            self.assertFalse((self.root/"dist").exists())

if __name__ == "__main__": unittest.main()
