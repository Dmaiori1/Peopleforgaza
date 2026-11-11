# People for Gaza — payment integration readiness (not live)

Status: **BLOCKED pending payment-provider approval and legal/compliance review**. Do not accept payments or collect bank details through GitHub Pages.

## Proposed economics
- Platform fee: **5% of each contribution** (provisional, subject to review).
- Beneficiary allocation: **95% before processor, transfer, currency-conversion, refund, and chargeback costs**.
- Display a donor-facing breakdown showing exactly which party bears each fee, and the estimated beneficiary net amount. Do not promise 95% net delivery until fees are accounted for.
- Operator is not yet verified as a registered charity; do not describe contributions as tax-deductible.
- Keep a ledger for each contribution, campaign, fee, refund, and confirmed beneficiary payout.

## Required approval
- Seek written approval from a provider for a US-based, for-profit crowdfunding platform featuring third-party Gaza family campaigns, a 5% platform fee, personal-account payouts initially proposed, and possible cross-border distributions.
- Stripe's published rules classify crowdfunding platforms as restricted and prohibit unsupported peer-to-peer transmission. Do not open a standard donation checkout or route family donations into an undisclosed personal account.
- Obtain qualified advice on business formation, charitable solicitation, money transmission, sanctions/AML screening, tax treatment, and cross-border payout options.
- Prefer dedicated operator accounts and compliant connected-recipient or partner payout flows once approved.

## Implementation after approval
1. Server-side application/API and secrets management (GitHub Pages alone cannot safely process payment secrets).
2. Approved payment provider's hosted checkout or embedded components.
3. Immutable donation/campaign IDs, signed webhook verification, idempotent accounting, refunds/disputes, and reconciliation.
4. Consent-based family onboarding, verification and safeguarding, private payout information storage, restricted admin access.
5. Transparent 5% fee disclosure, actual processing fees, refund policy, donor receipts, and campaign statuses.
6. Sandbox testing, independent security review, and only then live enablement.

## Design lock
Do not modify the approved homepage layout, copy, typography, colors, artwork, domain, DNS, or GitHub Pages hosting as part of this planning document.

References:
- https://stripe.com/legal/restricted-businesses
- https://support.stripe.com/questions/requirements-for-accepting-tips-or-donations
