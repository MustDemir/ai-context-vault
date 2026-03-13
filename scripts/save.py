#!/usr/bin/env python3
"""Create compact session summaries and refresh local context."""

from __future__ import annotations

import argparse
import subprocess
import sys

from pathlib import Path

import yaml

from workflow_lib import (
    REPO_ROOT,
    TOPIC_TO_DIR,
    build_index,
    build_resume_text,
    blob_configured,
    push_index_to_azure,
    push_summaries_to_blob,
    save_session_summary,
    write_index,
    write_resume_text,
)


def _topic_to_status_path(topic: str) -> Path | None:
    """Resolve topic to its chapter_state.yaml path."""
    session_dir = TOPIC_TO_DIR.get(topic)
    if not session_dir:
        return None
    chapter_dir = REPO_ROOT / Path(session_dir).parent
    return chapter_dir / "chapter_state.yaml"


def _offer_progress_update(topic: str) -> None:
    """Ask the user if chapter progress should be updated."""
    status_path = _topic_to_status_path(topic)
    if not status_path:
        return

    if status_path.exists():
        data = yaml.safe_load(status_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
        current = data.get("progress", data.get("progress_pct", 0))
        kapitel = data.get("kapitel", data.get("chapter", topic))
        status = data.get("status", "")
        print(f"\n--- Fortschritt: {kapitel} ---")
        print(f"Aktuell: {current}% — {status}")
    else:
        data = {}
        current = 0
        kapitel = topic
        print(f"\n--- Noch keine chapter_state.yaml fuer '{topic}' ---")
        print(f"Aktuell: {current}%")

    if not sys.stdin.isatty():
        return

    answer = input("Neuer Fortschritt (% eingeben, Enter = keine Aenderung): ").strip()
    if not answer:
        print("Fortschritt nicht geaendert.")
        return

    try:
        new_progress = int(answer)
    except ValueError:
        print("Ungueltige Eingabe, Fortschritt nicht geaendert.")
        return

    if new_progress == current:
        print("Fortschritt unveraendert.")
        return

    new_status = input("Status-Text (Enter = bisherig): ").strip()
    if not new_status:
        new_status = data.get("status", "In Arbeit") if data else "In Arbeit"

    # Merge: bestehende chapter_state.yaml erhalten, nur progress/status updaten
    if status_path.exists() and data:
        data["progress"] = new_progress
        if "progress_pct" in data:
            data["progress_pct"] = new_progress
        data["status"] = new_status
        status_path.write_text(
            yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
    else:
        # Fallback: minimale Datei erstellen
        status_data = {
            "kapitel": kapitel if data else topic,
            "progress": new_progress,
            "status": new_status,
        }
        status_path.parent.mkdir(parents=True, exist_ok=True)
        content = f"# Fortschritt: {status_data['kapitel']}\n"
        content += yaml.dump(status_data, allow_unicode=True, default_flow_style=False)
        status_path.write_text(content, encoding="utf-8")

    print(f"Fortschritt aktualisiert: {new_progress}% — {new_status}")

    # README gleich mit aktualisieren
    try:
        subprocess.run(
            [sys.executable, "scripts/update_progress.py"],
            cwd=str(REPO_ROOT),
            check=True,
        )
    except Exception as exc:
        print(f"README-Update fehlgeschlagen: {exc}")


def _read_input(args: argparse.Namespace) -> str:
    if args.text:
        return args.text.strip()
    if args.input:
        return args.input.read_text(encoding="utf-8", errors="replace").strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit("Kein Input gefunden. Nutze --text, --input oder Pipe.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Pfad zu Session-Notizen/Text")
    parser.add_argument("--text", type=str, help="Direkter Session-Text")
    parser.add_argument(
        "--topic",
        type=str,
        default="auto",
        help="z. B. architektur, anforderungen, theorie, evaluation, methodik, auto",
    )
    parser.add_argument("--title", type=str, default="", help="Kurzer Titel der Session")
    parser.add_argument("--source", type=str, default="chat", help="Quelle, z. B. chatgpt/claude/manual")
    parser.add_argument("--tags", type=str, default="", help="Kommagetrennte Tags")
    parser.add_argument("--azure", action="store_true", help="Direkt nach Azure AI Search pushen")
    parser.add_argument("--blob", action="store_true", help="Direkt nach Blob syncen")
    parser.add_argument("--no-llm", action="store_true", help="Keine Azure-OpenAI-Summary, nur lokale Regeln")
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

    print(f"Summary gespeichert: {summary_path}")
    print(f"Topic-Routing: {payload.get('target_folder')}")
    print(f"Summary-Engine: {payload.get('summary_engine')}")
    print(f"Index aktualisiert: {index_path}")
    print(f"Resume aktualisiert: {resume_path}")

    if args.azure:
        ok, msg = push_index_to_azure(index)
        prefix = "Azure OK" if ok else "Azure FEHLER"
        print(f"{prefix}: {msg}")
        if not ok:
            return 2

    if args.blob or blob_configured():
        ok, msg = push_summaries_to_blob()
        prefix = "Blob OK" if ok else "Blob FEHLER"
        print(f"{prefix}: {msg}")
        if not ok:
            return 3

    # --- Fortschritt-Update anbieten ---
    topic = payload.get("topic", "general")
    _offer_progress_update(topic)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
