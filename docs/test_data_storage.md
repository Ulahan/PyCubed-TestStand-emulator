# Test Data Storage

Every completed DUT run creates one traceable JSON record containing:

- DUT serial number;
- station ID;
- operator ID;
- timestamp;
- Golden Reference verification status/time;
- every executed step;
- measured values and units;
- limits when applicable;
- PASS / FAIL / SKIP status;
- RETEST attempt number;
- overall result.

## File organization

All results are stored directly in:

```text
test_data/
```

Filename format:

```text
<SERIAL_NUMBER>_<STATION_ID>_<YYYYMMDD>_<HHMMSS>_<MICROSECONDS>.json
```

There are no date subfolders. A repeated test of the same serial number creates a new timestamped file and never overwrites previous history.

## Responsibility

The final NI TestStand implementation will decide PASS, FAIL, SKIP, RETEST, and overall result. Python provides the DUT emulator plus the JSON persistence helper.

The included software sequence runner uses the same storage format for pre-TestStand validation.

## Git policy

Runtime JSON files are generated data and are ignored by Git. The storage code and schema are versioned.
