# Test Data

All runtime test-result files are stored directly in this directory.

One completed test run creates one JSON file:

```text
<SERIAL_NUMBER>_<STATION_ID>_<YYYYMMDD>_<HHMMSS>_<MICROSECONDS>.json
```

Example:

```text
PC05-00124_TS-EMU-01_20261009_115300_123456.json
```

If the same DUT is tested again, another file is created with a different
timestamp. Existing result files are not overwritten.

This allows repeated tests to be identified and ordered directly by time
without creating date subfolders.

Generated JSON files are excluded from Git.
