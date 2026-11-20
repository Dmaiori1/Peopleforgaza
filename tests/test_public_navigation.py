"""Navigation contracts for the current public prototype, without browser/network access."""
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = ("index.html", "ar.html", "privacy.html", "editorial-policy.html",
                "funding-transparency.html", "404.html")

class Navigation(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links, self.alternates = [], []
        self.language = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang")
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "link" and "alternate" in (values.get("rel") or "").split():
            self.alternates.append((values.get("hreflang"), values.get("href")))

def local_page(href, current):
    url = urlsplit(href)
    if url.scheme or url.netloc:
        return None
    return unquote(url.path).lstrip("/") or current

def reachable(graph, start):
    visited, pending = set(), deque([start])
    while pending:
        current = pending.popleft()
        if current not in visited:
            visited.add(current)
            pending.extend(graph[current] - visited)
    return visited

class PublicNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {name: Navigation((ROOT / name).read_text(encoding="utf-8"))
                     for name in PUBLIC_PAGES}

    def test_regular_pages_are_reachable_and_every_page_has_a_route_home(self):
        graph = {name: {target for href in page.links
                        if (target := local_page(href, name)) in self.pages}
                 for name, page in self.pages.items()}
        # A recovery page need not be linked from the regular navigation.
        self.assertTrue(set(PUBLIC_PAGES) - {"404.html"} <= reachable(graph, "index.html"))
        for name in PUBLIC_PAGES:
            with self.subTest(page=name):
                self.assertIn("index.html", reachable(graph, name))

    def test_homepage_language_alternates_are_reciprocal_and_match_documents(self):
        expected = {"en": "index.html", "ar": "ar.html", "x-default": "index.html"}
        for name in ("index.html", "ar.html"):
            with self.subTest(page=name):
                alternates = self.pages[name].alternates
                self.assertEqual(len(alternates), len(expected))
                self.assertEqual(dict(alternates), expected)
                for language, href in alternates:
                    target = self.pages[href]
                    if language != "x-default":
                        self.assertEqual(target.language, language)

if __name__ == "__main__":
    unittest.main()
