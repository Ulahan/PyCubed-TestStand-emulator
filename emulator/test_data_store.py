"""Persistent storage for PyCubed TestStand test results.

Results are grouped by calendar date. Each DUT/station pair gets one JSON
file per day:

    test_data/YYYY-MM-DD/<SERIAL>_<STATION>.json

Repeated tests of the same serial number on the same station and date are
appended to the file as separate runs.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "test_data"


def save_test_run(
    serial_number: str,
    station_id: str,
    operator_id: str,
    steps: Iterable[dict[str, Any]],
    overall_result: str,
    station_verified: bool,
    station_verification_date: str | None = None,
    data_dir: str | Path | None = None,
) -> str:
    """Append one completed test run and return the JSON file path."""

    now = datetime.now().astimezone()
    test_date = now.date().isoformat()
    root = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
    day_dir = root / test_date
    day_dir.mkdir(parents=True, exist_ok=True)

    serial = _safe_name(serial_number)
    station = _safe_name(station_id)
    file_path = day_dir / f"{serial}_{station}.json"

    if file_path.exists():
        document = json.loads(file_path.read_text(encoding="utf-8"))
    else:
        document = {
            "date": test_date,
            "serial_number": serial_number,
            "station_id": station_id,
            "runs": [],
        }

    run = {
        "run_id": now.strftime("%Y%m%dT%H%M%S%f"),
        "timestamp": now.isoformat(timespec="seconds"),
        "operator_id": operator_id,
        "station_verified": bool(station_verified),
        "station_verification_date": station_verification_date,
        "overall_result": str(overall_result).upper(),
        "steps": list(steps),
    }

    document["runs"].append(run)
    _write_json_atomic(file_path, document)
    return str(file_path)


def build_step(
    step_name: str,
    status: str,
    measured_value: Any,
    unit: str | None = None,
    minimum: float | None = None,
    maximum: float | None = None,
    attempt: int = 1,
) -> dict[str, Any]:
    """Create a normalized record for one executed test step."""

    limits = None
    if minimum is not None or maximum is not None:
        limits = {"min": minimum, "max": maximum}

    return {
        "step_name": step_name,
        "status": str(status).upper(),
        "measured_value": measured_value,
        "unit": unit,
        "limits": limits,
        "attempt": attempt,
    }


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value).strip())
    if not cleaned:
        raise ValueError("Serial number and station ID cannot be empty")
    return cleaned


def _write_json_atomic(file_path: Path, document: dict[str, Any]) -> None:
    temporary = file_path.with_suffix(file_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(file_path)
