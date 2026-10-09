# Planned TestStand Sequence Flow

```text
SETUP
  |
  +--> Initialize Emulator
  +--> Get Operator ID
  +--> Get Station ID
  +--> Read Last Station Verification
  |
  +--> Successful verification already completed today?
          |
          +--> YES --> StationVerified = True
          |              |
          |              v
          |            MAIN
          |
          +--> NO --> Load Golden Reference
                       +--> Verify Reference Power
                       +--> Verify Reference 3.3 V
                       +--> Verify Reference Boot
                       +--> Verify Reference Sensor
                       |
                       +--> Reference PASS ?
                               |
                               +--> YES
                               |     +--> Save today's successful verification
                               |     +--> StationVerified = True
                               |     +--> MAIN
                               |
                               +--> NO
                                     +--> StationVerified = False
                                     +--> Block DUT testing
                                     +--> CLEANUP

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
  +--> Unload Golden Reference if loaded
  +--> Emulator Cleanup
  +--> Report
```

The successful station-verification result must persist between DUT runs so the golden reference is not repeated for every unit on the same calendar day.
