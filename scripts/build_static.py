#!/usr/bin/env python3
"""Validate and stage the current static prototype: python3 scripts/build_static.py"""
from pathlib import Path
import shutil
import sys
from check_site import check

def build(root):
    root = Path(root).resolve()
    pages = ("index.html", "ar.html", "privacy.html", "editorial-policy.html")
    linked = [name for name in pages if (root / name).is_symlink()]
    if linked: raise ValueError("Public pages must not be symlinks: " + ", ".join(linked))
    missing = [name for name in pages if not (root / name).is_file()]
    if missing: raise ValueError("Missing required pages: " + ", ".join(missing))
    errors = check(root)
    if errors: raise ValueError("\n".join(errors))
    output = root / "dist"
    if output.exists() or output.is_symlink():
        raise ValueError("dist already exists; review and remove the previous output before rebuilding")
    # Copy only reviewed public pages, never repository history, tests or private drafts.
    output.mkdir()
    try:
        for name in pages: shutil.copyfile(root / name, output / name)
        artwork = root / "people-for-gaza-artwork.webp"
        if artwork.is_symlink(): raise ValueError("Public artwork must not be a symlink")
        if artwork.is_file(): shutil.copyfile(artwork, output / artwork.name)
        errors = check(output)
        if errors: raise ValueError("\n".join(errors))
    except Exception:
        shutil.rmtree(output)
        raise
    return output

if __name__ == "__main__":
    try:
        output = build(Path(__file__).resolve().parents[1])
    except (OSError, ValueError) as error:
        print("Build failed:", error, file=sys.stderr)
        sys.exit(1)
    print("Validated static package:", output)
    print("Contains four public HTML pages. No hosting, payments or collection enabled.")
