# PyCubed TestStand Emulator

Software-only NI TestStand training project based on a PyCubed v0.5 CubeSat avionics test workflow.

The project separates responsibilities intentionally:

- **Python emulator** simulates the DUT and the golden-reference responses.
- **NI TestStand** owns test flow, limits, PASS/FAIL, SKIP, RETEST, daily station verification, cleanup, reporting, and collection of test results.
- **Test data storage** keeps one timestamped result file for every completed test run.

No physical hardware is required.

## Planned Test Flow

1. Initialize emulator
2. Capture operator ID and station ID
3. Check whether the station already passed verification today
4. If needed, load / verify the golden reference
5. Set `StationVerified = True` only after a successful verification for the current day
6. Load DUT serial number
7. Power-on test
8. 3.3 V rail test
9. Boot test
10. IMU test
11. Battery test
12. Apply PASS / FAIL / SKIP / RETEST logic in TestStand
13. Save tested steps, measured values, and final result
14. Cleanup and report

## Test data

All runtime test records are stored in one directory:

```text
test_data/
├── PC05-00124_TS-EMU-01_20261009_115300_123456.json
├── PC05-00124_TS-EMU-01_20261009_142700_654321.json
└── PC05-00125_TS-EMU-01_20261009_143105_101010.json
```

Filename format:

```text
<SERIAL_NUMBER>_<STATION_ID>_<YYYYMMDD>_<HHMMSS>_<MICROSECONDS>.json
```

Every test run creates a separate file. If the same unit is tested multiple
times, its history is visible directly from the timestamps. No date subfolders
are created.

Each executed step records its status, measured value, unit, limits, and
attempt number.

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
emulator/   Python DUT/reference emulator and data-storage helpers
config/     Test and emulator configuration
scripts/    Windows helper scripts
teststand/  Notes for the future .seq implementation
docs/       Architecture, flow, and data-format documentation
tests/      Python unit tests
test_data/  Single runtime folder for timestamped test-result files
```

## Current status

The emulator scaffold and timestamped local JSON test-data storage are ready
for integration. The TestStand sequence will be created during the NI
TestStand trial after the software-only side is prepared and verified.
