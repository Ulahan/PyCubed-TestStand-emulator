import unittest

from emulator import pycubed_emulator as emu


class TestPyCubedEmulator(unittest.TestCase):
    def setUp(self):
        emu.set_fault_mode("NORMAL")
        emu.set_reference_mode("REFERENCE_NORMAL")
        emu.initialize_emulator()

    def test_normal_dut(self):
        self.assertTrue(emu.power_on())
        self.assertAlmostEqual(emu.read_3v3(), 3.30, places=2)
        self.assertTrue(emu.test_boot())
        self.assertTrue(emu.test_imu())
        self.assertAlmostEqual(emu.read_battery(), 3.95, places=2)

    def test_intermittent_imu_passes_second_attempt(self):
        emu.set_fault_mode("INTERMITTENT_IMU")
        self.assertTrue(emu.power_on())
        self.assertFalse(emu.test_imu())
        self.assertTrue(emu.test_imu())

    def test_reference_verification(self):
        self.assertTrue(emu.load_reference())
        self.assertTrue(emu.verify_reference_power())
        self.assertAlmostEqual(emu.read_reference_3v3(), 3.30, places=2)
        self.assertTrue(emu.verify_reference_boot())
        self.assertTrue(emu.verify_reference_sensor())

    def test_failed_reference_rail(self):
        emu.set_reference_mode("REFERENCE_RAIL_FAILURE")
        emu.load_reference()
        self.assertLess(emu.read_reference_3v3(), 3.25)

    def test_cleanup(self):
        emu.power_on()
        emu.load_reference()
        self.assertTrue(emu.cleanup())
        state = emu.get_state()
        self.assertFalse(state["powered"])
        self.assertFalse(state["reference_loaded"])


if __name__ == "__main__":
    unittest.main()
