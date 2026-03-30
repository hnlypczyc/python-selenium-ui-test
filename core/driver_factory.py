from __future__ import annotations

from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from core.exceptions import UnsupportedBrowserError


def _bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "y", "yes", "on"}


def _build_options(settings: dict[str, Any], browser_name: str, headless: bool):
    browser_options = settings.get("browser_options", {}).get(browser_name, {})
    arguments = browser_options.get("arguments", [])
    execution = settings.get("execution", {})

    if browser_name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument(f"--window-size={execution.get('headless_window_size', '1920,1080')}")
        for argument in arguments:
            options.add_argument(argument)
        return options

    if browser_name == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument(f"--window-size={execution.get('headless_window_size', '1920,1080')}")
        for argument in arguments:
            options.add_argument(argument)
        return options

    if browser_name == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        for argument in arguments:
            options.add_argument(argument)
        return options

    raise UnsupportedBrowserError(f"Unsupported browser: {browser_name}")


def create_driver(
    settings: dict[str, Any],
    browser: str | None = None,
    headless: bool | str | None = None,
    remote_url: str | None = None,
):
    execution = settings.get("execution", {})
    browser_name = (browser or execution.get("browser", "chrome")).lower()
    resolved_headless = _bool_value(headless if headless is not None else execution.get("headless", False))
    resolved_remote_url = remote_url if remote_url is not None else execution.get("remote_url", "")
    options = _build_options(settings, browser_name, resolved_headless)

    if resolved_remote_url:
        driver = webdriver.Remote(command_executor=resolved_remote_url, options=options)
    elif browser_name == "chrome":
        driver = webdriver.Chrome(options=options)
    elif browser_name == "edge":
        driver = webdriver.Edge(options=options)
    elif browser_name == "firefox":
        driver = webdriver.Firefox(options=options)
    else:
        raise UnsupportedBrowserError(f"Unsupported browser: {browser_name}")

    page_load_timeout = execution.get("page_load_timeout")
    implicit_wait = execution.get("implicit_wait")
    if page_load_timeout:
        driver.set_page_load_timeout(int(page_load_timeout))
    if implicit_wait:
        driver.implicitly_wait(int(implicit_wait))
    return driver

