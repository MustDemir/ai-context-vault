#!/usr/bin/env python3
"""Soft branch drift snapshot (info-only).

Compares selected files between main and an integration branch.
This script is intentionally non-blocking and always exits with code 0.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MAIN_REF = "origin/main"
DEFAULT_TARGET_REF = "origin/thesis/rq2-poc-integration"
DEFAULT_FILES = [
    "poc/chapter_state.yaml",
    "docs/ENTSCHEIDUNGSPAPIER_KAP4.md",
    "docs/ENTSCHEIDUNGSPAPIER_KAP5.md",
    "docs/roter_faden_tracker.md",
    "docs/thesis_state.md",
]


@dataclass
class FileDrift:
    path: str
    status: str
    added: str | None = None
    deleted: str | None = None
    note: str | None = None


@dataclass
class Snapshot:
    timestamp_utc: str
    mode: str
    main_ref: str
    target_ref: str
    main_sha: str | None
    target_sha: str | None
    status: str
    reason: str | None
    files: list[FileDrift]


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _resolve_sha(ref: str) -> str | None:
    result = _run_git(["rev-parse", "--verify", ref])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _file_numstat(main_ref: str, target_ref: str, rel_path: str) -> tuple[str, str]:
    result = _run_git(["diff", "--numstat", main_ref, target_ref, "--", rel_path])
    if result.returncode != 0 or not result.stdout.strip():
        return "?", "?"
    parts = result.stdout.strip().split("\t")
    if len(parts) < 2:
        return "?", "?"
    return parts[0], parts[1]


def _file_status(main_ref: str, target_ref: str, rel_path: str) -> FileDrift:
    result = _run_git(["diff", "--quiet", main_ref, target_ref, "--", rel_path])
    if result.returncode == 0:
        return FileDrift(path=rel_path, status="unchanged", added="0", deleted="0")
    if result.returncode == 1:
        added, deleted = _file_numstat(main_ref, target_ref, rel_path)
        return FileDrift(path=rel_path, status="changed", added=added, deleted=deleted)
    return FileDrift(path=rel_path, status="unknown", note="diff_failed")


def build_snapshot(main_ref: str, target_ref: str, files: list[str]) -> Snapshot:
    main_sha = _resolve_sha(main_ref)
    target_sha = _resolve_sha(target_ref)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not main_sha:
        return Snapshot(
            timestamp_utc=now,
            mode="soft-info-only",
            main_ref=main_ref,
            target_ref=target_ref,
            main_sha=None,
            target_sha=target_sha,
            status="skipped",
            reason=f"missing_ref:{main_ref}",
            files=[],
        )

    if not target_sha:
        return Snapshot(
            timestamp_utc=now,
            mode="soft-info-only",
            main_ref=main_ref,
            target_ref=target_ref,
            main_sha=main_sha[:12],
            target_sha=None,
            status="skipped",
            reason=f"missing_ref:{target_ref}",
            files=[],
        )

    drift_files = [_file_status(main_ref, target_ref, rel_path) for rel_path in files]

    return Snapshot(
        timestamp_utc=now,
        mode="soft-info-only",
        main_ref=main_ref,
        target_ref=target_ref,
        main_sha=main_sha[:12],
        target_sha=target_sha[:12],
        status="ok",
        reason=None,
        files=drift_files,
    )


def render_terminal(snapshot: Snapshot) -> str:
    lines = [
        "",
        "=== Branch Drift Snapshot (soft, info-only) ===",
        f"timestamp_utc: {snapshot.timestamp_utc}",
        f"main_ref:      {snapshot.main_ref}",
        f"target_ref:    {snapshot.target_ref}",
        f"main_sha:      {snapshot.main_sha or '-'}",
        f"target_sha:    {snapshot.target_sha or '-'}",
        f"status:        {snapshot.status}",
    ]
    if snapshot.reason:
        lines.append(f"reason:        {snapshot.reason}")
    lines.append("")
    lines.append("| File | Status | Diff |")
    lines.append("|------|--------|------|")
    if snapshot.files:
        for row in snapshot.files:
            if row.status == "changed":
                diff = f"+{row.added or '?'} / -{row.deleted or '?'}"
            elif row.status == "unchanged":
                diff = "0 / 0"
            else:
                diff = row.note or "-"
            lines.append(f"| {row.path} | {row.status} | {diff} |")
    else:
        lines.append("| - | n/a | - |")
    lines.append("")
    lines.append("Result: INFO ONLY (non-blocking)")
    return "\n".join(lines)


def render_markdown(snapshot: Snapshot) -> str:
    lines = [
        "## Drift Snapshot (soft, info-only)",
        "",
        f"- `timestamp_utc`: `{snapshot.timestamp_utc}`",
        f"- `main_ref`: `{snapshot.main_ref}`",
        f"- `target_ref`: `{snapshot.target_ref}`",
        f"- `main_sha`: `{snapshot.main_sha or '-'}`",
        f"- `branch_sha`: `{snapshot.target_sha or '-'}`",
        f"- `status`: `{snapshot.status}`",
    ]
    if snapshot.reason:
        lines.append(f"- `reason`: `{snapshot.reason}`")
    lines.extend([
        "",
        "| File | Status | Diff |",
        "|------|--------|------|",
    ])
    if snapshot.files:
        for row in snapshot.files:
            if row.status == "changed":
                diff = f"+{row.added or '?'} / -{row.deleted or '?'}"
            elif row.status == "unchanged":
                diff = "0 / 0"
            else:
                diff = row.note or "-"
            lines.append(f"| `{row.path}` | `{row.status}` | `{diff}` |")
    else:
        lines.append("| `-` | `n/a` | `-` |")
    lines.extend([
        "",
        "_Info-only. No gatekeeping, no failure condition from drift alone._",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Soft branch drift snapshot (info-only)")
    parser.add_argument("--main-ref", default=DEFAULT_MAIN_REF)
    parser.add_argument("--target-ref", default=DEFAULT_TARGET_REF)
    parser.add_argument("--json-out", help="Write snapshot JSON to file")
    parser.add_argument("--markdown-out", help="Write markdown summary to file")
    args = parser.parse_args()

    snapshot = build_snapshot(args.main_ref, args.target_ref, DEFAULT_FILES)

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(asdict(snapshot), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    if args.markdown_out:
        Path(args.markdown_out).write_text(
            render_markdown(snapshot),
            encoding="utf-8",
        )

    print(render_terminal(snapshot))

    # Always non-blocking by design.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
