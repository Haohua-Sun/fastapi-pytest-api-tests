from __future__ import annotations

import json
from collections.abc import Mapping
from json import JSONDecodeError
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

Case = dict[str, Any]


def load_json_cases(
    filename: str,
    required_keys: set[str] | None = None,
    enum_fields: Mapping[str, set[str]] | None = None,
) -> list[Case]:
    file_path = DATA_DIR / filename
    if not file_path.is_file():
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except JSONDecodeError as exc:
        raise ValueError(f"{filename} is not valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError(f"{filename} should contain a JSON list")

    required_keys = required_keys or set()
    enum_fields = enum_fields or {}
    cases: list[Case] = []
    seen_case_ids: set[str] = set()
    for index, case in enumerate(data):
        if not isinstance(case, dict):
            raise ValueError(f"{filename}[{index}] should be a JSON object")

        missing_keys = required_keys - set(case)
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ValueError(f"{filename}[{index}] missing required keys: {missing}")

        expected_status = case.get("expected_status")
        if expected_status is not None and not isinstance(expected_status, int):
            raise ValueError(f"{filename}[{index}].expected_status should be an integer")

        expected_detail = case.get("expected_detail")
        if expected_detail is not None and not isinstance(expected_detail, str):
            raise ValueError(f"{filename}[{index}].expected_detail should be a string")

        case_id = case.get("case_id")
        if case_id is not None:
            if not isinstance(case_id, str) or not case_id.strip():
                raise ValueError(f"{filename}[{index}].case_id should be a non-empty string")
            if case_id in seen_case_ids:
                raise ValueError(f"{filename} contains duplicate case_id: {case_id}")
            seen_case_ids.add(case_id)

        for field_name, allowed_values in enum_fields.items():
            value = case.get(field_name)
            if value not in allowed_values:
                allowed = ", ".join(sorted(allowed_values))
                raise ValueError(f"{filename}[{index}].{field_name} should be one of: {allowed}")

        cases.append(case)

    return cases
