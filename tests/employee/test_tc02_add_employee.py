from __future__ import annotations

import pytest

from data.data_loader import build_case_params
from flows.employee_flow import EmployeeFlow


pytestmark = [pytest.mark.ui, pytest.mark.smoke, pytest.mark.regression]
case_name = "TC02_新增员工"


@pytest.mark.parametrize("case_data", build_case_params(case_name, app_name="orangehrm"))
def test_add_employee(driver, settings, base_url, case_data):
    result = EmployeeFlow(driver, settings, base_url).add_employee(case_data)
    assert result["saved"], (
        "Employee creation should navigate to the personal details page. "
        f"Expected: {result['expected_result']} | Checkpoints: {result['checkpoints']}"
    )

