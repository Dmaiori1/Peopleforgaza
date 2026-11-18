"""Offline preparation only: compare text-story approvals with an exact draft.

This does not authenticate reviewers, establish consent, publish content, or
open intake. A future private backend must verify the approval records and
recheck withdrawal immediately before publication. Never put real records here.
"""
import hashlib
from html import escape
import json

PUBLIC_TEXT_FIELDS = frozenset(("title", "body", "display_name", "language"))

def story_digest(story):
    """Hash only the supported public text fields, preserving their exact text."""
    if not isinstance(story, dict) or set(story) != PUBLIC_TEXT_FIELDS:
        raise ValueError("unsupported_public_fields")
    if any(not isinstance(value, str) or not value.strip() for value in story.values()):
        raise ValueError("invalid_public_text")
    encoded = json.dumps(story, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

def publication_issues(story, consent=None, review=None):
    """Return fixed reason codes only; an empty list is not launch authorization."""
    try:
        digest = story_digest(story)
    except (ValueError, UnicodeError):
        return ["invalid_public_story"]
    consent = consent if isinstance(consent, dict) else {}
    review = review if isinstance(review, dict) else {}
    issues = []
    if consent.get("state") != "granted":
        issues.append("consent_not_granted")
    if consent.get("content_digest") != digest:
        issues.append("consent_version_mismatch")
    channels = consent.get("channels")
    if not isinstance(channels, list) or "website" not in channels:
        issues.append("website_consent_missing")
    if review.get("state") != "approved":
        issues.append("editorial_review_missing")
    if review.get("content_digest") != digest:
        issues.append("review_version_mismatch")
    if review.get("safety_reviewed") is not True:
        issues.append("safety_review_missing")
    if review.get("language_reviewed") is not True:
        issues.append("language_review_missing")
    return issues

def approved_story_html_fields(story, consent=None, review=None):
    """Prepare escaped fields for quoted HTML attributes/text, never scripts or URLs.

    The caller must use trusted current approval records. This function does
    not authenticate them, render a page, or publish anything.
    """
    if publication_issues(story, consent, review):
        raise ValueError("story_not_ready")
    return {field: escape(story[field], quote=True) for field in sorted(PUBLIC_TEXT_FIELDS)}
