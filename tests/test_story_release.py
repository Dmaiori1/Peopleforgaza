"""Synthetic policy fixtures only: no real family stories or approval records."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from story_release import approved_story_html_fields, publication_issues, story_digest

class StoryReleaseTests(unittest.TestCase):
    def setUp(self):
        self.story = {"title": "Synthetic title", "body": "Synthetic test text",
                      "display_name": "Test label", "language": "en"}
        digest = story_digest(self.story)
        self.consent = {"state": "granted", "content_digest": digest,
                        "channels": ["website"]}
        self.review = {"state": "approved", "content_digest": digest,
                       "safety_reviewed": True, "language_reviewed": True}

    def test_missing_approvals_default_to_not_ready(self):
        issues = publication_issues(self.story)
        self.assertIn("consent_not_granted", issues)
        self.assertIn("editorial_review_missing", issues)

    def test_matching_synthetic_approvals_pass_preparation_check(self):
        self.assertEqual(publication_issues(self.story, self.consent, self.review), [])

    def test_every_public_field_change_requires_fresh_approval(self):
        for field in self.story:
            with self.subTest(field=field):
                edited = dict(self.story)
                edited[field] = "ar" if field == "language" else edited[field] + " changed"
                issues = publication_issues(edited, self.consent, self.review)
                self.assertIn("consent_version_mismatch", issues)
                self.assertIn("review_version_mismatch", issues)

    def test_withdrawal_blocks_preparation_even_for_matching_text(self):
        self.consent["state"] = "withdrawn"
        self.assertIn("consent_not_granted", publication_issues(self.story, self.consent, self.review))

    def test_permission_for_another_channel_is_insufficient(self):
        self.consent["channels"] = ["print"]
        self.assertIn("website_consent_missing", publication_issues(self.story, self.consent, self.review))

    def test_truthy_strings_do_not_replace_explicit_review(self):
        for flag, issue in (("safety_reviewed", "safety_review_missing"),
                            ("language_reviewed", "language_review_missing")):
            with self.subTest(flag=flag):
                review = dict(self.review, **{flag: "true"})
                self.assertIn(issue, publication_issues(self.story, self.consent, review))

    def test_private_or_unknown_fields_are_rejected_without_echoing_values(self):
        story = dict(self.story, private_contact="PRIVATE_FIXTURE")
        self.assertEqual(publication_issues(story, self.consent, self.review), ["invalid_public_story"])
        with self.assertRaisesRegex(ValueError, "^unsupported_public_fields$"):
            story_digest(story)

    def test_key_order_does_not_change_the_digest(self):
        reordered = dict(reversed(list(self.story.items())))
        self.assertEqual(story_digest(reordered), story_digest(self.story))

    def test_invalid_text_and_missing_fields_are_rejected(self):
        for value in (None, {}, dict(self.story, body=" "), dict(self.story, body=False)):
            with self.subTest(value=value):
                self.assertEqual(publication_issues(value), ["invalid_public_story"])

    def test_html_template_fields_escape_markup_and_quotes(self):
        story = dict(self.story, title='Test <tag> & "quote"', body="Synthetic <script>test</script>",
                     display_name="Test 'label'")
        digest = story_digest(story)
        consent = dict(self.consent, content_digest=digest)
        review = dict(self.review, content_digest=digest)
        fields = approved_story_html_fields(story, consent, review)
        self.assertEqual(fields["title"], 'Test &lt;tag&gt; &amp; &quot;quote&quot;')
        self.assertEqual(fields["body"], "Synthetic &lt;script&gt;test&lt;/script&gt;")
        self.assertEqual(fields["display_name"], "Test &#x27;label&#x27;")

    def test_html_fields_preserve_unicode_and_line_breaks(self):
        story = dict(self.story, body="اختبار\n日本語", language="ar")
        digest = story_digest(story)
        fields = approved_story_html_fields(story, dict(self.consent, content_digest=digest),
                                           dict(self.review, content_digest=digest))
        self.assertEqual(fields["body"], story["body"])
        self.assertEqual(fields["language"], "ar")

    def test_html_preparation_requires_current_approval(self):
        for story, consent in ((self.story, None),
                               (self.story, dict(self.consent, state="withdrawn")),
                               (dict(self.story, body="Changed synthetic text"), self.consent)):
            with self.subTest(story=story, consent=consent):
                with self.assertRaisesRegex(ValueError, "^story_not_ready$"):
                    approved_story_html_fields(story, consent, self.review)

    def test_html_preparation_returns_only_public_fields_without_mutation(self):
        consent = dict(self.consent, private_note="PRIVATE_FIXTURE")
        review = dict(self.review, private_note="PRIVATE_FIXTURE")
        original = dict(self.story)
        fields = approved_story_html_fields(self.story, consent, review)
        self.assertEqual(set(fields), set(original))
        self.assertNotIn("PRIVATE_FIXTURE", str(fields))
        self.assertEqual(self.story, original)

    def test_html_attribute_field_escapes_quotes(self):
        story = dict(self.story, language='en" data-test="fixture')
        digest = story_digest(story)
        fields = approved_story_html_fields(story, dict(self.consent, content_digest=digest),
                                           dict(self.review, content_digest=digest))
        self.assertEqual(fields["language"], "en&quot; data-test=&quot;fixture")

if __name__ == "__main__":
    unittest.main()
