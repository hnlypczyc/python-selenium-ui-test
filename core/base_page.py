from __future__ import annotations

from pathlib import Path
from typing import Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


Locator = Tuple[By, str]


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.timeout = timeout

    def open(self, url: str) -> None:
        self.driver.get(url)

    def wait_for_visible(self, locator: Locator, timeout: int | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(ec.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator: Locator, timeout: int | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(ec.element_to_be_clickable(locator))

    def wait_for_invisible(self, locator: Locator, timeout: int | None = None) -> bool:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(ec.invisibility_of_element_located(locator))

    def find(self, locator: Locator) -> WebElement:
        return self.driver.find_element(*locator)

    def finds(self, locator: Locator) -> list[WebElement]:
        return self.driver.find_elements(*locator)

    def click(self, locator: Locator) -> None:
        self.wait_for_clickable(locator).click()

    def js_click(self, locator: Locator) -> None:
        element = self.wait_for_visible(locator)
        self.driver.execute_script("arguments[0].click();", element)

    def type(self, locator: Locator, value: str, clear_first: bool = True) -> None:
        element = self.wait_for_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(value)

    def clear(self, locator: Locator) -> None:
        self.wait_for_visible(locator).clear()

    def send_keys(self, locator: Locator, *keys: str) -> None:
        self.wait_for_visible(locator).send_keys(*keys)

    def text_of(self, locator: Locator) -> str:
        return self.wait_for_visible(locator).text.strip()

    def attribute_of(self, locator: Locator, attribute_name: str) -> str | None:
        return self.wait_for_visible(locator).get_attribute(attribute_name)

    def is_visible(self, locator: Locator, timeout: int | None = None) -> bool:
        try:
            self.wait_for_visible(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def is_clickable(self, locator: Locator, timeout: int | None = None) -> bool:
        try:
            self.wait_for_clickable(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def select_by_text(self, locator: Locator, text: str) -> None:
        Select(self.wait_for_visible(locator)).select_by_visible_text(text)

    def select_by_value(self, locator: Locator, value: str) -> None:
        Select(self.wait_for_visible(locator)).select_by_value(value)

    def select_by_index(self, locator: Locator, index: int) -> None:
        Select(self.wait_for_visible(locator)).select_by_index(index)

    def selected_option_text(self, locator: Locator) -> str:
        return Select(self.wait_for_visible(locator)).first_selected_option.text.strip()

    def hover(self, locator: Locator) -> None:
        element = self.wait_for_visible(locator)
        ActionChains(self.driver).move_to_element(element).perform()

    def double_click(self, locator: Locator) -> None:
        element = self.wait_for_clickable(locator)
        ActionChains(self.driver).double_click(element).perform()

    def right_click(self, locator: Locator) -> None:
        element = self.wait_for_clickable(locator)
        ActionChains(self.driver).context_click(element).perform()

    def drag_and_drop(self, source_locator: Locator, target_locator: Locator) -> None:
        source = self.wait_for_visible(source_locator)
        target = self.wait_for_visible(target_locator)
        ActionChains(self.driver).drag_and_drop(source, target).perform()

    def drag_and_drop_by_offset(self, locator: Locator, x_offset: int, y_offset: int) -> None:
        element = self.wait_for_visible(locator)
        ActionChains(self.driver).drag_and_drop_by_offset(element, x_offset, y_offset).perform()

    def scroll_to_element(self, locator: Locator, block: str = "center") -> None:
        element = self.wait_for_visible(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: arguments[1]});", element, block)

    def scroll_to_top(self) -> None:
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def execute_js(self, script: str, *args):
        return self.driver.execute_script(script, *args)

    def switch_to_frame(self, locator: Locator) -> None:
        frame = self.wait_for_visible(locator)
        self.driver.switch_to.frame(frame)

    def switch_to_default_content(self) -> None:
        self.driver.switch_to.default_content()

    def switch_to_window(self, index: int = -1) -> None:
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[index])

    def open_new_tab(self) -> None:
        self.driver.switch_to.new_window("tab")

    def open_new_window(self) -> None:
        self.driver.switch_to.new_window("window")

    def refresh(self) -> None:
        self.driver.refresh()

    def back(self) -> None:
        self.driver.back()

    def forward(self) -> None:
        self.driver.forward()

    def press_enter(self, locator: Locator) -> None:
        self.send_keys(locator, Keys.ENTER)

    def press_escape(self, locator: Locator) -> None:
        self.send_keys(locator, Keys.ESCAPE)

    def wait_for_page_ready(self, timeout: int | None = None) -> None:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(lambda web_driver: web_driver.execute_script("return document.readyState") == "complete")

    def save_screenshot(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.driver.save_screenshot(str(path))
        return path

