# Payments — preparation only

**Not live.** This directory contains offline fee math and a disabled configuration example. Nothing here collects money, banking details, or personal data. No changes to the public website or DNS are required.

Proposed 5% platform fee is represented by 500 basis points; 95% is allocated to the beneficiary fundraiser **before** processor and transfer fees. Fee incidence is undecided; do not claim beneficiaries receive 95% net. No funds may be collected before provider and legal approval.

The eventual integration will require a secure backend (GitHub Pages is static), an approved payment service, server-side checkout session creation, webhook signature verification, idempotency, reconciliation, refunds/disputes, beneficiary verification, and approved international payout rails. Never put API secret keys in this repository.

For readiness and compliance gates, see [payment-readiness](../docs/payment-readiness.md).

**Design lock:** Do not modify the homepage, images, colors, fonts, copy, Arabic page, privacy/editorial pages, domain, DNS, or hosting while preparing payments.
