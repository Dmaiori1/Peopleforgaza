# Story submission readiness — not live

Implementation checklist, November 13, 2026. No submissions, private records or real stories belong in this repository. This document describes work still required, not protections already implemented or legal approval.

The current [editorial policy](../editorial-policy.html) and [privacy notice](../privacy.html) keep submissions closed. Preserve the approved public design and wording while preparing implementation.

## Required before collecting any story

| Work | Acceptance evidence | Current status |
| --- | --- | --- |
| Private contact and removal channel | A synthetic correction/removal request reaches an authorized reviewer without becoming a public issue | Not established in current privacy notice |
| Secure intake and storage | Authorized reviewer can access a synthetic submission; another account cannot; unauthenticated requests fail | No intake/backend implemented |
| Informed consent | Contributor can review publication scope in their language and decline without submitting; consent records are private | Workflow required |
| Separate identity choices | Synthetic contributor can choose pseudonym, omit location and decline photo publication independently | Workflow required |
| Media review | Oversized, unsupported and mismatched file types are rejected; identifying metadata is removed from a synthetic image before release | Pipeline required |
| Editorial review | Draft remains private until consent, accuracy and safety checks are complete; graphic imagery is rejected | Review workflow required |
| Corrections and withdrawal | Published synthetic record can be corrected or unpublished; original media and cached derivatives are tracked for removal | Workflow required |
| Translation review | Contributor reviews the intended public translation; reviewers record which version was approved | Qualified review pending |
| Privacy disclosure | Operator, purpose, recipients, retention, deletion and security match the implemented service | Update required before intake |

## Keep private records separate from public content

Public output should contain only the specifically approved story version, display name/pseudonym and reviewed media. Keep consent evidence, contact information, moderation notes and any verification material in private storage with restricted access. Do not use repository files, public issues, URLs, browser logs or analytics events as private storage.

Avoid requesting identity documents, banking information, precise locations or travel routes as part of storytelling. Any independently required verification needs a separately reviewed, secure process. Do not store real records in example fixtures.

## Publication and withdrawal behavior

A future implementation should default to private draft, require review before publication, and allow unpublishing without deleting the private audit record prematurely. Consent must apply to the exact content version and permitted channels; edits or new uses may require renewed review. Do not promise that copies already made by other people can be erased.

Minor participation requires additional safeguarding and appropriate guardian consent. Do not treat consent alone as evidence that publishing identifying content is safe.

## Verification boundaries

Use synthetic labels and neutral test strings only; never invent a family biography or quote. Test unauthorized access, duplicate submissions, interrupted uploads, retries, deletion and translation-version changes before opening intake. Passing static website checks does not verify these future server-side workflows. Payments have separate gates in [payment readiness](payment-readiness.md).
