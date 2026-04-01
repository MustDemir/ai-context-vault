#!/usr/bin/env python3
"""Liest chapter_state.yaml aus jedem Kapitelordner und aktualisiert die
Fortschrittsbalken in der README.md automatisch.

Fallback: Falls chapter_state.yaml fehlt, wird _status.yml gelesen."""

import pathlib
import re
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Reihenfolge der Kapitelordner (bestimmt Tabellenreihenfolge)
CHAPTER_DIRS = [
    "docs/expose",
    "01_einleitung",
    "02_rigor_theorie_stand_forschung",
    "03_forschungsdesign_methodik",
    "04_anforderungsanalyse_RQ1",
    "05_referenzarchitektur_RQ2",
    "06_evaluation_RQ3",
    "07_diskussion",
    "08_fazit_ausblick",
    "poc",
]

BAR_LENGTH = 20  # Anzahl Bloecke im Balken


def make_bar(percent: int) -> str:
    """Erzeugt einen Unicode-Fortschrittsbalken."""
    filled = round(percent / 100 * BAR_LENGTH)
    empty = BAR_LENGTH - filled
    return "\u2588" * filled + "\u2591" * empty


def load_status(chapter_dir: str) -> dict | None:
    """Liest chapter_state.yaml (bevorzugt) oder _status.yml als Fallback.

    Mergt fehlende Pflichtfelder (kapitel, progress, status) aus _status.yml,
    falls chapter_state.yaml sie nicht enthaelt.
    """
    primary = REPO_ROOT / chapter_dir / "chapter_state.yaml"
    fallback = REPO_ROOT / chapter_dir / "_status.yml"

    data: dict = {}
    if primary.exists():
        with open(primary, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        if isinstance(raw, dict):
            data = raw
    if fallback.exists():
        with open(fallback, encoding="utf-8") as f:
            raw_fb = yaml.safe_load(f)
        if isinstance(raw_fb, dict):
            # Nur fehlende Felder aus _status.yml ergaenzen
            for key in ("kapitel", "progress", "status"):
                if key not in data and key in raw_fb:
                    data[key] = raw_fb[key]

    if not data:
        return None

    # Feld-Normalisierung
    if "kapitel" not in data and "chapter" in data:
        data["kapitel"] = data["chapter"]
    if "progress" not in data and "progress_pct" in data:
        data["progress"] = data["progress_pct"]
    if "progress" not in data:
        data["progress"] = 0
    return data


def build_table(chapters: list[dict]) -> str:
    """Baut die Markdown-Fortschrittstabelle."""
    total = sum(c["progress"] for c in chapters)
    avg = round(total / len(chapters))
    overall_bar = make_bar(avg)

    lines = [
        f"> Gesamtfortschritt: `{overall_bar}` **{avg}%**",
        "",
        "| Kapitel | Fortschritt | % | Status |",
        "|---------|------------|---|--------|",
    ]
    for c in chapters:
        bar = make_bar(c["progress"])
        lines.append(
            f"| {c['kapitel']} | `{bar}` | {c['progress']}% | {c['status']} |"
        )
    return "\n".join(lines)


def update_readme(table: str) -> None:
    """Ersetzt den Fortschritts-Block in der README zwischen den Markern."""
    readme_path = REPO_ROOT / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    marker_start = "<!-- PROGRESS-START -->"
    marker_end = "<!-- PROGRESS-END -->"

    pattern = re.compile(
        re.escape(marker_start) + r".*?" + re.escape(marker_end),
        re.DOTALL,
    )
    replacement = f"{marker_start}\n{table}\n{marker_end}"

    if pattern.search(content):
        new_content = pattern.sub(replacement, content)
    else:
        print("WARNUNG: Marker nicht gefunden — README nicht aktualisiert.")
        print(f"Bitte fuege '{marker_start}' und '{marker_end}' in die README ein.")
        return

    readme_path.write_text(new_content, encoding="utf-8")
    print(f"README aktualisiert — Gesamtfortschritt: {table.splitlines()[0]}")


def main() -> None:
    chapters = []
    for d in CHAPTER_DIRS:
        status = load_status(d)
        if status is None:
            print(f"WARNUNG: {d}/chapter_state.yaml nicht gefunden — uebersprungen.")
            continue
        chapters.append(status)

    if not chapters:
        print("Keine chapter_state.yaml Dateien gefunden.")
        return

    table = build_table(chapters)
    update_readme(table)


if __name__ == "__main__":
    main()
