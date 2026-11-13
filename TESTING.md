# Verification record

Updated November 12, 2026. This records bounded checks, not launch approval.

## Automated checks
Run from the repository root with Python 3.9 or newer:
```sh
python3 scripts/check_site.py
python3 -m unittest discover -s tests
python3 scripts/build_static.py
```
The build refuses existing dist output. Review and remove old output explicitly before rebuilding.

The most recently executed full regression suite passed 28 tests. Coverage includes local links and image sources, fragments, basic document structure, Arabic/ regional Arabic direction, review gates for active content and data collection, and static packaging safeguards. This does not establish comprehensive accessibility, security, or browser compatibility.

On November 12, a fresh copy of all five public pages and three artwork assets passed static checks, the full 24-test suite, and packaging. Every staged page and asset was byte-identical to its source. Embedded CSS literal image URLs were included in validation.

## Observed live browser checks
| Check | Evidence and scope |
| --- | --- |
| Desktop homepage rendering | Scrapbook artwork visibly loaded in Chrome on November 11. |
| Linked pages | Followed homepage to Arabic, Arabic to Privacy, Privacy back home, and home to Funding Transparency on November 11. |
| Homepage keyboard skip | Tab reached skip link first; Enter focused details; next Tab reached footer Editorial & safety on November 11. |
| Arabic keyboard skip | On November 12, Tab reached skip first and Enter focused main including the heading and introduction; desktop view showed no obvious clipping. |
| Funding keyboard skip | Tab reached skip link first; Enter focused main; next Tab reached footer Home on November 12. |

These observations used a remote desktop browser, not physical phones or a running screen reader.

On November 12, live Chrome DOM inspection confirmed `meta[name="referrer"]` has content `no-referrer` on Privacy, Editorial & Safety, and Funding Transparency. No outbound header capture was performed.

On November 12, after the execution environment recovered, a fresh 26-test regression run passed. All five current HTML pages also passed parser-level main/heading containment and safety checks. This pass did not rerun full asset packaging.

## Open verification work
- Mobile and tablet browser interaction, narrow widths, zoom and text enlargement.
- VoiceOver and TalkBack with real assistive technology.
- Arabic review by a qualified speaker.
- Current visual comparison against Denise's selected reference; successful loading is not proof of exact design fidelity.
- Network-level verification of referrer headers; DOM metadata alone does not prove every outbound request.
- Full keyboard traversal, focus visibility, back/forward behavior and broken-image recovery.
- Fresh checks after any later source change.

## Boundaries
Preserve the selected design, wording and typography. Keep fictional imagery and quotations labeled. Do not open story submissions or payments through this verification work. Do not alter DNS, domain or hosting settings. GitHub Pages at peopleforgaza.org is the current user-selected hosting; the linked VIII Site project is unrelated and must not be used for this project.

## Custom-domain packaging regression — November 12, 2026
The package helper previously omitted the repository's existing CNAME file. A regression reproduced the missing output before the fix. The helper now copies that file byte-for-byte when present and rejects symlinks, cleaning staged output on failure. Both new regressions pass alongside the existing suite (28 tests total). Tests also retain the existing no-CNAME behavior. This changes packaging only; DNS, CNAME source, hosting settings, public pages and design were not changed. A full current-assets package and live deployment were not exercised in this pass.

## Full package verification — November 12, 2026
Fetched the current five HTML pages, three WebP artwork assets, CNAME, checker, builder and regression tests from GitHub. Static validation, all 28 tests and a fresh package build passed. All nine packaged files (five pages, three assets and CNAME) were byte-identical to the fetched source. This closes the prior full-package verification gap for the custom-domain fix. No hosting settings or live deployment were changed or tested in this pass; mobile, assistive-technology and translation review remain open.

## Offline calculator checks — November 12, 2026
Run `node --test tests/payment-calculator.test.mjs` from the repository root with Node.js 18 or newer, in addition to the Python checks. No npm installation, credentials or network access is required. Three calculator tests passed on Node.js 24.22.1; the existing 28 Python tests also passed in this verification pass. The calculator tests cover normal allocation, integer rounding (including the reproduced large-input one-cent error), allocation conservation and rejected inputs/fees. Node.js 18 compatibility was not executed. These are offline preparation checks, not checkout, provider, webhook or payout tests. Payments remain disabled and no launch approval is implied.
