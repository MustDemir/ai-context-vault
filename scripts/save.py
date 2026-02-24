#!/usr/bin/env python3
"""Create compact session summaries and refresh local context."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from workflow_lib import (
    blob_configured,
    build_index,
    build_resume_text,
    push_index_to_azure,
    push_summaries_to_blob,
    save_session_summary,
    write_index,
    write_resume_text,
)


def _read_input(args: argparse.Namespace) -> str:
    if args.text:
        return args.text.strip()
    if args.input:
        return args.input.read_text(encoding="utf-8", errors="replace").strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit("No input found. Use --text, --input, or pipe.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Path to session notes")
    parser.add_argument("--text", type=str, help="Inline session text")
    parser.add_argument("--topic", type=str, default="auto", help="architecture|requirements|evaluation|methodology|auto")
    parser.add_argument("--title", type=str, default="", help="Short session title")
    parser.add_argument("--source", type=str, default="chat", help="chatgpt|claude|manual")
    parser.add_argument("--tags", type=str, default="", help="Comma-separated tags")
    parser.add_argument("--azure", action="store_true", help="Push to Azure AI Search")
    parser.add_argument("--blob", action="store_true", help="Force Blob sync")
    parser.add_argument("--no-llm", action="store_true", help="Disable Azure OpenAI summary")
    args = parser.parse_args()

    if args.input:
        args.input = Path(args.input)

    text = _read_input(args)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    summary_path, payload = save_session_summary(
        text=text,
        topic=args.topic,
        title=args.title or None,
        source=args.source,
        tags=tags,
        use_llm=not args.no_llm,
    )

    index = build_index()
    index_path = write_index(index)
    resume = build_resume_text(index)
    resume_path = write_resume_text(resume)

    print(f"Summary saved: {summary_path}")
    print(f"Topic routing: {payload.get('target_folder')}")
    print(f"Summary engine: {payload.get('summary_engine')}")
    print(f"Index updated: {index_path}")
    print(f"Resume updated: {resume_path}")

    if args.azure:
        ok, msg = push_index_to_azure(index)
        print(("Azure OK: " if ok else "Azure ERROR: ") + msg)
        if not ok:
            return 2

    if args.blob or blob_configured():
        ok, msg = push_summaries_to_blob()
        print(("Blob OK: " if ok else "Blob ERROR: ") + msg)
        if not ok:
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
