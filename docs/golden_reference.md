# Golden Reference Verification

The golden reference is used to verify that the test station is healthy before DUT testing.

## Verification frequency

Station verification is performed **once per calendar day**, not before every DUT.

At the beginning of each sequence run, TestStand checks the stored date and result of the most recent station verification.

- If the station already passed verification today, TestStand reuses that result and DUT testing may begin.
- If there is no successful verification for today, the golden-reference verification must run.
- If the daily verification fails, `StationVerified = False` and DUT testing is blocked until a successful verification is completed.

Expected rule:

`Successful verification today -> StationVerified = True -> DUT tests may run`

`No successful verification today -> Run Golden Reference Verification`

`Reference verification FAIL -> StationVerified = False -> DUT tests are blocked -> Cleanup`

The reference emulator can inject failures independently from DUT failures so the future TestStand sequence can validate this station-gating logic.
