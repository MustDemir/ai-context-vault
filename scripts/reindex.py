#!/usr/bin/env python3
from __future__ import annotations

import argparse

from workflow_lib import (
    azure_configured,
    blob_configured,
    build_index,
    build_resume_text,
    input_blob_sync_enabled,
    push_index_to_azure,
    push_input_files_to_blob,
    push_summaries_to_blob,
    write_index,
    write_resume_text,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--azure", action="store_true", help="Azure AI Search Push erzwingen")
    parser.add_argument("--no-azure", action="store_true", help="Kein Azure Push")
    parser.add_argument("--blob", action="store_true", help="Blob Sync erzwingen")
    parser.add_argument("--no-blob", action="store_true", help="Kein Blob Sync")
    parser.add_argument("--input-blob", action="store_true", help="Input-Dateien nach Blob syncen")
    parser.add_argument("--no-input-blob", action="store_true", help="Input-Dateien nicht nach Blob syncen")
    args = parser.parse_args()

    index = build_index()
    index_path = write_index(index)
    resume = build_resume_text(index)
    resume_path = write_resume_text(resume)

    print(f"Index aktualisiert: {index_path}")
    print(f"Resume-Kontext aktualisiert: {resume_path}")
    print(f"Dateien indexiert: {len(index.get('files', []))}")
    print(f"Session-Summaries: {len(index.get('session_summaries', []))}")

    do_azure = False
    if not args.no_azure:
        do_azure = args.azure or azure_configured()

    if do_azure:
        ok, msg = push_index_to_azure(index)
        print(("Azure OK: " if ok else "Azure FEHLER: ") + msg)
        if not ok:
            return 2
    else:
        print("Azure Push uebersprungen (kein --azure oder Konfiguration fehlt).")

    do_blob = False
    if not args.no_blob:
        do_blob = args.blob or blob_configured()

    if do_blob:
        ok, msg = push_summaries_to_blob()
        print(("Blob OK: " if ok else "Blob FEHLER: ") + msg)
        if not ok:
            return 3
    else:
        print("Blob Sync uebersprungen (kein --blob oder Konfiguration fehlt).")

    do_input_blob = False
    if not args.no_input_blob:
        do_input_blob = args.input_blob or input_blob_sync_enabled()

    if do_input_blob:
        ok, msg = push_input_files_to_blob()
        print(("Input-Blob OK: " if ok else "Input-Blob FEHLER: ") + msg)
        if not ok:
            return 4
    else:
        print("Input-Blob Sync uebersprungen (kein --input-blob oder AZURE_INPUT_BLOB_SYNC=1).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
