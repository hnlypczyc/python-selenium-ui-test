from __future__ import annotations

from selenium.webdriver.common.by import By

from core.base_page import BasePage


class PimPage(BasePage):
    ADD_EMPLOYEE_BUTTON = (By.XPATH, "//button[normalize-space()='Add']")
    FIRST_NAME_INPUT = (By.NAME, "firstName")
    MIDDLE_NAME_INPUT = (By.NAME, "middleName")
    LAST_NAME_INPUT = (By.NAME, "lastName")
    SAVE_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    PERSONAL_DETAILS_HEADER = (By.XPATH, "//h6[normalize-space()='Personal Details']")

    def open_add_employee_form(self) -> None:
        self.wait_for_page_ready()
        self.click(self.ADD_EMPLOYEE_BUTTON)
        self.wait_for_visible(self.FIRST_NAME_INPUT)

    def add_employee(self, first_name: str, middle_name: str, last_name: str) -> None:
        self.type(self.FIRST_NAME_INPUT, first_name)
        self.type(self.MIDDLE_NAME_INPUT, middle_name)
        self.type(self.LAST_NAME_INPUT, last_name)
        self.click(self.SAVE_BUTTON)

    def is_personal_details_loaded(self) -> bool:
        return self.is_visible(self.PERSONAL_DETAILS_HEADER, timeout=self.timeout)

