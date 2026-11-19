#!/usr/bin/env python3
"""Read-only audit of reviewed WebP assets; not an upload sanitizer or decoder.

Checks top-level RIFF framing and flags EXIF/XMP chunks for review. This does
not detect identifying pixels, all metadata formats, or establish consent.
"""
from pathlib import Path
import sys

ASSETS = ("people-for-gaza-artwork.webp", "assets/family-scrapbook.webp",
          "assets/paper-texture.webp")

def webp_chunks(data):
    """Read top-level chunk identifiers without decoding or exposing payloads."""
    if (not isinstance(data, bytes) or len(data) < 12 or data[:4] != b"RIFF"
            or data[8:12] != b"WEBP"
            or int.from_bytes(data[4:8], "little") + 8 != len(data)):
        raise ValueError("invalid_webp_container")
    position, chunks = 12, []
    while position < len(data):
        if position + 8 > len(data):
            raise ValueError("invalid_webp_container")
        tag = data[position:position + 4]
        size = int.from_bytes(data[position + 4:position + 8], "little")
        end = position + 8 + size
        padded_end = end + (size % 2)
        if padded_end > len(data) or (size % 2 and data[end] != 0):
            raise ValueError("invalid_webp_container")
        chunks.append(tag)
        position = padded_end
    return tuple(chunks)

def check(root):
    root = Path(root).resolve()
    issues = []
    for relative in ASSETS:
        path = root / relative
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents
                                    if parent.is_relative_to(root)):
            issues.append(relative + ": symlink requires review")
            continue
        try:
            chunks = webp_chunks(path.read_bytes())
        except OSError:
            issues.append(relative + ": asset unavailable")
            continue
        except ValueError:
            issues.append(relative + ": invalid WebP container framing")
            continue
        if b"EXIF" in chunks or b"XMP " in chunks:
            issues.append(relative + ": EXIF/XMP metadata requires review")
    return issues

if __name__ == "__main__":
    issues = check(Path(__file__).resolve().parents[1])
    for issue in issues:
        print("FAIL:", issue)
    if issues:
        sys.exit(1)
    print("PASS: reviewed WebP framing; no top-level EXIF/XMP chunks")
