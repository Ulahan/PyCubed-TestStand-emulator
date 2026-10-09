# Test Data

This directory is the runtime root for local test-result files.

The application creates one date directory automatically:

```text
YYYY-MM-DD/
```

Inside it, each DUT/station pair is stored as:

```text
<SERIAL_NUMBER>_<STATION_ID>.json
```

Example:

```text
2026-10-09/PC05-00124_TS-EMU-01.json
```

Repeated tests of the same DUT on the same station and date are appended as
separate entries in the file's `runs` array.

Generated date folders are excluded from Git.
