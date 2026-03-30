from __future__ import annotations

import argparse
import sys

import pytest

from utils.file_manager import ensure_directories
from utils.paths import create_runtime_paths


def _contains_option(arguments: list[str], option_name: str) -> bool:
    return any(argument == option_name or argument.startswith(f"{option_name}=") for argument in arguments)


def main(argv: list[str] | None = None) -> int:
    incoming_args = list(argv if argv is not None else sys.argv[1:])

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--run-id", default=None)
    parsed_args, _ = parser.parse_known_args(incoming_args)

    runtime_paths = create_runtime_paths(parsed_args.run_id)
    ensure_directories(
        [
            runtime_paths.report_dir,
            runtime_paths.log_dir,
            runtime_paths.screenshot_dir,
            runtime_paths.allure_results_dir,
        ]
    )

    pytest_args = list(incoming_args)
    if not _contains_option(pytest_args, "--run-id"):
        pytest_args.extend(["--run-id", runtime_paths.run_id])
    if not _contains_option(pytest_args, "--alluredir"):
        pytest_args.extend(["--alluredir", str(runtime_paths.allure_results_dir)])
    if not _contains_option(pytest_args, "--junitxml"):
        pytest_args.extend(["--junitxml", str(runtime_paths.report_dir / "junit.xml")])
    if not _contains_option(pytest_args, "--html"):
        pytest_args.extend(["--html", str(runtime_paths.html_report_file)])
    if not _contains_option(pytest_args, "--self-contained-html"):
        pytest_args.append("--self-contained-html")
    return pytest.main(pytest_args)


if __name__ == "__main__":
    raise SystemExit(main())

