"""Source-level privacy contracts; these do not capture browser request headers."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = ("index.html", "ar.html", "privacy.html", "editorial-policy.html",
                "funding-transparency.html", "404.html")

class ReferrerMarkup(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.policies = []
        self.overrides = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "meta" and (values.get("name") or "").lower() == "referrer":
            self.policies.append((values.get("content") or "").strip().lower())
        if "referrerpolicy" in values:
            self.overrides.append((values["referrerpolicy"] or "").strip().lower())

class PublicPrivacyTests(unittest.TestCase):
    def test_public_pages_retain_no_referrer_without_weaker_element_overrides(self):
        for name in PUBLIC_PAGES:
            with self.subTest(page=name):
                page = ReferrerMarkup((ROOT / name).read_text(encoding="utf-8"))
                self.assertEqual(page.policies, ["no-referrer"])
                self.assertTrue(all(policy == "no-referrer" for policy in page.overrides))

if __name__ == "__main__":
    unittest.main()
