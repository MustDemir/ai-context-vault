# Workflow Output Schema

> Spezifikation aller Artefakte, die von Scripts und Skills erzeugt werden.

---

## Scripts (Python-Workflow)

| Script | Output-Datei | Pfad-Muster | Git | Beschreibung |
|--------|-------------|-------------|-----|-------------|
| save.py | Session Summary | `{KK}_*/session_summaries/YYYYMMDD_*.yaml` | .gitignore | Kompakte YAML-Summary pro Session |
| resume.py | Resume Context | `.memory/resume_context.txt` | .gitignore | Aggregierter Kontext fuer Session-Start |
| resume.py | Thesis State | `docs/thesis_state.md` | TRACKED | Generierte SSOT-Momentaufnahme |
| reindex.py | Index | `.memory/index.json` | .gitignore | Lokaler Suchindex |

## Skills (Cowork-Workflow)

| Skill | Output-Datei | Pfad-Muster | Git | Beschreibung |
|-------|-------------|-------------|-----|-------------|
| thesis-preflight | Preflight-Protokoll | `docs/preflight/PREFLIGHT_KAP{N}_*.md` | TRACKED | Argumentationsstruktur + Checkliste |
| thesis-reviewer | Bewertungsbericht | `docs/bewertung/BEWERTUNG_KAP{N}_*.md` | TRACKED | Review mit Scoring (R1–R6) |
| thesis-post-session | Post-Session-Bericht | `docs/post_session/POST_SESSION_*.md` | TRACKED | Verifikation Repo-Artefakte |
| thesis-consistency | Konsistenz-Report | `docs/consistency/CONSISTENCY_REPORT_*.md` | TRACKED | K1–K7 Pruefergebnis |
| evidence-matrix-builder | Evidenz-Matrix | `docs/Evidenz/EVIDENZ_MATRIX_*.md` + `.html` | TRACKED | Quellen-Abdeckungsanalyse |

## Datei-Hierarchie nach Relevanz

| Tier | Dateien | Rolle |
|------|---------|-------|
| **Kritisch (SSOT)** | chapter_state.yaml, thesis_state.md, roter_faden_tracker.md, pruefkatalog.md | Primaere Wahrheit |
| **Hoch (QA)** | Preflight, Bewertung, Consistency, Post-Session | Qualitaetssicherung |
| **Mittel (Kontext)** | Session Summaries, Evidenz-Matrizen | Nachvollziehbarkeit |
| **Optional** | .memory/*, Diagramme, Legacy | Lokaler Cache, Archiv |
