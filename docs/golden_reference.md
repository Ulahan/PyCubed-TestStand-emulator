# Golden Reference Verification

The Golden Reference verifies that the test station is healthy before DUT testing.

## Validity rule

A successful station verification is reusable only when **both** conditions remain true:

- the station is still in the **same boot session**;
- no more than **12 hours** have passed since the successful verification.

A change of operator does **not** invalidate station verification.

Reverification is required after:

- station/PC reboot;
- 12 hours since the last successful verification;
- suspected station malfunction;
- fixture or test-equipment repair/replacement.

If Golden Reference verification fails, `StationVerified = False`, DUT testing is blocked, and the sequence goes to Cleanup.

The reference emulator has independent failure modes so the TestStand gating logic can be tested separately from DUT failures.
