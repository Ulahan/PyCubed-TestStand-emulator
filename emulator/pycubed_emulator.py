"""PyCubed v0.5 software DUT and golden-reference emulator.

The emulator returns deterministic measurements and interface results.
NI TestStand (or the included Python sequence runner) owns sequence flow,
limits, PASS/FAIL/SKIP/RETEST, cleanup, and reporting.
"""

from __future__ import annotations

SERIAL_NUMBER = "PC05-00124"
STATION_ID = "TS-EMU-01"

VALID_DUT_MODES = {
    "NORMAL", "POWER_FAILURE", "RAIL_FAILURE", "MCU_FAILURE",
    "SOFTWARE_FAILURE", "MRAM_FAILURE", "SD_FAILURE", "IMU_FAILURE",
    "INTERMITTENT_IMU", "CURRENT_MONITOR_FAILURE", "WATCHDOG_FAILURE",
    "USB_DATA_FAILURE", "USB_POWER_FAILURE", "VBATT_MONITOR_FAILURE",
    "OVERCURRENT_PROTECTION_FAILURE", "USB_CHARGER_FAILURE",
    "SOLAR_CHARGER_FAILURE", "GPS_FAILURE", "RADIO_FAILURE",
    "FINAL_FIRMWARE_FAILURE",
}

VALID_REFERENCE_MODES = {
    "REFERENCE_NORMAL", "REFERENCE_POWER_FAILURE", "REFERENCE_RAIL_FAILURE",
    "REFERENCE_BOOT_FAILURE", "REFERENCE_SENSOR_FAILURE",
}

_state = {
    "dut_mode": "NORMAL",
    "reference_mode": "REFERENCE_NORMAL",
    "powered": False,
    "reference_loaded": False,
    "imu_attempt": 0,
}


def initialize_emulator():
    _state["powered"] = False
    _state["reference_loaded"] = False
    _state["imu_attempt"] = 0
    return True


def set_fault_mode(mode):
    mode = str(mode).strip().upper()
    if mode not in VALID_DUT_MODES:
        raise ValueError(f"Unsupported DUT mode: {mode}")
    _state["dut_mode"] = mode
    _state["imu_attempt"] = 0
    return mode


def set_reference_mode(mode):
    mode = str(mode).strip().upper()
    if mode not in VALID_REFERENCE_MODES:
        raise ValueError(f"Unsupported reference mode: {mode}")
    _state["reference_mode"] = mode
    return mode


def get_serial_number():
    return SERIAL_NUMBER


def get_station_id():
    return STATION_ID


def load_reference():
    _state["reference_loaded"] = True
    return True


def verify_reference_power():
    _require_reference()
    return _state["reference_mode"] != "REFERENCE_POWER_FAILURE"


def read_reference_3v3():
    _require_reference()
    return 2.70 if _state["reference_mode"] == "REFERENCE_RAIL_FAILURE" else 3.30


def verify_reference_boot():
    _require_reference()
    return _state["reference_mode"] != "REFERENCE_BOOT_FAILURE"


def verify_reference_sensor():
    _require_reference()
    return _state["reference_mode"] != "REFERENCE_SENSOR_FAILURE"


def unload_reference():
    _state["reference_loaded"] = False
    return True


def safe_power_up(vbatt_v=7.4):
    if _state["dut_mode"] == "POWER_FAILURE":
        _state["powered"] = False
        return {"powered": False, "vbatt_v": 0.0, "current_a": 0.0, "current_limit": True}
    _state["powered"] = True
    return {"powered": True, "vbatt_v": float(vbatt_v), "current_a": 0.030, "current_limit": False}


def power_on():
    return bool(safe_power_up()["powered"])


def read_3v3():
    _require_power()
    return 2.75 if _state["dut_mode"] == "RAIL_FAILURE" else 3.30


def detect_mcu():
    _require_power()
    return {"detected": _state["dut_mode"] != "MCU_FAILURE", "device": "ATSAMD51J19A"}


def verify_internal_software():
    _require_power()
    ok = _state["dut_mode"] != "SOFTWARE_FAILURE"
    return {
        "bootloader_version": "0.7.0" if ok else "unknown",
        "firmware_version": "test-1.0" if ok else "mismatch",
        "hash_ok": ok,
        "handshake": ok,
    }


def test_boot():
    _require_power()
    return _state["dut_mode"] not in {"SOFTWARE_FAILURE", "FINAL_FIRMWARE_FAILURE"}


def test_mram():
    _require_power()
    ok = _state["dut_mode"] != "MRAM_FAILURE"
    return {"write_ok": ok, "readback_ok": ok, "compare_ok": ok, "cleared": ok}


def test_microsd(new_board=True):
    _require_power()
    ok = _state["dut_mode"] != "SD_FAILURE"
    return {
        "detected": ok,
        "filesystem": "FAT32" if ok else None,
        "formatted": bool(new_board and ok),
        "write_read_compare": ok,
        "test_file_deleted": ok,
    }


def test_imu():
    _require_power()
    _state["imu_attempt"] += 1
    if _state["dut_mode"] == "IMU_FAILURE":
        return False
    if _state["dut_mode"] == "INTERMITTENT_IMU":
        return _state["imu_attempt"] >= 2
    return True


def test_imu_positions():
    ok = test_imu()
    return {
        "device_id_ok": ok,
        "position_0_ok": ok,
        "position_45_ok": ok,
        "gyro_motion_ok": ok,
        "mag_data_valid": ok,
    }


def read_adm1176_current(target_total_a):
    _require_power()
    target = float(target_total_a)
    measured = target * (0.80 if _state["dut_mode"] == "CURRENT_MONITOR_FAILURE" else 0.995)
    return {"fixture_current_a": target, "adm1176_current_a": measured}


def watchdog_recovery():
    _require_power()
    if _state["dut_mode"] == "WATCHDOG_FAILURE":
        return {"event_detected": False, "timeout_s": None, "communication_restored": False}
    return {"event_detected": True, "timeout_s": 1.60, "communication_restored": True}


def test_usb_data():
    _require_power()
    ok = _state["dut_mode"] != "USB_DATA_FAILURE"
    return {"enumerated": ok, "identity_ok": ok, "ping_pong": ok, "loopback_ok": ok}


def test_usb_power():
    ok = _state["dut_mode"] != "USB_POWER_FAILURE"
    return {"powered_from_usb": ok, "rail_3v3_v": 3.30 if ok else 0.0, "enumerated": ok, "ping_pong": ok}


def read_adm1176_voltage(fixture_voltage_v):
    _require_power()
    actual = float(fixture_voltage_v)
    measured = actual * (0.90 if _state["dut_mode"] == "VBATT_MONITOR_FAILURE" else 0.992)
    adc_code = round(measured * 4096 / 26.35)
    return {"fixture_voltage_v": actual, "adm1176_voltage_v": measured, "adc_code": adc_code}


def test_overcurrent_protection(normal_load_a=0.5, overload_request_a=1.2):
    _require_power()
    ok = _state["dut_mode"] != "OVERCURRENT_PROTECTION_FAILURE"
    return {
        "normal_stable": True,
        "normal_load_a": float(normal_load_a),
        "overload_request_a": float(overload_request_a),
        "measured_fault_current_a": 1.00 if ok else float(overload_request_a),
        "protection_event": ok,
        "output_off": ok,
        "auto_retry": ok,
        "recovered": ok,
    }


def test_usb_charger(battery_v=7.4):
    ok = _state["dut_mode"] != "USB_CHARGER_FAILURE"
    return {
        "i2c_ok": ok,
        "usb_input_v": 5.0,
        "battery_v": float(battery_v),
        "charging": ok,
        "chrg_stat": "FAST_CHARGE_CC" if float(battery_v) < 8.2 else "TAPER_OR_DONE",
        "charge_current_a": 0.80 if ok and float(battery_v) < 8.2 else 0.10 if ok else 0.0,
        "fault": not ok,
    }


def test_solar_charger(battery_v=7.4, solar_v=12.0):
    ok = _state["dut_mode"] != "SOLAR_CHARGER_FAILURE"
    return {
        "solar_input_v": float(solar_v),
        "battery_v": float(battery_v),
        "charging": ok,
        "chrg_active": ok,
        "charge_current_a": 0.35 if ok and float(battery_v) < 8.2 else 0.08 if ok else 0.0,
        "fault": not ok,
    }


def test_gps():
    _require_power()
    ok = _state["dut_mode"] != "GPS_FAILURE"
    return {
        "uart_ok": ok,
        "message_valid": ok,
        "pps_detected": ok,
        "fix_status": "SIMULATED_FIX" if ok else "NO_DATA",
    }


def test_radio():
    _require_power()
    ok = _state["dut_mode"] != "RADIO_FAILURE"
    return {"reset_ok": ok, "spi_ok": ok, "tx_packet_ok": ok, "rx_packet_ok": ok}


def verify_final_firmware():
    _require_power()
    ok = _state["dut_mode"] != "FINAL_FIRMWARE_FAILURE"
    return {
        "package_id": "PYCUBED-V05-FLIGHT-APPROVED",
        "bootloader_version": "0.7.0",
        "flight_firmware_version": "flight-1.0",
        "hash_ok": ok,
        "post_reset_handshake": ok,
        "test_firmware_active": False if ok else True,
    }


def read_battery():
    _require_power()
    return 6.50 if _state["dut_mode"] == "VBATT_MONITOR_FAILURE" else 7.40


def power_off():
    _state["powered"] = False
    return True


def cleanup():
    _state["powered"] = False
    _state["reference_loaded"] = False
    return True


def get_state():
    return dict(_state)


def _require_power():
    if not _state["powered"]:
        raise RuntimeError("DUT is not powered on")


def _require_reference():
    if not _state["reference_loaded"]:
        raise RuntimeError("Golden reference is not loaded")
