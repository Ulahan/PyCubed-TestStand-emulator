"""Executable software mirror of the planned NI TestStand sequence.

This runner demonstrates setup, Golden Reference verification, all defined
DUT tests, retest, cleanup, and timestamped JSON result storage without NI
TestStand.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from emulator import pycubed_emulator as emu
from emulator.test_data_store import build_step, save_test_run


class SequenceRunner:
    def __init__(self, operator_id: str, serial_number: str | None = None):
        if not operator_id.strip():
            raise ValueError("operator_id is required for every DUT run")
        self.operator_id = operator_id.strip()
        self.serial_number = serial_number or emu.get_serial_number()
        self.station_id = emu.get_station_id()
        self.steps = []
        self.station_verified = False
        self.station_verification_time = None
        self.hard_failure = False

    def _record(self, name, passed, value, unit=None, minimum=None, maximum=None, attempt=1):
        self.steps.append(build_step(
            name, "PASS" if passed else "FAIL", value,
            unit, minimum, maximum, attempt
        ))
        if not passed:
            self.hard_failure = True
        return passed

    def verify_station(self):
        emu.load_reference()
        checks = [
            ("Golden Reference Power", emu.verify_reference_power()),
            ("Golden Reference 3.3 V", 3.25 <= emu.read_reference_3v3() <= 3.35),
            ("Golden Reference Boot", emu.verify_reference_boot()),
            ("Golden Reference Sensor", emu.verify_reference_sensor()),
        ]
        for name, passed in checks:
            self.steps.append(build_step(name, "PASS" if passed else "FAIL", passed))
        self.station_verified = all(passed for _, passed in checks)
        if self.station_verified:
            self.station_verification_time = datetime.now(timezone.utc)
        emu.unload_reference()
        return self.station_verified

    def run(self):
        emu.initialize_emulator()
        try:
            if not self.verify_station():
                return self._finish("FAIL")

            power = emu.safe_power_up(7.4)
            self._record("01 Safe Power-Up", power["powered"] and not power["current_limit"], power)
            if self.hard_failure:
                return self._finish("FAIL")

            rail = emu.read_3v3()
            self._record("02 3.3 V Rail", 3.20 <= rail <= 3.40, rail, "V", 3.20, 3.40)

            mcu = emu.detect_mcu()
            self._record("03 MCU Detection / SWD", mcu["detected"], mcu)

            sw = emu.verify_internal_software()
            self._record("04 Internal Flash / Software", sw["hash_ok"] and sw["handshake"], sw)

            mram = emu.test_mram()
            self._record("05 MRAM Read/Write", mram["compare_ok"], mram)

            sd = emu.test_microsd(True)
            self._record("06 microSD", sd["write_read_compare"], sd)

            imu1 = emu.test_imu_positions()
            if imu1["device_id_ok"]:
                self._record("07 BMX160 IMU", True, imu1, attempt=1)
            else:
                self.steps.append(build_step("07 BMX160 IMU", "FAIL", imu1, attempt=1))
                imu2 = emu.test_imu_positions()
                self._record("07 BMX160 IMU", imu2["device_id_ok"], imu2, attempt=2)

            current_ok = True
            current_rows = []
            for target in (0.125, 0.250, 0.500):
                row = emu.read_adm1176_current(target)
                error = abs(row["adm1176_current_a"] - row["fixture_current_a"]) / row["fixture_current_a"] * 100
                row["error_percent"] = error
                current_ok &= error <= 6.0
                current_rows.append(row)
            self._record("08 ADM1176 Current", current_ok, current_rows)

            wd = emu.watchdog_recovery()
            wd_ok = (
                wd["event_detected"]
                and wd["timeout_s"] is not None
                and 1.0 <= wd["timeout_s"] <= 2.25
                and wd["communication_restored"]
            )
            self._record("09 Watchdog Recovery", wd_ok, wd)

            usb_data = emu.test_usb_data()
            usb_power = emu.test_usb_power()
            usb_ok = (
                all(usb_data.values())
                and usb_power["powered_from_usb"]
                and usb_power["enumerated"]
                and usb_power["ping_pong"]
                and 3.20 <= usb_power["rail_3v3_v"] <= 3.40
            )
            self._record("10 USB Data & Power", usb_ok, {"data": usb_data, "power": usb_power})

            vbatt_ok = True
            vbatt_rows = []
            for target in (7.4, 8.4):
                row = emu.read_adm1176_voltage(target)
                error = abs(row["adm1176_voltage_v"] - row["fixture_voltage_v"]) / row["fixture_voltage_v"] * 100
                row["error_percent"] = error
                vbatt_ok &= error <= 5.0
                vbatt_rows.append(row)
            self._record("11 ADM1176 VBATT Voltage", vbatt_ok, vbatt_rows)

            oc = emu.test_overcurrent_protection()
            oc_ok = all([
                oc["normal_stable"], oc["protection_event"], oc["output_off"],
                oc["auto_retry"], oc["recovered"]
            ])
            self._record("12 ADM1176 Overcurrent Protection", oc_ok, oc)

            usb_chg_low = emu.test_usb_charger(7.4)
            usb_chg_high = emu.test_usb_charger(8.4)
            usb_chg_ok = (
                usb_chg_low["i2c_ok"] and usb_chg_low["charging"]
                and not usb_chg_low["fault"]
                and usb_chg_high["chrg_stat"] == "TAPER_OR_DONE"
            )
            self._record("13 BQ25883 USB Charger", usb_chg_ok, {"7.4V": usb_chg_low, "8.4V": usb_chg_high})

            solar_low = emu.test_solar_charger(7.4, 12.0)
            solar_high = emu.test_solar_charger(8.4, 12.0)
            solar_ok = solar_low["charging"] and solar_low["chrg_active"] and not solar_low["fault"] and not solar_high["fault"]
            self._record("14 LTC4121 Solar Charger", solar_ok, {"7.4V": solar_low, "8.4V": solar_high})

            gps = emu.test_gps()
            self._record("15 GPS Functional", gps["uart_ok"] and gps["message_valid"] and gps["pps_detected"], gps)

            radio = emu.test_radio()
            self._record("16 RFM9x Radio Functional", all(radio.values()), radio)

            fw = emu.verify_final_firmware()
            fw_ok = fw["hash_ok"] and fw["post_reset_handshake"] and not fw["test_firmware_active"]
            self._record("17 Final Flight Firmware", fw_ok, fw)

            overall = "FAIL" if any(s["status"] == "FAIL" for s in self.steps) else "PASS"
            return self._finish(overall)
        finally:
            emu.cleanup()

    def _finish(self, overall_result):
        return save_test_run(
            serial_number=self.serial_number,
            station_id=self.station_id,
            operator_id=self.operator_id,
            steps=self.steps,
            overall_result=overall_result,
            station_verified=self.station_verified,
            station_verification_time=(
                self.station_verification_time.isoformat()
                if self.station_verification_time else None
            ),
        )


def main():
    parser = argparse.ArgumentParser(
        description="Run complete PyCubed software-emulated manufacturing sequence"
    )
    parser.add_argument("--operator", required=True, help="Operator badge/ID")
    parser.add_argument("--serial", default=None, help="DUT serial number")
    parser.add_argument("--fault", default="NORMAL", choices=sorted(emu.VALID_DUT_MODES))
    args = parser.parse_args()

    emu.set_fault_mode(args.fault)
    path = SequenceRunner(args.operator, args.serial).run()
    print(path)


if __name__ == "__main__":
    main()
