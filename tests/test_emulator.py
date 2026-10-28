import unittest

from emulator import pycubed_emulator as emu


class TestPyCubedEmulator(unittest.TestCase):
    def setUp(self):
        emu.set_fault_mode("NORMAL")
        emu.set_reference_mode("REFERENCE_NORMAL")
        emu.initialize_emulator()

    def test_normal_dut_all_interfaces(self):
        self.assertTrue(emu.safe_power_up()["powered"])
        self.assertAlmostEqual(emu.read_3v3(), 3.30, places=2)
        self.assertTrue(emu.detect_mcu()["detected"])
        self.assertTrue(emu.verify_internal_software()["hash_ok"])
        self.assertTrue(emu.test_mram()["compare_ok"])
        self.assertTrue(emu.test_microsd()["write_read_compare"])
        self.assertTrue(emu.test_imu_positions()["device_id_ok"])
        self.assertTrue(emu.watchdog_recovery()["event_detected"])
        self.assertTrue(emu.test_usb_data()["enumerated"])
        self.assertTrue(emu.test_overcurrent_protection()["auto_retry"])
        self.assertTrue(emu.test_usb_charger()["i2c_ok"])
        self.assertTrue(emu.test_solar_charger()["charging"])
        self.assertTrue(emu.test_gps()["pps_detected"])
        self.assertTrue(emu.test_radio()["spi_ok"])
        self.assertTrue(emu.verify_final_firmware()["hash_ok"])

    def test_intermittent_imu_passes_second_attempt(self):
        emu.set_fault_mode("INTERMITTENT_IMU")
        emu.power_on()
        self.assertFalse(emu.test_imu())
        self.assertTrue(emu.test_imu())

    def test_vbatt_monitor_failure_exceeds_project_limit(self):
        emu.set_fault_mode("VBATT_MONITOR_FAILURE")
        emu.power_on()
        row = emu.read_adm1176_voltage(7.4)
        error = abs(row["adm1176_voltage_v"] - 7.4) / 7.4 * 100
        self.assertGreater(error, 5.0)

    def test_radio_failure_is_detectable(self):
        emu.set_fault_mode("RADIO_FAILURE")
        emu.power_on()
        self.assertFalse(emu.test_radio()["spi_ok"])

    def test_reference_verification(self):
        emu.load_reference()
        self.assertTrue(emu.verify_reference_power())
        self.assertAlmostEqual(emu.read_reference_3v3(), 3.30, places=2)
        self.assertTrue(emu.verify_reference_boot())
        self.assertTrue(emu.verify_reference_sensor())

    def test_cleanup(self):
        emu.power_on()
        emu.load_reference()
        emu.cleanup()
        self.assertFalse(emu.get_state()["powered"])
        self.assertFalse(emu.get_state()["reference_loaded"])


if __name__ == "__main__":
    unittest.main()
