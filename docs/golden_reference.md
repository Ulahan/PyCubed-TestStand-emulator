# Golden Reference Verification

The setup phase verifies the test station before a DUT is tested.

The reference emulator can inject failures independently from DUT failures so the future TestStand sequence can validate station gating logic.

Expected rule:

`Reference verification PASS -> StationVerified = True -> DUT tests may run`

`Reference verification FAIL -> StationVerified = False -> DUT tests are blocked -> Cleanup`
