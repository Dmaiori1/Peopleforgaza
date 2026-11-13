// Run: node --test tests/payment-calculator.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const source = await readFile(new URL('../payments/fee-calculator.js', import.meta.url), 'utf8');
const {donationBreakdown} = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
test('ordinary allocation accounts for processor fees', () => {
  assert.deepEqual(donationBreakdown(10000, 320), {amountCents:10000, platformFeeCents:500, beneficiaryAllocationCents:9500, processorFeeCents:320, estimatedBeneficiaryNetCents:9180});
});
test('cent rounding and allocation conservation', () => {
  for (const [amount, fee] of [[1,0],[9,0],[10,1],[11,1],[29,1],[30,2],[9007199254740969,450359962737048]]) {
    const result = donationBreakdown(amount);
    assert.equal(result.platformFeeCents, fee);
    assert.equal(result.platformFeeCents + result.beneficiaryAllocationCents, amount);
  }
});
test('invalid amounts and excessive fees are rejected', () => {
  for (const amount of [0,-1,1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1,'100']) assert.throws(() => donationBreakdown(amount), RangeError);
  for (const fee of [-1,1.5,NaN,Infinity,'1',96]) assert.throws(() => donationBreakdown(100,fee), RangeError);
  assert.equal(donationBreakdown(100,95).estimatedBeneficiaryNetCents,0);
});

test('preparation configuration keeps payment collection disabled', async () => {
  const config = JSON.parse(await readFile(new URL('../payments/config.example.json', import.meta.url), 'utf8'));
  assert.equal(config.status, 'disabled');
  assert.equal(config.provider, 'unselected');
  assert.equal(config.checkout_enabled, false);
  assert.equal(config.payouts_enabled, false);
  assert.equal(config.requires_provider_approval, true);
  assert.equal(config.requires_legal_review, true);
  assert.equal(config.platform_fee_basis_points, 500);
  assert.equal(config.beneficiary_share_basis_points, 9500);
});
