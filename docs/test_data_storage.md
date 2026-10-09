# Test Data Storage

## Goal

Every completed DUT test must leave a traceable record showing:

- test date and time
- DUT serial number
- station ID
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

Runtime data is stored by calendar date:

```text
test_data/
└── YYYY-MM-DD/
    └── <SERIAL_NUMBER>_<STATION_ID>.json
```

Example:

```text
test_data/
└── 2026-10-09/
    └── PC05-00124_TS-EMU-01.json
```

If the same serial number is tested more than once on the same station during
the same day, a new entry is appended to the `runs` array instead of
overwriting the previous result.

## Example record

```json
{
  "date": "2026-10-09",
  "serial_number": "PC05-00124",
  "station_id": "TS-EMU-01",
  "runs": [
    {
      "run_id": "20261009T115300123456",
      "timestamp": "2026-10-09T11:53:00-07:00",
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
  ]
}
```

## TestStand responsibility

The future TestStand sequence will collect each step result during execution and
write one completed run to this storage after the test reaches Cleanup.

The Python storage module only persists the result. TestStand remains
responsible for deciding PASS, FAIL, SKIP, RETEST, and the final sequence
result.

## Git policy

Actual runtime result JSON files are ignored by Git because they are generated
test data rather than source code. The storage format and code are versioned in
the repository.
