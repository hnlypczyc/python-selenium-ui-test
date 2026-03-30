from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

import data.data_loader as data_loader
from data.data_loader import discover_case_data, find_case_data_file


def _write_excel(path: Path, headers: list[str], rows: list[tuple[object, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "data"
    worksheet.append(headers)
    for row in rows:
        worksheet.append(row)
    workbook.save(path)
    workbook.close()


def test_sample_excel_file_exists():
    assert find_case_data_file("TC02_新增员工", app_name="orangehrm") is not None


def test_invalid_login_excel_file_exists():
    dataset = discover_case_data("TC03_登录失败", app_name="orangehrm")
    assert dataset.file_path is not None


def test_discover_case_data_filters_by_execute_column(tmp_path, monkeypatch):
    case_name = "TC10_执行列过滤"
    data_file = tmp_path / "orangehrm" / f"{case_name}.xlsx"
    _write_excel(
        data_file,
        ["execute", "data_id", "test_title", "expected_result", "checkpoints"],
        [
            ("Y", "DATA_001", "有效数据", "成功执行", "断言通过"),
            ("N", "DATA_002", "停用数据", "不执行", "应被跳过"),
        ],
    )
    monkeypatch.setattr(data_loader, "DATA_DIR", tmp_path)

    dataset = discover_case_data(case_name, app_name="orangehrm")

    assert dataset.file_path == data_file
    assert dataset.skip_reason is None
    assert [row["data_id"] for row in dataset.rows] == ["DATA_001"]


def test_discover_case_data_allows_missing_data_file(tmp_path, monkeypatch):
    monkeypatch.setattr(data_loader, "DATA_DIR", tmp_path)

    dataset = discover_case_data("TC12_无数据文件", app_name="orangehrm")

    assert dataset.file_path is None
    assert dataset.rows == []
    assert dataset.skip_reason == "No Excel data file matched case name 'TC12_无数据文件'."

