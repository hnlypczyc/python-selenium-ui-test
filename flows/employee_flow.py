from __future__ import annotations

from typing import Any

from flows.login_flow import LoginFlow
from pages.pim_page import PimPage


class EmployeeFlow:
    def __init__(self, driver, settings: dict[str, Any], base_url: str) -> None:
        self.driver = driver
        self.settings = settings
        self.base_url = base_url

    def add_employee(self, case_data: dict[str, Any]) -> dict[str, Any]:
        dashboard_page = LoginFlow(self.driver, self.settings, self.base_url).login_as_default_admin()
        dashboard_page.open_pim()
        pim_page = PimPage(self.driver, timeout=self.settings["execution"]["explicit_wait"])
        pim_page.open_add_employee_form()
        pim_page.add_employee(
            first_name=str(case_data.get("first_name", "")),
            middle_name=str(case_data.get("middle_name", "")),
            last_name=str(case_data.get("last_name", "")),
        )
        return {
            "saved": pim_page.is_personal_details_loaded(),
            "checkpoints": case_data.get("checkpoints", ""),
            "expected_result": case_data.get("expected_result", ""),
        }

