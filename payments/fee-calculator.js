// Offline illustration only. No payment collection or banking connections.
// Amounts are integer cents to avoid floating point errors.
export function donationBreakdown(amountCents, processorFeeCents = 0) {
  if (!Number.isSafeInteger(amountCents) || amountCents <= 0) throw new RangeError('Positive integer cents required');
  if (!Number.isSafeInteger(processorFeeCents) || processorFeeCents < 0) throw new RangeError('Nonnegative integer processor fee required');
  const platformFeeCents = Number((BigInt(amountCents) + 10n) / 20n);
  const beneficiaryAllocationCents = amountCents - platformFeeCents;
  if (processorFeeCents > beneficiaryAllocationCents) throw new RangeError('Fees exceed beneficiary allocation');
  return {amountCents, platformFeeCents, beneficiaryAllocationCents, processorFeeCents, estimatedBeneficiaryNetCents:beneficiaryAllocationCents - processorFeeCents};
}
