import json
import tempfile
import unittest
from pathlib import Path

from emulator.test_data_store import build_step, save_test_run


class TestDataStore(unittest.TestCase):
    def test_timestamped_file_and_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(save_test_run(
                serial_number="PC05-00124",
                station_id="TS-EMU-01",
                operator_id="OP-001",
                steps=[build_step("3.3 V Rail", "PASS", 3.30, "V", 3.20, 3.40)],
                overall_result="PASS",
                station_verified=True,
                station_verification_time="2026-10-27T18:00:00-07:00",
                data_dir=directory,
            ))
            self.assertTrue(path.name.startswith("PC05-00124_TS-EMU-01_"))
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(document["operator_id"], "OP-001")
            self.assertEqual(document["overall_result"], "PASS")
            self.assertEqual(document["steps"][0]["attempt"], 1)

    def test_repeated_runs_create_unique_files(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = {
                "serial_number": "PC05-1",
                "station_id": "TS-1",
                "operator_id": "OP-1",
                "steps": [],
                "overall_result": "PASS",
                "station_verified": True,
                "data_dir": directory,
            }
            first = Path(save_test_run(**arguments))
            second = Path(save_test_run(**arguments))
            self.assertNotEqual(first.name, second.name)


if __name__ == "__main__":
    unittest.main()
