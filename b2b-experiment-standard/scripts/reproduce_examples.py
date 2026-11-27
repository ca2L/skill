#!/usr/bin/env python3
"""Replay the canonical quote-SLA case and compare it with documented values.

Run: python scripts/reproduce_examples.py
Exit code 0 means all four commands match 15-running-case.md and 90-validation.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).with_name("experiment_stats.py")

CASES = [
    (
        "power-binary",
        ["power-binary", "--baseline", "0.084", "--mde-relative", "0.11"],
        {"individual_n_per_arm": 14847, "relative_mde": 0.11},
    ),
    (
        "mde-binary",
        ["mde-binary", "--baseline", "0.084", "--n-per-arm", "16000"],
        {"absolute_mde": 0.008893, "relative_mde": 0.105866},
    ),
    (
        "test-binary",
        ["test-binary", "--baseline", "0.084", "--treatment", "0.092", "--n-per-arm", "16000"],
        {
            "absolute_lift": 0.008,
            "relative_lift": 0.095238,
            "p_value": 0.011544,
            "ci_absolute": [0.00179276, 0.01420724],
            "ci_relative": [0.021342, 0.169134],
            "significant": True,
        },
    ),
    (
        "srm",
        ["srm", "--counts", "16000", "15850"],
        {"chi_square": 0.706436, "p_value": 0.400629, "status": "pass"},
    ),
]


def close(actual, expected) -> bool:
    if isinstance(expected, bool):
        return actual is expected
    if isinstance(expected, int):
        return actual == expected
    if isinstance(expected, float):
        return abs(float(actual) - expected) <= 5e-6
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(close(a, e) for a, e in zip(actual, expected))
    return actual == expected


def run_case(name: str, args: list[str], expected: dict) -> list[str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        return [f"{name}: exit {proc.returncode}; stderr={proc.stderr.strip()}"]
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return [f"{name}: invalid JSON ({exc})"]
    problems = []
    for key, want in expected.items():
        if key not in out:
            problems.append(f"{name}.{key}: missing")
        elif not close(out[key], want):
            problems.append(f"{name}.{key}: expected {want!r}, got {out[key]!r}")
    return problems


def main() -> int:
    failures: list[str] = []
    for name, args, expected in CASES:
        problems = run_case(name, args, expected)
        if problems:
            failures.extend(problems)
            print(f"[FAIL] {name}")
            for p in problems:
                print(f"       {p}")
        else:
            print(f"[PASS] {name}")
    if failures:
        print(f"\n{len(failures)} mismatch(es); canonical case is not reproducible.")
        return 1
    print("\nAll four canonical commands match the documented numbers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
