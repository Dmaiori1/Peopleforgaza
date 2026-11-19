# Development guidance — People for Gaza

Applies throughout this repository. Read [README.md](README.md) and [TESTING.md](TESTING.md) before changing files.

## Preserve Denise’s design and project

- Work on `Dmaiori1/Peopleforgaza`. The linked VIII Site is a different project; do not edit or deploy it for this website.
- Preserve the existing public layout, wording, fonts, colors, artwork and decorative details. Do not redesign or replace assets without explicit direction from Denise. Report any conflict between a functional fix and the design before making a visual change.
- Keep English/Arabic navigation, the privacy notice, editorial policy and fictional-placeholder labels intact. Do not invent family biographies, testimony, consent or documentary images.
- Preserve the existing domain, DNS, CNAME, .nojekyll and GitHub Pages settings. The package builder prepares output; it does not change hosting.

## Privacy and launch boundaries

- This is a public repository. Never commit real submissions, consent evidence, contact details, identity documents, private moderation notes, banking information, credentials or secret keys. A file excluded from `dist/` is still public if committed here.
- Use neutral synthetic labels and test data. Do not collect sensitive information through public issues, pull requests or static forms.
- Keep story intake, checkout and payouts inactive. Follow [story readiness](docs/story-readiness.md) and [payment readiness](docs/payment-readiness.md) before integration. Offline approval checks are not authenticated consent, access control or permission to publish.
- Do not incur costs, activate payments/donations, publish private information or accept binding terms without explicit approval.

## Verify bounded changes

- Run `python3 scripts/verify.py` for code or public-source changes. It runs static checks, Python regressions and offline JavaScript checks without installing dependencies or contacting a provider.
- For packaging changes, run `python3 scripts/build_static.py` in a clean working copy. The builder intentionally refuses existing `dist/`; do not delete unreviewed output just to make the command pass. Use a disposable copy when appropriate.
- Preserve the reviewed public-file allowlist. Check that packaged public content is unchanged when a fix affects only development tooling.
- Reproduce a claimed defect before fixing it. Keep tests tied to the failure or required behavior, and avoid duplicate counts or speculative claims.
- Record material evidence and limitations in [TESTING.md](TESTING.md). Distinguish local tests, GitHub verification, Pages build success and observed live behavior. Do not claim physical-device, screen-reader, real consent, live payment or live-domain verification from static tests or iframe previews.
