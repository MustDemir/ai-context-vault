#!/usr/bin/env python3
"""
resume.py – Generate Token-Optimized Context for New AI Sessions

THE CORE INNOVATION: Reduces context from ~30,000 tokens to ~600 tokens (98% savings).

Reads project artifacts (YAML, MD) and produces a compact summary that can be
pasted into any AI model (Claude, ChatGPT, Gemini, etc.) to resume work.

Features:
- Chapter-based filtering (e.g., `resume.py 04` for chapter 4 only)
- Auto-copy to clipboard (macOS pbcopy)
- Structured output: status, requirements, gates, key info
- Works with any AI model – no vendor lock-in

Usage:
    python3 scripts/resume.py           # Full project context
    python3 scripts/resume.py 04        # Chapter 4 only
    python3 scripts/resume.py --no-copy # Don't copy to clipboard

Token Cost: $0 (no API calls – local file parsing only)
"""

import os
import sys
import glob
import yaml
import subprocess
import argparse
from datetime import datetime


def load_yaml(path: str) -> dict:
    """Safely load a YAML file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def find_project_root() -> str:
    """Find project root (directory containing .env or .git)."""
    cwd = os.getcwd()
    for marker in [".env", ".git"]:
        check = os.path.join(cwd, marker)
        if os.path.exists(check):
            return cwd
    # Try parent
    parent = os.path.dirname(cwd)
    for marker in [".env", ".git"]:
        if os.path.exists(os.path.join(parent, marker)):
            return parent
    return cwd


def extract_chapter_states(root: str, chapter_filter: str = None) -> list:
    """Extract status from all chapter_state.yaml files."""
    states = []
    pattern = os.path.join(root, "**/chapter_state.yaml")
    for path in sorted(glob.glob(pattern, recursive=True)):
        data = load_yaml(path)
        chapter = os.path.basename(os.path.dirname(path))

        if chapter_filter and not chapter.startswith(chapter_filter):
            continue

        states.append(
            {
                "chapter": chapter,
                "status": data.get("status", "unknown"),
                "title": data.get("title", chapter),
                "progress": data.get("progress_pct", 0),
            }
        )
    return states


def extract_requirements(root: str, chapter_filter: str = None) -> list:
    """Extract requirements from YAML files."""
    reqs = []
    pattern = os.path.join(root, "**/requirements/*.yaml")
    for path in sorted(glob.glob(pattern, recursive=True)):
        data = load_yaml(path)
        if not data:
            continue

        chapter_dir = os.path.basename(
            os.path.dirname(os.path.dirname(path))
        )
        if chapter_filter and not chapter_dir.startswith(chapter_filter):
            continue

        req_id = data.get("id", os.path.basename(path).replace(".yaml", ""))
        title = data.get("title", "")
        status = "filled" if title else "empty"

        reqs.append({"id": req_id, "title": title, "status": status})
    return reqs


def extract_gates(root: str) -> list:
    """Extract quality gates from YAML files."""
    gates = []
    for gate_type in ["strategic", "technical", "compliance"]:
        pattern = os.path.join(root, f"**/{gate_type}/*.yaml")
        for path in sorted(glob.glob(pattern, recursive=True)):
            data = load_yaml(path)
            if not data:
                continue

            gate_id = data.get("id", os.path.basename(path).replace(".yaml", ""))
            title = data.get("title", data.get("name", ""))
            status = "filled" if title else "empty"

            gates.append(
                {
                    "id": gate_id,
                    "type": gate_type,
                    "title": title,
                    "status": status,
                }
            )
    return gates


def build_context(root: str, chapter_filter: str = None) -> str:
    """Build compact context string."""
    lines = []
    lines.append("=" * 50)
    lines.append("AI CONTEXT VAULT – Session Resume")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if chapter_filter:
        lines.append(f"Filter: Chapter {chapter_filter}")
    lines.append("=" * 50)

    # Chapter states
    states = extract_chapter_states(root, chapter_filter)
    if states:
        lines.append("\n## Kapitel-Status:")
        for s in states:
            icon = "✅" if s["status"] == "done" else "🔄" if s["progress"] > 0 else "⬜"
            lines.append(f"  {icon} {s['chapter']}: {s['title']} ({s['progress']}%)")

    # Requirements
    reqs = extract_requirements(root, chapter_filter)
    if reqs:
        filled = sum(1 for r in reqs if r["status"] == "filled")
        lines.append(f"\n## Requirements: {filled}/{len(reqs)} filled")
        for r in reqs:
            icon = "✅" if r["status"] == "filled" else "⬜"
            title = r["title"] if r["title"] else "(empty)"
            lines.append(f"  {icon} {r['id']}: {title}")

    # Gates
    gates = extract_gates(root)
    if gates:
        filled = sum(1 for g in gates if g["status"] == "filled")
        lines.append(f"\n## Quality Gates: {filled}/{len(gates)} filled")
        for g in gates:
            icon = "✅" if g["status"] == "filled" else "⬜"
            title = g["title"] if g["title"] else "(empty)"
            lines.append(f"  {icon} [{g['type'][:4].upper()}] {g['id']}: {title}")

    # Token count estimate
    context = "\n".join(lines)
    token_est = len(context.split()) * 1.3  # rough estimate
    lines.append(f"\n---\n~{int(token_est)} tokens (vs ~30,000 full context = {int((1 - token_est/30000) * 100)}% savings)")

    return "\n".join(lines)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to macOS clipboard."""
    try:
        process = subprocess.Popen(
            ["pbcopy"], stdin=subprocess.PIPE, stderr=subprocess.PIPE
        )
        process.communicate(text.encode("utf-8"))
        return process.returncode == 0
    except FileNotFoundError:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate token-optimized context for AI sessions"
    )
    parser.add_argument(
        "chapter", nargs="?", default=None, help="Filter by chapter (e.g., 04)"
    )
    parser.add_argument(
        "--no-copy", action="store_true", help="Don't copy to clipboard"
    )
    parser.add_argument(
        "--path", default=None, help="Project root path"
    )
    args = parser.parse_args()

    root = args.path or find_project_root()
    context = build_context(root, args.chapter)

    print(context)

    if not args.no_copy:
        if copy_to_clipboard(context):
            print("\n📋 Copied to clipboard! Paste into any AI chat to resume.")
        else:
            print("\n⚠️  Clipboard copy failed (pbcopy not available)")


if __name__ == "__main__":
    main()
