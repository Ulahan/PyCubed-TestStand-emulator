# Final TestStand Sequence Flow

```text
SETUP
  |
  +--> Initialize Python emulator / fixture interfaces
  +--> Require Operator ID
  +--> Read Station ID
  +--> Check Golden Reference verification state
  |      +--> same boot session AND age <= 12 h ? --> reuse
  |      +--> otherwise --> verify Golden Reference
  |             +--> FAIL --> block DUT tests --> CLEANUP
  |
  +--> Require DUT Serial Number
  v
MAIN
  |
  +--> 01 Safe Power-Up / Overcurrent
  +--> 02 3.3 V Rail
  +--> 03 MCU Detection / SWD
  +--> 04 Internal Flash / Software Verification
  +--> 05 MRAM Read/Write
  +--> 06 microSD Provisioning / Verification
  +--> 07 BMX160 IMU (one transient retest allowed)
  +--> 08 ADM1176 Current 125 / 250 / 500 mA
  +--> 09 External Watchdog Recovery
  +--> 10 USB Data & USB Power
  +--> 11 ADM1176 VBATT at 7.4 / 8.4 V
  +--> 12 ADM1176 Overcurrent Protection / Auto-Retry
  +--> 13 BQ25883 USB Charger
  +--> 14 LTC4121 Solar Charger
  +--> 15 GPS UART / message / 1PPS
  +--> 16 RFM9x Radio SPI / packet loopback
  +--> 17 Final Flight Firmware Verification
  |
  +--> Any required FAIL => overall FAIL
  +--> Upstream hard FAIL may SKIP dependent steps; skipped steps are logged
  v
CLEANUP (always)
  +--> Power OFF DUT
  +--> Return electronic load / USB / solar source to safe state
  +--> Release emulator / fixture resources
  +--> Save one timestamped JSON result
  +--> Final report
```

Operator change does not invalidate a valid Golden Reference verification. A station/PC reboot does.
