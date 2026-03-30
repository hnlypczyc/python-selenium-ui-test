from __future__ import annotations

from typing import Any

from core.config_loader import get_default_credentials
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class LoginFlow:
    def __init__(self, driver, settings: dict[str, Any], base_url: str) -> None:
        self.driver = driver
        self.settings = settings
        self.base_url = base_url

    def login_as_default_admin(self) -> DashboardPage:
        credentials = get_default_credentials(self.settings)
        return self.login_with_credentials(credentials["username"], credentials["password"])

    def login_with_credentials(self, username: str, password: str) -> DashboardPage:
        login_page = LoginPage(self.driver, timeout=self.settings["execution"]["explicit_wait"])
        login_page.open_login_page(self.base_url)
        login_page.login(username, password)
        dashboard_page = DashboardPage(self.driver, timeout=self.settings["execution"]["explicit_wait"])
        dashboard_page.wait_until_loaded()
        return dashboard_page

