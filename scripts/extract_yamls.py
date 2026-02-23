#!/usr/bin/env python3
"""
extract_yamls.py – AI-Powered Artifact Extraction from Chat Transcripts

Uses Claude API to intelligently parse unstructured chat text and extract
structured YAML artifacts (Requirements, Quality Gates).

Features:
- Reads chapter state files and YAML templates
- Claude analyzes chat transcripts for requirements/gates
- Generates R### (Requirements) and G### (Gates) files
- Prevents duplicates by checking existing IDs
- Updates chapter progress tracking

Usage:
    python3 scripts/extract_yamls.py --input chat.txt --chapter 04
    python3 scripts/extract_yamls.py --input chat.txt --type requirements
    python3 scripts/extract_yamls.py --input chat.txt --type gates

Token Cost: ~0.05-0.20$ per extraction (Claude API)
"""

import os
import sys
import glob
import yaml
import argparse
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-20250514"


# ── Templates ─────────────────────────────────────────────

REQUIREMENT_TEMPLATE = """id: "{req_id}"
title: "{title}"
description: "{description}"
source: "{source}"
category: "{category}"
priority: "must"
status: "draft"
chapter: "{chapter}"
created: "{date}"
"""

GATE_TEMPLATE = """id: "{gate_id}"
title: "{title}"
dimension: "{dimension}"
phase: "{phase}"
trigger: "{trigger}"
criteria: "{criteria}"
evidence: "{evidence}"
decision: "Go/NoGo"
status: "draft"
created: "{date}"
"""


def find_existing_ids(root: str) -> set:
    """Find all existing requirement/gate IDs to prevent duplicates."""
    ids = set()
    for pattern in ["**/requirements/*.yaml", "**/gates/**/*.yaml"]:
        for path in glob.glob(os.path.join(root, pattern), recursive=True):
            try:
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
                    if data and "id" in data:
                        ids.add(data["id"])
            except Exception:
                pass
    return ids


def extract_with_claude(chat_text: str, extract_type: str, existing_ids: set) -> list:
    """Use Claude to extract structured artifacts from chat text."""
    if not ANTHROPIC_KEY:
        print("❌ ANTHROPIC_API_KEY required in .env")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    if extract_type == "requirements":
        prompt = (
            "Analysiere den folgenden Chat-Text und extrahiere ALLE Anforderungen "
            "(Requirements) für eine GenAI-Referenzarchitektur.\n\n"
            "Für jede Anforderung gib zurück (als JSON-Array):\n"
            "- title: Kurztitel\n"
            "- description: Beschreibung\n"
            "- category: technical|organizational|regulatory\n"
            "- source: Quelle (Paper, EU AI Act Artikel, etc.)\n\n"
            f"Bereits existierende IDs (NICHT erneut extrahieren): {existing_ids}\n\n"
            f"Chat-Text:\n{chat_text[:15000]}"
        )
    else:
        prompt = (
            "Analysiere den folgenden Chat-Text und extrahiere ALLE Quality Gates "
            "für eine GenAI-Referenzarchitektur.\n\n"
            "Für jedes Gate gib zurück (als JSON-Array):\n"
            "- title: Gate-Name\n"
            "- dimension: strategic|technical|compliance\n"
            "- phase: data|model|eval|deploy|prod|retire\n"
            "- trigger: Auslöser\n"
            "- criteria: Prüfkriterien\n"
            "- evidence: Erforderliche Artefakte\n\n"
            f"Bereits existierende IDs (NICHT erneut extrahieren): {existing_ids}\n\n"
            f"Chat-Text:\n{chat_text[:15000]}"
        )

    message = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    # Parse Claude's response (expects JSON-like output)
    response_text = message.content[0].text
    try:
        import json
        # Try to find JSON array in response
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(response_text[start:end])
    except Exception:
        pass

    print("⚠️  Could not parse Claude's response as JSON")
    print(response_text[:500])
    return []


def save_artifacts(artifacts: list, extract_type: str, chapter: str, root: str):
    """Save extracted artifacts as YAML files."""
    date = datetime.now().strftime("%Y-%m-%d")

    if extract_type == "requirements":
        output_dir = os.path.join(root, f"{chapter}/requirements")
        os.makedirs(output_dir, exist_ok=True)

        # Find next ID
        existing = glob.glob(os.path.join(output_dir, "R*.yaml"))
        next_num = len(existing) + 1

        for item in artifacts:
            req_id = f"R{next_num:03d}"
            content = REQUIREMENT_TEMPLATE.format(
                req_id=req_id,
                title=item.get("title", ""),
                description=item.get("description", ""),
                source=item.get("source", ""),
                category=item.get("category", "technical"),
                chapter=chapter,
                date=date,
            )
            filepath = os.path.join(output_dir, f"{req_id}.yaml")
            with open(filepath, "w") as f:
                f.write(content)
            print(f"   ✅ {req_id}: {item.get('title', '')}")
            next_num += 1

    elif extract_type == "gates":
        for item in artifacts:
            dimension = item.get("dimension", "technical")
            dim_short = {"strategic": "GSTR", "technical": "GTECH", "compliance": "GCOMP"}.get(
                dimension, "GTECH"
            )
            output_dir = os.path.join(root, "quality-gates", dimension)
            os.makedirs(output_dir, exist_ok=True)

            existing = glob.glob(os.path.join(output_dir, f"{dim_short}-*.yaml"))
            next_num = len(existing) + 1
            gate_id = f"{dim_short}-{next_num:03d}"

            content = GATE_TEMPLATE.format(
                gate_id=gate_id,
                title=item.get("title", ""),
                dimension=dimension,
                phase=item.get("phase", ""),
                trigger=item.get("trigger", ""),
                criteria=item.get("criteria", ""),
                evidence=item.get("evidence", ""),
                date=date,
            )
            filepath = os.path.join(output_dir, f"{gate_id}.yaml")
            with open(filepath, "w") as f:
                f.write(content)
            print(f"   ✅ {gate_id}: {item.get('title', '')}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured artifacts from chat transcripts"
    )
    parser.add_argument("--input", required=True, help="Path to chat transcript")
    parser.add_argument(
        "--type",
        choices=["requirements", "gates"],
        default="requirements",
        help="Type of artifacts to extract",
    )
    parser.add_argument("--chapter", default="04", help="Chapter directory")
    parser.add_argument("--path", default=os.getcwd(), help="Project root")
    args = parser.parse_args()

    root = os.path.abspath(args.path)

    print("=" * 60)
    print("  AI Context Vault – Artifact Extraction")
    print("=" * 60)

    # Read chat transcript
    with open(args.input, "r", encoding="utf-8") as f:
        chat_text = f.read()
    print(f"📄 Chat geladen: {len(chat_text)} Zeichen")

    # Find existing IDs
    existing_ids = find_existing_ids(root)
    print(f"🔍 {len(existing_ids)} bestehende Artefakte gefunden")

    # Extract with Claude
    print(f"\n🤖 Claude extrahiert {args.type}...")
    artifacts = extract_with_claude(chat_text, args.type, existing_ids)
    print(f"   {len(artifacts)} neue {args.type} gefunden\n")

    # Save
    if artifacts:
        save_artifacts(artifacts, args.type, args.chapter, root)
        print(f"\n✅ {len(artifacts)} {args.type} gespeichert!")
    else:
        print("ℹ️  Keine neuen Artefakte gefunden.")


if __name__ == "__main__":
    main()
