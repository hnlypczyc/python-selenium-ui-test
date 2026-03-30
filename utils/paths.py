from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOTS_DIR = ROOT_DIR / "screenshots"
ALLURE_RESULTS_DIR = ROOT_DIR / "allure-results"


def worker_label() -> str:
    return os.getenv("PYTEST_XDIST_WORKER", "main")


def build_run_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{uuid4().hex[:8]}"


@dataclass(frozen=True)
class RuntimePaths:
    run_id: str
    report_dir: Path
    log_dir: Path
    screenshot_dir: Path
    allure_results_dir: Path
    html_report_file: Path
    report_assets_dir: Path


def create_runtime_paths(run_id: str | None = None) -> RuntimePaths:
    resolved_run_id = run_id or os.getenv("TEST_RUN_ID") or build_run_id()
    return RuntimePaths(
        run_id=resolved_run_id,
        report_dir=REPORTS_DIR / resolved_run_id,
        log_dir=LOGS_DIR / resolved_run_id,
        screenshot_dir=SCREENSHOTS_DIR / resolved_run_id,
        allure_results_dir=ALLURE_RESULTS_DIR / resolved_run_id,
        html_report_file=REPORTS_DIR / resolved_run_id / "report.html",
        report_assets_dir=REPORTS_DIR / resolved_run_id / "assets",
    )

