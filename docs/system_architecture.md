# System Architecture

```text
NI TestStand
    |
    | Python Adapter calls
    v
pycubed_emulator.py
    |
    +-- Golden Reference responses
    +-- DUT responses
    +-- Fault modes
```

## Responsibility split

### Python
- Simulate hardware behavior
- Return measurements / booleans
- Maintain minimal emulator runtime state
- Inject deterministic faults for training

### TestStand
- Sequence control
- Operator ID / station ID handling
- Golden-reference verification workflow
- `StationVerified` logic
- Test limits
- PASS / FAIL
- SKIP
- RETEST
- Cleanup group
- Final report
