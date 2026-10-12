import json
import tempfile
import unittest
from pathlib import Path

from emulator.test_data_store import build_step, save_test_run


class TestDataStore(unittest.TestCase):
    def test_file_name_contains_serial_station_and_timestamp(self):
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

            self.assertTrue(path.name.startswith("PC05-00124_TS-EMU-01_"))
            self.assertTrue(path.name.endswith(".json"))
            self.assertEqual(path.parent, Path(directory))

    def test_repeated_runs_create_separate_files(self):
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

            first_path = Path(save_test_run(**arguments))
            second_path = Path(save_test_run(**arguments))

            self.assertNotEqual(first_path.name, second_path.name)
            self.assertTrue(first_path.exists())
            self.assertTrue(second_path.exists())

    def test_saved_document_contains_test_time_and_steps(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(
                save_test_run(
                    serial_number="PC05-00124",
                    station_id="TS-EMU-01",
                    operator_id="OP-TRAINING",
                    steps=[build_step("IMU Test", "FAIL", False, attempt=2)],
                    overall_result="FAIL",
                    station_verified=True,
                    station_verification_date="2026-10-09",
                    data_dir=directory,
                )
            )

            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("test_date", document)
            self.assertIn("test_time", document)
            self.assertIn("timestamp", document)
            self.assertEqual(document["steps"][0]["attempt"], 2)
            self.assertFalse(document["steps"][0]["measured_value"])


if __name__ == "__main__":
    unittest.main()
