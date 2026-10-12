"""Persistent storage for PyCubed TestStand test results.

All runtime result files are stored in one directory:

    test_data/<SERIAL>_<STATION>_<YYYYMMDD>_<HHMMSS>_<MICROSECONDS>.json

Each completed test run gets its own file. Repeated tests of the same DUT are
therefore preserved as separate files and can be ordered by timestamp.
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
    """Save one completed test run and return the JSON file path."""

    now = datetime.now().astimezone()
    root = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
    root.mkdir(parents=True, exist_ok=True)

    serial = _safe_name(serial_number)
    station = _safe_name(station_id)
    timestamp_for_name = now.strftime("%Y%m%d_%H%M%S_%f")
    file_path = root / f"{serial}_{station}_{timestamp_for_name}.json"

    document = {
        "serial_number": serial_number,
        "station_id": station_id,
        "test_date": now.date().isoformat(),
        "test_time": now.strftime("%H:%M:%S"),
        "timestamp": now.isoformat(timespec="microseconds"),
        "operator_id": operator_id,
        "station_verified": bool(station_verified),
        "station_verification_date": station_verification_date,
        "overall_result": str(overall_result).upper(),
        "steps": list(steps),
    }

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
