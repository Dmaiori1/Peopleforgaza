"""Synthetic RIFF fixtures only; no contributor records or image rewriting."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_media import ASSETS, check, webp_chunks

def chunk(tag, payload=b""):
    return tag + len(payload).to_bytes(4, "little") + payload + (b"\0" if len(payload) % 2 else b"")

def container(payload):
    return b"RIFF" + (len(payload) + 4).to_bytes(4, "little") + b"WEBP" + payload

class MediaChecks(unittest.TestCase):
    def test_reads_chunks_including_zero_length_and_odd_padding(self):
        data = container(chunk(b"VP8 ", b"test") + chunk(b"TEST") + chunk(b"XMP ", b"x"))
        self.assertEqual(webp_chunks(data), (b"VP8 ", b"TEST", b"XMP "))

    def test_invalid_headers_and_lengths_are_rejected(self):
        for data in (b"", b"RIFF", b"NOTR" + b"\0" * 8,
                     container(chunk(b"VP8 ")) + b"extra"):
            with self.subTest(data=data), self.assertRaisesRegex(ValueError, "^invalid_webp_container$"):
                webp_chunks(data)

    def test_truncated_chunk_headers_and_payloads_are_rejected(self):
        for payload in (b"VP8", b"VP8 " + (9).to_bytes(4, "little") + b"x"):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                webp_chunks(container(payload))

    def test_missing_or_nonzero_padding_is_rejected(self):
        for payload in (b"TEST" + (1).to_bytes(4, "little") + b"x",
                        b"TEST" + (1).to_bytes(4, "little") + b"x!"):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                webp_chunks(container(payload))

    def prepare_assets(self, root, data):
        for relative in ASSETS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def test_clean_assets_are_not_modified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = container(chunk(b"VP8 ", b"synthetic"))
            self.prepare_assets(root, data)
            self.assertEqual(check(root), [])
            self.assertTrue(all((root / relative).read_bytes() == data for relative in ASSETS))

    def test_metadata_requires_review_without_payload_disclosure(self):
        for tag in (b"EXIF", b"XMP "):
            with self.subTest(tag=tag), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.prepare_assets(root, container(chunk(tag, b"PRIVATE_FIXTURE")))
                issues = check(root)
                self.assertEqual(len(issues), len(ASSETS))
                self.assertTrue(all("metadata requires review" in issue for issue in issues))
                self.assertNotIn("PRIVATE_FIXTURE", str(issues))

    def test_missing_asset_and_malformed_container_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(len(check(root)), len(ASSETS))
            self.prepare_assets(root, b"malformed")
            self.assertTrue(all("invalid WebP" in issue for issue in check(root)))

    def test_asset_directory_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            self.prepare_assets(root, container(chunk(b"VP8 ")))
            for name in ("family-scrapbook.webp", "paper-texture.webp"):
                (root / "assets" / name).unlink()
            (root / "assets").rmdir()
            (root / "assets").symlink_to(outside, target_is_directory=True)
            self.assertEqual(sum("symlink requires review" in issue for issue in check(root)), 2)
