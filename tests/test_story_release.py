"""Synthetic policy fixtures only: no real family stories or approval records."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from story_release import publication_issues, story_digest

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

if __name__ == "__main__":
    unittest.main()
