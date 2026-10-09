# Test Data Storage

## Goal

Every completed DUT test leaves one traceable JSON record showing:

- DUT serial number
- station ID
- test date and time
- operator ID
- whether the station had a valid daily verification
- every executed test step
- measured value
- engineering unit
- limits when applicable
- PASS / FAIL / SKIP result
- RETEST attempt number
- overall test result

## File organization

All result files are stored directly in one folder:

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

There are no date subfolders. Every test run creates a new file.

If the same board is tested again, the previous file is never overwritten.
The new result gets a new timestamp in its filename, so the test history can
be reconstructed simply by sorting the files by time.

## Example record

```json
{
  "serial_number": "PC05-00124",
  "station_id": "TS-EMU-01",
  "test_date": "2026-10-09",
  "test_time": "11:53:00",
  "timestamp": "2026-10-09T11:53:00.123456-07:00",
  "operator_id": "OP-TRAINING",
  "station_verified": true,
  "station_verification_date": "2026-10-09",
  "overall_result": "PASS",
  "steps": [
    {
      "step_name": "Power On",
      "status": "PASS",
      "measured_value": true,
      "unit": null,
      "limits": null,
      "attempt": 1
    },
    {
      "step_name": "3.3 V Rail",
      "status": "PASS",
      "measured_value": 3.3,
      "unit": "V",
      "limits": {
        "min": 3.2,
        "max": 3.4
      },
      "attempt": 1
    },
    {
      "step_name": "IMU Test",
      "status": "FAIL",
      "measured_value": false,
      "unit": null,
      "limits": null,
      "attempt": 1
    },
    {
      "step_name": "IMU Test",
      "status": "PASS",
      "measured_value": true,
      "unit": null,
      "limits": null,
      "attempt": 2
    }
  ]
}
```

## TestStand responsibility

The future TestStand sequence will collect each step result during execution.
When the sequence reaches Cleanup, it writes one complete result file for that
specific test run.

Python only persists the result. TestStand remains responsible for deciding
PASS, FAIL, SKIP, RETEST, and the final sequence result.

## Git policy

Runtime JSON result files are ignored by Git because they are generated test
data rather than source code. The storage code and data format are versioned
in the repository.
