from __future__ import annotations

import pytest

from flows.login_flow import LoginFlow


pytestmark = [pytest.mark.ui, pytest.mark.report_demo]
case_name = "TC99_报告截图失败演示"


def test_report_demo_intentional_failure(driver, settings, base_url):
    dashboard = LoginFlow(driver, settings, base_url).login_as_default_admin()
    assert dashboard.is_loaded(), "Precondition failed: dashboard should be loaded before the report demo assertion."

    assert False, (
        "Intentional failure for HTML report screenshot verification. "
        "Use this case to confirm failed-test screenshots are embedded in the report."
    )
