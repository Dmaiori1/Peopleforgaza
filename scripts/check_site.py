#!/usr/bin/env python3
"""Offline static-site checks. Run: python3 scripts/check_site.py [site-root]"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
import re

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.errors = set(), [], []
        self.lang = self.direction = None
        self.main = self.h1 = 0
        self.main_depth = 0
        self.in_style = False
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "style": self.in_style = True
        if any(name.startswith("on") for name in a):
            self.errors.append("inline event handler requires privacy/security review")
        if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
            self.errors.append("automatic refresh/redirect requires review")
        if tag == "base":
            self.errors.append("document base URL/target requires navigation and privacy review")
        if tag == "html":
            self.lang, self.direction = a.get("lang"), a.get("dir")
        if "id" in a:
            if a["id"] in self.ids:
                self.errors.append("duplicate id: " + a["id"])
            self.ids.add(a["id"])
        if tag == "main":
            self.main += 1
            self.main_depth += 1
        if tag == "h1":
            self.h1 += 1
            if not self.main_depth: self.errors.append("h1 outside main landmark")
        if tag in ("a", "link") and "href" in a: self.links.append(a["href"])
        if tag in ("form", "input", "textarea", "select"):
            self.errors.append("data collection control requires safety review: " + tag)
        if tag == "script":
            self.errors.append("script requires privacy/security review")
        if tag == "img" and "src" in a: self.links.append(a["src"])
        if tag == "img" and "alt" not in a:
            self.errors.append("image missing alt")
        if tag in ("iframe", "object", "embed"):
            self.errors.append("embedded third-party content requires review")

    def handle_endtag(self, tag):
        if tag == "main": self.main_depth = max(0, self.main_depth - 1)
        if tag == "style": self.in_style = False
    def handle_data(self, data):
        if self.in_style:
            # Covers literal url() references in embedded styles, not a full CSS parser.
            data = re.sub(r"/\*.*?\*/", "", data, flags=re.S)
            for match in re.finditer(r"""url\(\s*(['"]?)(.*?)\1\s*\)""", data, flags=re.I | re.S):
                self.links.append(match.group(2).strip())

def check(root):
    root = Path(root).resolve()
    paths = sorted(root.glob("*.html"))
    errors = []
    if not paths: return ["no root HTML pages found"]
    pages = {p.resolve(): Page(p.read_text(encoding="utf-8")) for p in paths}
    for path, page in pages.items():
        name = path.name
        errors.extend(name + ": " + e for e in page.errors)
        if not page.lang: errors.append(name + ": missing document language")
        if (page.lang or "").lower().split("-")[0] == "ar" and page.direction != "rtl":
            errors.append(name + ": Arabic document needs RTL")
        if page.main != 1: errors.append(name + ": expected one main landmark")
        if page.h1 != 1: errors.append(name + ": expected one h1")
        for href in page.links:
            try:
                url = urlsplit(href)
            except ValueError:
                errors.append(name + ": malformed link URL")
                continue
            if url.scheme or url.netloc:
                if url.scheme not in ("https", "mailto", "tel"):
                    errors.append(name + ": unsupported or insecure link scheme")
                continue
            local_path = unquote(url.path)
            if local_path.startswith("/"):
                target = (root / local_path.lstrip("/")).resolve()
            else:
                target = (path.parent / local_path).resolve() if local_path else path
            if local_path.endswith("/"):
                target = (target / "index.html").resolve()
            if not target.is_relative_to(root):
                errors.append(name + ": link escapes site root")
                continue
            if not target.is_file():
                errors.append(name + ": missing link target " + href)
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(name + ": missing fragment " + href)
    return errors

if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = check(root)
    for error in errors: print("FAIL:", error)
    if errors: sys.exit(1)
    print("PASS: static links, landmarks, languages, images and closed data collection")
