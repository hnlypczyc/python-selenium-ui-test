from __future__ import annotations

import pytest

from data.data_loader import build_case_params
from pages.login_page import LoginPage


pytestmark = [pytest.mark.ui, pytest.mark.regression]
case_name = "TC03_登录失败"


@pytest.mark.parametrize("case_data", build_case_params(case_name, app_name="orangehrm"))
def test_invalid_login_shows_error_message(driver, settings, base_url, case_data):
    login_page = LoginPage(driver, timeout=settings["execution"]["explicit_wait"])
    login_page.open_login_page(base_url)
    login_page.login(case_data["username"], case_data["password"])
    actual_error = login_page.get_error_message()
    assert case_data["expected_error"] in actual_error, (
        f"Expected login error to contain '{case_data['expected_error']}', got '{actual_error}'. "
        f"Checkpoints: {case_data['checkpoints']}"
    )

