# People for Gaza

An independent, in-development website for consent-based storytelling by families in Gaza.

## Current status
The homepage is a static prototype. **No story submission form, donation processing, or family verification is live.** Do not solicit or collect sensitive information through GitHub issues, public pull requests, or the repository.

## Design
Navy blue, lavender, gentle botanical accents, responsive HTML.

## Publishing
The root `index.html` can be deployed on a static host (GitHub Pages, Render Static Site, etc.). Hosting must be explicitly configured in the hosting provider. A domain purchase is not required for a preview URL.

## Before accepting stories
- Obtain informed, revocable consent in the contributor's language.
- Provide anonymity/pseudonymity choices; remove identifying metadata from images.
- Avoid publishing real-time locations, evacuation routes, identity documents, contact information, or other high-risk details.
- Establish moderation, secure storage, deletion process, translations, and safeguarding for minors.
- Do not expose submissions publicly before review.

## Before accepting donations
- Identify the legal operator and beneficiary, document the transfer and verification process, explain payment-provider fees and any platform fee, and confirm applicable legal and sanctions compliance with qualified advisers and payment processors.
- Do not claim donations are tax deductible unless this is verified.
- Test payment webhooks and refund/chargeback handling in sandbox mode first.

See [Editorial & Safety Policy](editorial-policy.html) and [Privacy](privacy.html).

## Offline checks
Requires Python 3.9 or newer; no package installation or network access is needed.

```sh
python3 scripts/check_site.py
python3 -m unittest discover -s tests
```

The checker validates root HTML pages for local links/fragments, one main landmark and heading, document languages/Arabic direction, image alt attributes, and insecure link schemes. Forms, input controls, scripts, and iframes fail review checks while submissions remain closed. This is a static regression guard, not a security certification or browser/screen-reader test. External URL availability, contrast, layout, and translation accuracy require separate review. It does not contact visitors or collect data.

## Prepare a deployment package

```sh
python3 scripts/build_static.py
```

This validates the source pages and creates `dist/` containing only `index.html`, `ar.html`, `privacy.html`, and `editorial-policy.html`. It validates links again in the staged output and refuses to overwrite an existing `dist/`. Review and remove old output explicitly before rebuilding. No dependencies, hosting calls, payment services, or collection endpoints are enabled. Future public assets must be added to the reviewed allowlist before they are used.

Deploy only the staged directory after separately configuring the correct People for Gaza host. The VIII Site project ID must not be reused for this project. External Google Fonts still require connectivity; browser/device and translation reviews remain necessary before launch.

## Design preservation — Denise’s instruction, November 11, 2026

The current implementation is an approximation, not an approved replacement for the selected reference. Restoration remains incomplete.

The authoritative selection is the screenshot `IMG_2297.jpeg` shared with “Keep the text and font as is.” It shows navy/lavender/cream scrapbook styling: textured torn parchment, lace, tape, Polaroid framing, delicate botanical illustrations, handwritten details, and the original copy and typography. Restore against that visual reference, not a new interpretation. Reference imagery must not be presented as verified family testimony or consented documentary photographs.

After restoration, preserve layout, colors, fonts, wording, imagery, and decorative details. Do not redesign or substitute assets without Denise’s explicit request. Functional, security, accessibility, and deployment work must preserve the approved appearance; report conflicts rather than silently changing it. Verify desktop and mobile rendering against the reference before claiming restoration is complete.
