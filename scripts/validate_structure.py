#!/usr/bin/env python3
"""Validate repository structure conventions for thesis workflow."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRIMARY_EXPOSE = ROOT / "docs" / "expose" / "Expose_v4_final_2026-02-28_encrypted.pdf"
LEGACY_EXPOSE_DIR = ROOT / "docs" / "expose" / "legacy"


def _is_tracked_by_git(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path)],
        capture_output=True,
        cwd=ROOT,
    )
    return result.returncode == 0


def check_session_summaries() -> list[str]:
    issues: list[str] = []
    for d in ROOT.rglob("session_summaries"):
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if p.is_dir():
                issues.append(f"Directory inside session_summaries not allowed: {p.relative_to(ROOT)}")
                continue
            if p.name in {".DS_Store", ".gitkeep"}:
                continue
            if p.suffix.lower() != ".yaml":
                issues.append(f"Non-YAML in session_summaries: {p.relative_to(ROOT)}")
    return issues


def check_expose_locations() -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    if not PRIMARY_EXPOSE.exists():
        issues.append(f"Primary expose missing: {PRIMARY_EXPOSE.relative_to(ROOT)}")

    for p in ROOT.rglob("*.docx"):
        if not _is_tracked_by_git(p):
            continue
        name = p.name.lower()
        if "expose" not in name and "expos" not in name:
            continue
        if LEGACY_EXPOSE_DIR in p.parents:
            continue
        if p.name.startswith("~$"):
            warnings.append(f"Temporary lock file present (close Word to remove): {p.relative_to(ROOT)}")
            continue
        issues.append(f"Expose outside primary/legacy: {p.relative_to(ROOT)}")

    return issues, warnings


def check_final_images() -> list[str]:
    issues: list[str] = []
    pattern = re.compile(r"_v\d{2}\.png$", re.IGNORECASE)
    for p in ROOT.rglob("images/final/*.png"):
        if not pattern.search(p.name):
            issues.append(f"Final image missing _vNN suffix: {p.relative_to(ROOT)}")
    return issues


def main() -> int:
    issues: list[str] = []
    warnings: list[str] = []
    issues.extend(check_session_summaries())
    expose_issues, expose_warnings = check_expose_locations()
    issues.extend(expose_issues)
    warnings.extend(expose_warnings)
    issues.extend(check_final_images())

    if issues:
        print("Structure validation FAILED:\n")
        for i in issues:
            print(f"- {i}")
        if warnings:
            print("\nWarnings:\n")
            for w in warnings:
                print(f"- {w}")
        return 1

    if warnings:
        print("Structure validation OK (with warnings):\n")
        for w in warnings:
            print(f"- {w}")
        return 0

    print("Structure validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
