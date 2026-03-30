from __future__ import annotations


def assert_contains(actual: str, expected: str, context: str = "") -> None:
    if expected not in actual:
        raise AssertionError(f"{context} expected '{expected}' to be contained in '{actual}'.")


def assert_equal(actual, expected, context: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{context} expected '{expected}', got '{actual}'.")

