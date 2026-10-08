# PyCubed TestStand Emulator

Software-only NI TestStand training project based on a PyCubed v0.5 CubeSat avionics test workflow.

The project separates responsibilities intentionally:

- **Python emulator** simulates the DUT and the golden-reference responses.
- **NI TestStand** owns test flow, limits, PASS/FAIL, SKIP, RETEST, station verification, cleanup, and reporting.

No physical hardware is required.

## Planned Test Flow

1. Initialize emulator
2. Capture operator ID and station ID
3. Load / verify golden reference
4. Set `StationVerified = True` only after reference checks pass
5. Load DUT serial number
6. Power-on test
7. 3.3 V rail test
8. Boot test
9. IMU test
10. Battery test
11. Apply PASS / FAIL / SKIP / RETEST logic in TestStand
12. Cleanup and report

## Emulator modes

DUT modes:

- `NORMAL`
- `POWER_FAILURE`
- `RAIL_FAILURE`
- `BOOT_FAILURE`
- `IMU_FAILURE`
- `BATTERY_FAILURE`
- `INTERMITTENT_IMU`

Reference modes:

- `REFERENCE_NORMAL`
- `REFERENCE_POWER_FAILURE`
- `REFERENCE_RAIL_FAILURE`
- `REFERENCE_BOOT_FAILURE`
- `REFERENCE_SENSOR_FAILURE`

## Repository layout

```text
emulator/   Python DUT/reference emulator
config/     Test and emulator configuration
scripts/    Windows helper scripts
 teststand/  Notes for the future .seq implementation
 docs/       Architecture and flow documentation
 tests/      Python unit tests
```

## Current status

The emulator scaffold is ready for integration. The TestStand sequence will be created during the NI TestStand trial after the software-only side is prepared and verified.
