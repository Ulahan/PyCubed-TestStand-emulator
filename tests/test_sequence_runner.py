import unittest
from unittest.mock import patch

from emulator import pycubed_emulator as emu
from emulator.sequence_runner import SequenceRunner


class TestSequenceRunner(unittest.TestCase):
    def setUp(self):
        emu.set_fault_mode("NORMAL")
        emu.set_reference_mode("REFERENCE_NORMAL")

    def test_normal_sequence_passes(self):
        with patch("emulator.sequence_runner.save_test_run") as save:
            save.return_value = "result.json"
            path = SequenceRunner("OP-001", "PC05-TEST").run()
            self.assertEqual(path, "result.json")
            kwargs = save.call_args.kwargs
            self.assertEqual(kwargs["overall_result"], "PASS")
            self.assertTrue(kwargs["station_verified"])
            self.assertTrue(any(s["step_name"].startswith("17 ") for s in kwargs["steps"]))

    def test_fault_causes_fail(self):
        emu.set_fault_mode("RADIO_FAILURE")
        with patch("emulator.sequence_runner.save_test_run") as save:
            save.return_value = "result.json"
            SequenceRunner("OP-001", "PC05-TEST").run()
            self.assertEqual(save.call_args.kwargs["overall_result"], "FAIL")


if __name__ == "__main__":
    unittest.main()
