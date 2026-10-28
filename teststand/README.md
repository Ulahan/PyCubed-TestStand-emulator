# NI TestStand Integration Blueprint

The software side of the project is complete. The remaining native artifact is the `.seq` file, which must be created with NI TestStand Sequence Editor during the planned trial; a `.seq` file is not a text placeholder.

## Sequence groups

### Setup
- Require Operator ID for every DUT run.
- Read Station ID.
- Reuse Golden Reference only within the same station boot session and for at most 12 hours.
- Reverify after station reboot, 12 hours, suspected malfunction, or fixture/test-equipment repair/replacement.
- Block DUT testing if Golden Reference verification fails.
- Require DUT serial number.

### Main
Implement the 17 steps in `config/PyCubed_Test_Plan_FINAL.json` in order. Use Python Adapter calls into `emulator/pycubed_emulator.py`.

### Cleanup
Always execute cleanup: DUT power off, loads/sources safe, resources released, and one timestamped JSON result saved.

## TestStand result logic
- Any required test FAIL => overall FAIL.
- SKIP is allowed only for dependent steps after an upstream hard failure; it never converts the DUT to PASS.
- RETEST is allowed only where explicitly defined and every attempt must be logged.
- Test 17 Final Flight Firmware Verification must PASS before the DUT can receive overall PASS.

For pre-trial validation, run:

`python -m emulator.sequence_runner --operator OP-001`
