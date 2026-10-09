import json
import tempfile
import unittest
from pathlib import Path

from emulator.test_data_store import build_step, save_test_run


class TestDataStore(unittest.TestCase):
    def test_file_name_contains_serial_and_station(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(
                save_test_run(
                    serial_number="PC05-00124",
                    station_id="TS-EMU-01",
                    operator_id="OP-TRAINING",
                    steps=[],
                    overall_result="PASS",
                    station_verified=True,
                    station_verification_date="2026-10-09",
                    data_dir=directory,
                )
            )

            self.assertEqual(path.name, "PC05-00124_TS-EMU-01.json")

    def test_repeated_runs_append_to_same_daily_file(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = {
                "serial_number": "PC05-00124",
                "station_id": "TS-EMU-01",
                "operator_id": "OP-TRAINING",
                "steps": [build_step("3.3 V Rail", "PASS", 3.30, "V", 3.20, 3.40)],
                "overall_result": "PASS",
                "station_verified": True,
                "station_verification_date": "2026-10-09",
                "data_dir": directory,
            }

            first_path = save_test_run(**arguments)
            second_path = save_test_run(**arguments)

            self.assertEqual(first_path, second_path)
            document = json.loads(Path(first_path).read_text(encoding="utf-8"))
            self.assertEqual(len(document["runs"]), 2)

    def test_step_keeps_value_limits_and_attempt(self):
        step = build_step(
            "IMU Test",
            "FAIL",
            False,
            attempt=2,
        )

        self.assertEqual(step["step_name"], "IMU Test")
        self.assertEqual(step["status"], "FAIL")
        self.assertFalse(step["measured_value"])
        self.assertEqual(step["attempt"], 2)


if __name__ == "__main__":
    unittest.main()
