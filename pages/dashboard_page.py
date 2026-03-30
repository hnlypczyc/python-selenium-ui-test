from __future__ import annotations

from selenium.webdriver.common.by import By

from core.base_page import BasePage


class DashboardPage(BasePage):
    DASHBOARD_HEADER = (By.XPATH, "//h6[normalize-space()='Dashboard']")
    PIM_MENU = (By.XPATH, "//span[normalize-space()='PIM']")

    def wait_until_loaded(self) -> None:
        self.wait_for_page_ready()
        self.wait_for_visible(self.DASHBOARD_HEADER)

    def is_loaded(self) -> bool:
        return self.is_visible(self.DASHBOARD_HEADER, timeout=self.timeout)

    def open_pim(self) -> None:
        self.click(self.PIM_MENU)

