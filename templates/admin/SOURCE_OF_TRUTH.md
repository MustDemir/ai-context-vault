# Source of Truth

Dieses Dokument definiert verbindlich, welche Artefakte als primaere Wahrheit gelten
und welche nur abgeleitet/legacy sind.

## Primaere Quellen

- Operativer Einstiegspunkt (Workspace):
  - `00_workspace/`
- Expose / Projektantrag (primaer):
  - `00_admin/<PROJEKT_EXPOSE>.pdf` (abgegebene Version, SSOT im Repo)
- Gliederung (primaer):
  - `00_admin/gliederung.md`
- Kapitel-Volltexte (primaer, Abgabe-Texte):
  - `00_workspace/Fulltext_Kapitel/*.docx`
  - Bei Abweichungen zwischen DRAFT.md und DOCX gilt die DOCX

## Kapitelordner: Ordnungsregel

- Kapitelwurzel bleibt schlank: `chapter_state.yaml`, `images/`, `session_summaries/`
- Lose Arbeitsdateien kapitel-lokal unter `arbeitsmaterial/`
- Bereits einsortierte Dateien bleiben in bestehenden Unterordnern

## Vorgaben und Stilrichtlinien (bindend)

- Ordner: `docs/uni_vorgaben/`
- Enthaltene Dokumente:
  - `<STILRICHTLINIEN>.docx` — Bindende Stilregeln fuer alle Kapitel
  - `<BEWERTUNGSKRITERIEN>.pdf` — Struktur- und Formalia-Anforderungen
- Verwendung:
  - **Preflight-Checks**: Beide Dokumente als Pruefinstanz
  - **Consistency-Check**: Formalia-Abgleich gegen Bewertungskriterien
  - **Post-Session**: Stil-Compliance als Pruefpunkt
- Roter Faden Tracker (primaer):
  - `docs/roter_faden_tracker.md`
- Pruefkatalog (primaer):
  - `docs/uni_vorgaben/pruefkatalog.md`

## Fortschritts- und Tracking-Artefakte

| Kategorie | Pfad-Muster | Zweck | Git-Status |
|-----------|-------------|-------|-----------|
| **chapter_state.yaml** | `{KK}_*/chapter_state.yaml` | Kapitel-Status: progress, done, next_steps, decisions | TRACKED |
| **Preflight-Protokolle** | `docs/preflight/PREFLIGHT_KAP{N}_*.md` | Argumentationsstruktur, Quellen-Zuordnung, Negativ-Checklisten | TRACKED |
| **Bewertungsberichte** | `docs/bewertung/BEWERTUNG_KAP{N}_*.md` | Reviews mit Scoring | TRACKED |
| **Session Summaries** | `{KK}_*/session_summaries/*.yaml` | Per-Session YAML (via save.py) | .gitignore |
| **.memory/** | `.memory/` | Lokaler Cache, Sync-States | .gitignore |

## Status-Enum (verbindlich fuer alle Artefakte)

```
planned → in_progress → draft → review → final
```

## Session Summary Regeln

- `*/session_summaries/` enthaelt nur `*.yaml`
- Rohmaterial unter `99_inbox_unsorted/raw/`

## Cloud/RAG Betriebsmodell

- Blob ist getrennt per Container
- Azure Search mit Metadaten: `repo_scope`, `summary_type`, `source_repo`
