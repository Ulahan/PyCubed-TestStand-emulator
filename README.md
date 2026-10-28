# PyCubed v0.5 TestStand Emulator

Software-only manufacturing-test project for a **PyCubed v0.5 CubeSat avionics board**, designed to be implemented in **NI TestStand** with Python Adapter calls.

The pre-TestStand software phase is complete: the repository now contains the final 17-test plan, deterministic DUT/golden-reference emulator, fault injection, a runnable Python mirror of the future TestStand sequence, timestamped JSON reporting, unit tests, and the NI TestStand implementation blueprint.

No physical hardware is required for the current validation stage.

## Final test sequence

1. Safe Power-Up / Overcurrent
2. 3.3 V Rail
3. MCU Detection / SWD
4. Internal Flash / Software Verification
5. MRAM Read/Write
6. microSD Provisioning / Verification
7. BMX160 IMU Functional Test
8. ADM1176 Current Measurement — 125 / 250 / 500 mA
9. External Watchdog Recovery
10. USB Data & USB Power
11. ADM1176 VBATT Measurement — 7.4 / 8.4 V
12. ADM1176 Overcurrent Protection / Auto-Retry
13. BQ25883 USB Battery Charger
14. LTC4121 Solar Charger
15. GPS Functional Test — UART / message / 1PPS
16. RFM9x Radio Functional Test — SPI / packet loopback
17. Final Flight Firmware Verification

Full definitions: `config/PyCubed_Test_Plan_FINAL.json`.

## Golden Reference policy

Golden Reference verification is reusable for **up to 12 hours only within the same station boot session**.

Reverify after station reboot, 12 hours, suspected malfunction, or fixture/test-equipment repair/replacement. Operator change alone does not require reverification.

## Run the complete software sequence

From the repository root:

```bash
python -m emulator.sequence_runner --operator OP-001 --serial PC05-00124
```

Fault-injection example:

```bash
python -m emulator.sequence_runner --operator OP-001 --fault RADIO_FAILURE
```

Windows helper:

```text
scripts\RUN_EMULATOR.bat OP-001 PC05-00124
```

Each completed run writes a separate JSON file to `test_data/`.

## Verify the software

```bash
python -m unittest discover -s tests -v
```

The final software validation currently covers 10 unit/integration tests including the complete normal sequence and fault propagation.

## Repository layout

```text
config/     Final test plan and station/test configuration
emulator/   DUT/reference emulator, sequence runner, result storage
docs/       Architecture, Golden Reference, sequence flow, validation
scripts/    Windows run/verification helpers
tests/      Unit and integration tests
teststand/  NI TestStand implementation blueprint
test_data/  Runtime timestamped JSON results
```

## NI TestStand status

The project is **TestStand-ready**, but a native binary `.seq` file is intentionally not fabricated here. It must be created/edited with **NI TestStand Sequence Editor** during the planned trial.

The sequence blueprint is already defined as **Setup → Main → Cleanup**, with PASS/FAIL/SKIP/RETEST logic, Golden Reference gating, 17 DUT tests, final firmware verification, cleanup, and result reporting.

## Scope limits

This is a software-only training/portfolio implementation. Values explicitly marked as project/simulation limits are not claimed as official PyCubed manufacturing limits.

The project also does not claim calibrated RF transmit power/sensitivity, antenna performance, real GNSS satellite acquisition, or production charger characterization without appropriate physical fixtures and test equipment.
