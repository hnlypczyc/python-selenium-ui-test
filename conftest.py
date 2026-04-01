from __future__ import annotations

import allure
import logging
import shutil
from typing import Any

import pytest

from core.config_loader import load_settings
from core.driver_factory import create_driver
from utils.file_manager import ensure_directories
from utils.logger import configure_logging
from utils.paths import RuntimePaths, create_runtime_paths, worker_label


def _parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "y", "yes", "on"}


def _sanitize_node_id(node_id: str) -> str:
    invalid_characters = ["\\", "/", ":", "::", "[", "]", " "]
    result = node_id
    for character in invalid_characters:
        result = result.replace(character, "_")
    return result


def pytest_addoption(parser) -> None:
    parser.addoption("--env", action="store", default="demo", help="Target environment name.")
    parser.addoption("--browser", action="store", default=None, help="Browser to run: chrome, edge, firefox.")
    parser.addoption("--headless", action="store", default=None, help="Run browser in headless mode.")
    parser.addoption("--remote-url", action="store", default=None, help="Remote Selenium Grid URL.")
    parser.addoption("--base-url", action="store", default=None, help="Override base URL.")
    parser.addoption("--run-id", action="store", default=None, help="Custom run identifier for reports and logs.")


def pytest_configure(config) -> None:
    runtime_paths = create_runtime_paths(config.getoption("--run-id"))
    ensure_directories(
        [
            runtime_paths.report_dir,
            runtime_paths.log_dir,
            runtime_paths.screenshot_dir,
            runtime_paths.allure_results_dir,
            runtime_paths.report_assets_dir,
        ]
    )
    configure_logging(runtime_paths.log_dir)

    config.runtime_paths = runtime_paths
    config.framework_settings = load_settings(config.getoption("--env"))


def pytest_html_report_title(report) -> None:
    report.title = "python-selenium-ui-test Test Report"



@pytest.fixture(scope="session")
def settings(pytestconfig) -> dict[str, Any]:
    return pytestconfig.framework_settings


@pytest.fixture(scope="session")
def runtime_paths(pytestconfig) -> RuntimePaths:
    return pytestconfig.runtime_paths


@pytest.fixture(scope="session")
def base_url(pytestconfig, settings: dict[str, Any]) -> str:
    return pytestconfig.getoption("--base-url") or settings["app"]["base_url"]


@pytest.fixture(scope="function")
def driver(pytestconfig, settings: dict[str, Any]):
    browser = pytestconfig.getoption("--browser") or settings["execution"]["browser"]
    headless = _parse_bool(pytestconfig.getoption("--headless"), default=settings["execution"]["headless"])
    remote_url = pytestconfig.getoption("--remote-url") or settings["execution"].get("remote_url", "")

    driver_instance = create_driver(
        settings=settings,
        browser=browser,
        headless=headless,
        remote_url=remote_url,
    )
    yield driver_instance
    driver_instance.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when != "call" or report.passed:
        return

    driver_instance = item.funcargs.get("driver")
    runtime_paths: RuntimePaths | None = getattr(item.config, "runtime_paths", None)
    if not driver_instance or not runtime_paths:
        return

    screenshot_name = f"{_sanitize_node_id(item.nodeid)}_{worker_label()}.png"
    screenshot_path = runtime_paths.screenshot_dir / screenshot_name
    driver_instance.save_screenshot(str(screenshot_path))
    logging.getLogger(__name__).error("Saved failure screenshot: %s", screenshot_path)

    if item.config.pluginmanager.hasplugin("allure_pytest"):
        allure.attach.file(
            str(screenshot_path),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )

    html_plugin = item.config.pluginmanager.getplugin("html")
    if not html_plugin:
        return

    extras = list(getattr(report, "extras", []))
    report_image_path = runtime_paths.report_assets_dir / screenshot_name
    shutil.copy2(screenshot_path, report_image_path)
    image_relative_path = f"assets/{report_image_path.name}"
    extras.append(
        html_plugin.extras.html(
            (
                "<div>"
                "<p><strong>Failure Screenshot</strong></p>"
                f'<a href="{image_relative_path}" target="_blank">'
                f'<img src="{image_relative_path}" alt="failure screenshot" '
                'style="max-width: 320px; border: 1px solid #ccc;" />'
                "</a>"
                "</div>"
            )
        )
    )
    report.extras = extras

