from __future__ import annotations

import pytest

from flows.login_flow import LoginFlow


pytestmark = [pytest.mark.ui, pytest.mark.smoke]
case_name = "TC01_登录成功"


def test_orangehrm_login_success(driver, settings, base_url):
    dashboard = LoginFlow(driver, settings, base_url).login_as_default_admin()
    assert dashboard.is_loaded(), "Login should land on the OrangeHRM dashboard."

