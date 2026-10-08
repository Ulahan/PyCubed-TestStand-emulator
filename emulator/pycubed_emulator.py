"""PyCubed v0.5 TestStand software emulator.

Python emulates DUT and golden-reference responses.
TestStand owns sequence flow, limits, PASS/FAIL, SKIP, RETEST,
StationVerified, cleanup, and reporting.
"""

SERIAL_NUMBER = "PC05-00124"
STATION_ID = "TS-EMU-01"

VALID_DUT_MODES = {
    "NORMAL",
    "POWER_FAILURE",
    "RAIL_FAILURE",
    "BOOT_FAILURE",
    "IMU_FAILURE",
    "BATTERY_FAILURE",
    "INTERMITTENT_IMU",
}

VALID_REFERENCE_MODES = {
    "REFERENCE_NORMAL",
    "REFERENCE_POWER_FAILURE",
    "REFERENCE_RAIL_FAILURE",
    "REFERENCE_BOOT_FAILURE",
    "REFERENCE_SENSOR_FAILURE",
}

_state = {
    "dut_mode": "NORMAL",
    "reference_mode": "REFERENCE_NORMAL",
    "powered": False,
    "reference_loaded": False,
    "imu_attempt": 0,
}


def initialize_emulator():
    """Reset runtime state while preserving selected fault modes."""
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
    if _state["reference_mode"] == "REFERENCE_RAIL_FAILURE":
        return 2.70
    return 3.30


def verify_reference_boot():
    _require_reference()
    return _state["reference_mode"] != "REFERENCE_BOOT_FAILURE"


def verify_reference_sensor():
    _require_reference()
    return _state["reference_mode"] != "REFERENCE_SENSOR_FAILURE"


def unload_reference():
    _state["reference_loaded"] = False
    return True


def power_on():
    if _state["dut_mode"] == "POWER_FAILURE":
        _state["powered"] = False
        return False
    _state["powered"] = True
    return True


def read_3v3():
    _require_power()
    if _state["dut_mode"] == "RAIL_FAILURE":
        return 2.75
    return 3.30


def test_boot():
    _require_power()
    return _state["dut_mode"] != "BOOT_FAILURE"


def test_imu():
    _require_power()
    _state["imu_attempt"] += 1

    if _state["dut_mode"] == "IMU_FAILURE":
        return False

    if _state["dut_mode"] == "INTERMITTENT_IMU":
        return _state["imu_attempt"] >= 2

    return True


def read_battery():
    _require_power()
    if _state["dut_mode"] == "BATTERY_FAILURE":
        return 2.90
    return 3.95


def power_off():
    _state["powered"] = False
    return True


def cleanup():
    """Return emulator to a safe runtime state.

    TestStand still owns the Cleanup group and reporting logic.
    """
    _state["powered"] = False
    _state["reference_loaded"] = False
    return True


def get_state():
    """Return a copy for diagnostics/tests."""
    return dict(_state)


def _require_power():
    if not _state["powered"]:
        raise RuntimeError("DUT is not powered on")


def _require_reference():
    if not _state["reference_loaded"]:
        raise RuntimeError("Golden reference is not loaded")
