#!/usr/bin/env python3
"""Structural checks for the skill package.

Run: python scripts/check_docs.py
This is not a substitute for statistical validation; see references/90-validation.md.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = [
    "SKILL.md",
    "README.md",
    "references/INDEX.md",
    "references/00-triage.md",
    "references/05-glossary.md",
    "references/10-design.md",
    "references/15-running-case.md",
    "references/20-data-quality.md",
    "references/30-metrics-statistics.md",
    "references/40-decision-longterm.md",
    "references/50-templates.md",
    "references/60-field-dictionary.md",
    "references/70-anti-patterns.md",
    "references/80-governance-platform.md",
    "references/90-validation.md",
    "assets/B2B电商平台实验规范.md",
    "assets/实验字段字典.csv",
    "scripts/experiment_stats.py",
    "scripts/test_experiment_stats.py",
    "scripts/reproduce_examples.py",
    "scripts/check_docs.py",
    "scripts/check.ps1",
]
MAX_SKILL_BYTES = 8192
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*```")


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []

    def fail(message: str) -> None:
        failures.append(message)

    for rel in EXPECTED:
        if not (ROOT / rel).is_file():
            fail(f"missing file: {rel}")
    if failures:
        for item in failures:
            print(f"[FAIL] {item}")
        return 1

    skill = read("SKILL.md")
    if not skill.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    else:
        end = skill.find("\n---", 4)
        if end < 0:
            fail("SKILL.md frontmatter is not closed")
        else:
            fm = skill[4:end]
            name_match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", fm, re.MULTILINE)
            desc_match = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
            if not name_match or name_match.group(1) != "b2b-experiment-standard":
                fail("SKILL.md name must be b2b-experiment-standard")
            if not desc_match or len(desc_match.group(1).strip()) < 40:
                fail("SKILL.md description is missing or too short")

    size = (ROOT / "SKILL.md").stat().st_size
    if size > MAX_SKILL_BYTES:
        fail(f"SKILL.md is {size} bytes; limit is {MAX_SKILL_BYTES}")

    for phrase in ["61", "SRM", "CUPED", "护栏", "决策"]:
        if phrase not in skill:
            fail(f"SKILL.md missing key phrase: {phrase}")

    for rel in EXPECTED:
        if not rel.endswith(".md"):
            continue
        text = read(rel)
        fences = sum(1 for line in text.splitlines() if FENCE_RE.match(line))
        if fences % 2 != 0:
            fail(f"{rel}: odd number of code fences ({fences})")
        for raw in LINK_RE.findall(text):
            target = raw.strip().strip("<>").split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            if not (Path(ROOT / rel).parent / target).resolve().exists():
                fail(f"{rel}: broken link target {raw!r}")

    # Table rows in each contiguous block must have the same pipe count.
    for rel in EXPECTED:
        if not rel.endswith(".md"):
            continue
        text = read(rel)
        block: list[str] = []
        in_fence = False

        def check_block(block_lines: list[str]) -> None:
            if len(block_lines) < 2:
                return
            counts = {line.count("|") for line in block_lines}
            if len(counts) > 1:
                fail(f"{rel}: inconsistent table column count near {block_lines[0].strip()[:60]!r}")

        for line in text.splitlines():
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if line.strip().startswith("|"):
                block.append(line)
            else:
                check_block(block)
                block = []
        check_block(block)

    csv_path = ROOT / "assets/实验字段字典.csv"
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 61:
        fail(f"field CSV has {len(rows)} rows, expected 61")
    ids = [row.get("field_id", "") for row in rows]
    if len(set(ids)) != 61 or any(not value for value in ids):
        fail("field CSV ids are not 61 unique non-empty values")
    module_counts: dict[str, int] = {}
    for row in rows:
        module = (row.get("module", "") or "").strip()[:1]
        module_counts[module] = module_counts.get(module, 0) + 1
    expected_counts = {"A": 8, "B": 8, "C": 7, "D": 7, "E": 7, "F": 7, "G": 6, "H": 6, "I": 5}
    for module, expected in expected_counts.items():
        if module_counts.get(module, 0) != expected:
            fail(f"field module {module}: {module_counts.get(module, 0)} rows, expected {expected}")

    dictionary = read("references/60-field-dictionary.md")
    missing = [field_id for field_id in ids if field_id not in dictionary]
    if missing:
        fail(f"60-field-dictionary.md missing ids: {', '.join(missing)}")

    case = read("references/15-running-case.md")
    for token in ["0.011544", "16000", "0.706436"]:
        if token not in case:
            fail(f"15-running-case.md missing canonical value: {token}")
    validation = read("references/90-validation.md")
    for token in ["0.400629", "0.011544", "0.706436"]:
        if token not in validation:
            fail(f"90-validation.md missing canonical value: {token}")
    anti = read("references/70-anti-patterns.md")
    if "6,200" in anti or "6200" in anti:
        fail("70-anti-patterns.md still contains the retired 6,200 case")
    templates = read("references/50-templates.md")
    if "6200" in templates or "12400" in templates:
        fail("50-templates.md still contains the retired 6,200/12,400 sample")
    if "1.1.0" not in read("README.md"):
        fail("README.md does not declare version 1.1.0")

    if failures:
        for item in failures:
            print(f"[FAIL] {item}")
        print(f"\n{len(failures)} structural check(s) failed.")
        return 1
    print("[PASS] frontmatter and SKILL.md size")
    print("[PASS] required files")
    print("[PASS] local links and code fences")
    print("[PASS] tables")
    print("[PASS] 61 fields, module counts, dictionary coverage")
    print("[PASS] canonical case and version markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
