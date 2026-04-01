#!/usr/bin/env python3
"""
generate_html.py — Evidence-Matrix HTML Generator
Befüllt matrix_template.html mit JSON-Daten und erzeugt eine fertige HTML-Evidenz-Matrix.

Usage:
  python3 generate_html.py --template assets/matrix_template.html --data data.json --output output.html
  python3 generate_html.py --template assets/matrix_template.html --data '{"kapitel":"Kap. 2.4"}' --output out.html

JSON-Struktur:
{
  "kapitel":      "Kap. 2.4.2",
  "titel":        "EU AI Act: Regulatorischer Rahmen",
  "datum":        "2026-03-13",
  "budget":       "450W",
  "n_pdfs":       12,
  "questions": [
    {"id": "Q1", "text": "Frage mit <strong>Begriff</strong>?", "target": "Absatz 1: Thema"}
  ],
  "tier1": [
    {"author": "Sinha et al.", "year": "2024",
     "ratings": {"Q1": "deep", "Q2": "mod", "Q3": "mention", "Q4": "none"},
     "role": "Primärquelle für GenAIOps-Systematik"}
  ],
  "tier2": [ ... gleiche Struktur wie tier1 ... ],
  "tier3": [
    {"author": "Autor", "year": "2023", "target_chapter": "Kap. 5", "reason": "Begründung"}
  ],
  "evidence_strength": [
    {"question": "Q1", "strength": "STARK", "deep": 3, "mod": 2, "mention": 1, "paragraph": "Abs. 1"}
  ],
  "synthesis": [
    {"paragraph": "Abs. 1", "claim": "Aussage ...", "primary": "Autor (2024)", "secondary": "Autor2 (2023)"}
  ],
  "next_step": "Evidenz-Matrix bestätigt → GO für thesis-writer"
}

Rating-Werte: "deep" | "mod" | "mention" | "none"
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import date


RATING_MAP = {
    "deep":    ("🟢", "cell-deep"),
    "mod":     ("🟠", "cell-mod"),
    "mention": ("🟡", "cell-mention"),
    "none":    ("⬛", "cell-none"),
    "":        ("⬛", "cell-none"),
}

STRENGTH_MAP = {
    "STARK":    ("ev-strong",   "STARK"),
    "MODERAT":  ("ev-moderate", "MODERAT"),
    "SCHWACH":  ("ev-weak",     "SCHWACH"),
}


def build_question_cards(questions):
    cards = []
    for q in questions:
        cards.append(
            f'  <div class="q-card">\n'
            f'    <div class="q-id">{q["id"]}</div>\n'
            f'    <div class="q-text">{q["text"]}</div>\n'
            f'    <div class="q-target">→ {q.get("target","")}</div>\n'
            f'  </div>'
        )
    return "\n".join(cards)


def build_question_headers(questions):
    return "".join(f"<th>{q['id']}</th>" for q in questions)


def build_source_rows(sources, questions, tier_badge):
    rows = []
    for i, src in enumerate(sources, 1):
        badge_class = {"CORE": "badge-core", "EMPFOHLEN": "badge-rec"}.get(tier_badge, "badge-core")
        cells = ""
        for q in questions:
            rating_key = src.get("ratings", {}).get(q["id"], "none")
            symbol, css = RATING_MAP.get(rating_key, ("⬛", "cell-none"))
            cells += f'<td class="{css}">{symbol}</td>'
        rows.append(
            f'<tr>'
            f'<td>{i}</td>'
            f'<td><span class="source-name">{src["author"]}</span> '
            f'<span class="source-year">({src["year"]})</span><br>'
            f'<span class="badge {badge_class}">{tier_badge}</span></td>'
            f'{cells}'
            f'<td class="role-cell">{src.get("role","")}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def build_evidence_strength_rows(ev_data):
    rows = []
    for ev in ev_data:
        dot_class, label = STRENGTH_MAP.get(ev["strength"], ("ev-weak", ev["strength"]))
        rows.append(
            f'<tr>'
            f'<td>{ev["question"]}</td>'
            f'<td><div class="ev-bar"><div class="ev-dot {dot_class}"></div>'
            f'<span class="ev-label">{label}</span></div></td>'
            f'<td>{ev.get("deep", 0)}</td>'
            f'<td>{ev.get("mod", 0)}</td>'
            f'<td>{ev.get("mention", 0)}</td>'
            f'<td>{ev.get("paragraph","")}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def build_synthesis_rows(synthesis):
    rows = []
    for s in synthesis:
        rows.append(
            f'<tr>'
            f'<td>{s.get("paragraph","")}</td>'
            f'<td>{s.get("claim","")}</td>'
            f'<td>{s.get("primary","")}</td>'
            f'<td>{s.get("secondary","—")}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def build_tier3_rows(tier3):
    rows = []
    for i, src in enumerate(tier3, 1):
        rows.append(
            f'<tr>'
            f'<td>{i}</td>'
            f'<td><span class="source-name">{src["author"]}</span> ({src["year"]})</td>'
            f'<td>{src.get("target_chapter","")}</td>'
            f'<td>{src.get("reason","")}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def fill_template(template_str, data):
    questions = data.get("questions", [])
    tier1 = data.get("tier1", [])
    tier2 = data.get("tier2", [])
    tier3 = data.get("tier3", [])

    n_tier12 = len(tier1) + len(tier2)
    n_cells  = (len(tier1) + len(tier2)) * len(questions)

    replacements = {
        "{{KAPITEL}}":               data.get("kapitel", ""),
        "{{TITEL}}":                 data.get("titel", ""),
        "{{DATUM}}":                 data.get("datum", str(date.today())),
        "{{BUDGET}}":                str(data.get("budget", "")),
        "{{N_PDFS}}":                str(data.get("n_pdfs", len(tier1)+len(tier2)+len(tier3))),
        "{{N_TIER12}}":              str(n_tier12),
        "{{N_QUESTIONS}}":           str(len(questions)),
        "{{N_CELLS}}":               str(n_cells),
        "{{QUESTION_CARDS}}":        build_question_cards(questions),
        "{{QUESTION_HEADERS}}":      build_question_headers(questions),
        "{{TIER1_ROWS}}":            build_source_rows(tier1, questions, "CORE"),
        "{{TIER2_ROWS}}":            build_source_rows(tier2, questions, "EMPFOHLEN"),
        "{{EVIDENCE_STRENGTH_ROWS}}": build_evidence_strength_rows(data.get("evidence_strength", [])),
        "{{SYNTHESIS_ROWS}}":        build_synthesis_rows(data.get("synthesis", [])),
        "{{TIER3_ROWS}}":            build_tier3_rows(tier3),
        "{{NEXT_STEP}}":             data.get("next_step", "Evidence-Matrix bestätigt → GO für thesis-writer"),
    }

    result = template_str
    for key, value in replacements.items():
        result = result.replace(key, value)
    return result


def main():
    parser = argparse.ArgumentParser(description="Evidence-Matrix HTML Generator")
    parser.add_argument("--template", required=True, help="Pfad zur matrix_template.html")
    parser.add_argument("--data", required=True, help="JSON-Datei oder JSON-String")
    parser.add_argument("--output", required=True, help="Output-HTML-Pfad")
    args = parser.parse_args()

    # Load template
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"ERROR: Template nicht gefunden: {template_path}", file=sys.stderr)
        sys.exit(1)
    template_str = template_path.read_text(encoding="utf-8")

    # Load data
    data_arg = args.data.strip()
    if data_arg.startswith("{"):
        data = json.loads(data_arg)
    else:
        data_file = Path(data_arg)
        if not data_file.exists():
            print(f"ERROR: Datendatei nicht gefunden: {data_file}", file=sys.stderr)
            sys.exit(1)
        data = json.loads(data_file.read_text(encoding="utf-8"))

    # Fill and write
    output_html = fill_template(template_str, data)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_html, encoding="utf-8")
    print(f"✅ HTML generiert: {output_path}")


if __name__ == "__main__":
    main()
