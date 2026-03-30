from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from core.exceptions import MissingCaseDataError
from utils.excel_reader import ExcelReader
from utils.paths import DATA_DIR


@dataclass(frozen=True)
class CaseDataSet:
    case_name: str
    file_path: Path | None
    rows: list[dict[str, Any]]
    skip_reason: str | None = None


def find_case_data_file(case_name: str, app_name: str | None = None) -> Path | None:
    search_roots = []
    if app_name:
        search_roots.append(DATA_DIR / app_name)
    search_roots.append(DATA_DIR)

    for root in search_roots:
        candidate = root / f"{case_name}.xlsx"
        if candidate.exists():
            return candidate
        matches = list(root.rglob(f"{case_name}.xlsx")) if root.exists() else []
        if matches:
            return matches[0]
    return None


def discover_case_data(case_name: str, app_name: str | None = None, sheet_name: str = "data") -> CaseDataSet:
    data_file = find_case_data_file(case_name, app_name=app_name)
    if not data_file:
        return CaseDataSet(
            case_name=case_name,
            file_path=None,
            rows=[],
            skip_reason=f"No Excel data file matched case name '{case_name}'.",
        )

    reader = ExcelReader(data_file)
    rows = reader.get_executable_rows(sheet_name=sheet_name)
    if not rows:
        return CaseDataSet(
            case_name=case_name,
            file_path=data_file,
            rows=[],
            skip_reason=f"Excel data file '{data_file.name}' does not contain executable rows for '{case_name}'.",
        )

    return CaseDataSet(case_name=case_name, file_path=data_file, rows=rows)


def load_case_rows(case_name: str, app_name: str | None = None, sheet_name: str = "data") -> list[dict[str, Any]]:
    dataset = discover_case_data(case_name, app_name=app_name, sheet_name=sheet_name)
    return dataset.rows


def build_case_params(case_name: str, app_name: str | None = None, sheet_name: str = "data") -> list[Any]:
    dataset = discover_case_data(case_name, app_name=app_name, sheet_name=sheet_name)
    if dataset.skip_reason:
        return [pytest.param(None, id=case_name, marks=pytest.mark.skip(reason=dataset.skip_reason))]

    params = []
    for row in dataset.rows:
        data_id = row.get("data_id", "row")
        title = row.get("test_title", case_name)
        params.append(pytest.param(row, id=f"{data_id}_{title}"))
    return params


def require_case_rows(case_name: str, app_name: str | None = None, sheet_name: str = "data") -> list[dict[str, Any]]:
    dataset = discover_case_data(case_name, app_name=app_name, sheet_name=sheet_name)
    if dataset.skip_reason:
        raise MissingCaseDataError(dataset.skip_reason)
    return dataset.rows

