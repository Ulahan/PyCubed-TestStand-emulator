# Planned TestStand Sequence Flow

```text
SETUP
  |
  +--> Initialize Emulator
  +--> Get Operator ID
  +--> Get Station ID
  +--> Load Golden Reference
  +--> Verify Reference Power
  +--> Verify Reference 3.3 V
  +--> Verify Reference Boot
  +--> Verify Reference Sensor
  |
  +--> Reference PASS ?
          | YES
          v
     StationVerified = True
          |
          v
MAIN
  |
  +--> Get DUT Serial Number
  +--> Power On
  +--> Read 3.3 V
  +--> Boot Test
  +--> IMU Test
  |      |
  |      +--> FAIL -> RETEST allowed -> second attempt
  |
  +--> Battery Test
  |
  +--> PASS / FAIL / SKIP decisions in TestStand
  |
  v
CLEANUP
  +--> Power Off
  +--> Unload Golden Reference
  +--> Emulator Cleanup
  +--> Report
```

If golden-reference verification fails, `StationVerified` remains false and DUT testing must not proceed.
