# System Architecture

```text
NI TestStand Sequence Editor (planned native .seq)
              |
              | Python Adapter
              v
      pycubed_emulator.py
              |
      +-------+--------+------------------+
      |                |                  |
Golden Reference   DUT interfaces    Fault injection
      |                |                  |
      +----------------+------------------+
                       |
              timestamped JSON results
```

## Software-only validation path

Until the NI TestStand trial is activated, `emulator/sequence_runner.py` executes the same 17-test blueprint in Python. This validates emulator behavior, fault injection, retest, cleanup, and result storage before a native `.seq` is created.

## Responsibility split

**Python emulator** simulates device measurements, buses, charger states, watchdog behavior, GPS/radio interfaces, and deterministic failures.

**NI TestStand** will own operator prompts, sequence flow, limits, PASS/FAIL/SKIP/RETEST, Golden Reference validity, cleanup, and production reporting.

The project does not claim physical RF, GNSS acquisition, charging-current accuracy, or other hardware performance that would require calibrated fixtures or RF/GNSS equipment.
