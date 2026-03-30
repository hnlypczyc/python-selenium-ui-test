from __future__ import annotations

from selenium.webdriver.common.by import By

from core.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".oxd-alert-content-text")

    def open_login_page(self, base_url: str) -> None:
        self.open(base_url)
        self.wait_for_page_ready()
        self.wait_for_visible(self.USERNAME_INPUT)

    def login(self, username: str, password: str) -> None:
        self.type(self.USERNAME_INPUT, username)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        return self.text_of(self.ERROR_MESSAGE)

