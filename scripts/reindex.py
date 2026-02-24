#!/usr/bin/env python3
"""Rebuild local index/resume and optionally sync to Azure Search + Blob."""

from __future__ import annotations

import argparse

from workflow_lib import (
    azure_configured,
    blob_configured,
    build_index,
    build_resume_text,
    push_index_to_azure,
    push_summaries_to_blob,
    write_index,
    write_resume_text,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--azure", action="store_true", help="Force Azure AI Search push")
    parser.add_argument("--no-azure", action="store_true", help="Disable Azure push")
    parser.add_argument("--blob", action="store_true", help="Force Blob sync")
    parser.add_argument("--no-blob", action="store_true", help="Disable Blob sync")
    args = parser.parse_args()

    index = build_index()
    index_path = write_index(index)
    resume_path = write_resume_text(build_resume_text(index))

    print(f"Index updated: {index_path}")
    print(f"Resume context updated: {resume_path}")
    print(f"Indexed files: {len(index.get('files', []))}")
    print(f"Session summaries: {len(index.get('session_summaries', []))}")

    do_azure = False
    if not args.no_azure:
        do_azure = args.azure or azure_configured()

    if do_azure:
        ok, msg = push_index_to_azure(index)
        print(("Azure OK: " if ok else "Azure ERROR: ") + msg)
        if not ok:
            return 2
    else:
        print("Azure push skipped.")

    do_blob = False
    if not args.no_blob:
        do_blob = args.blob or blob_configured()

    if do_blob:
        ok, msg = push_summaries_to_blob()
        print(("Blob OK: " if ok else "Blob ERROR: ") + msg)
        if not ok:
            return 3
    else:
        print("Blob sync skipped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
