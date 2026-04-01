# Templates — Starter-Kit fuer neue Projekte

Diese Templates sind generische Schemata (ohne projektspezifischen Inhalt),
abgeleitet aus dem produktiven Einsatz im GenAIOps-Thesis-Projekt (100+ Sessions).

## Verwendung

Siehe `chapter/project_scaffold.md` fuer eine Schritt-fuer-Schritt-Anleitung.

## Inhalt

### admin/ — Projektsteuerung und Governance

| Template | Zweck | Referenziert von |
|----------|-------|-----------------|
| `README.md` | Projekt-Dashboard mit Fortschrittstabelle | session-manager (S1) |
| `SOURCE_OF_TRUTH.md` | Definiert primaere Artefakte und Ordnungsregeln | Alle Skills |
| `WORKFLOW_PLAYBOOK.md` | Operative Anleitung: Save, Resume, Reindex | Session-Start/Ende |
| `gliederung.md` | Kapitelstruktur mit Seitenbudgets (bindend) | preflight (P1), reviewer (R1) |
| `asset_naming.md` | Namenskonvention fuer Abbildungen | Dateierstellung |

### docs/ — SSOTs, QA-Artefakte und Tracking

| Template | Zweck | Referenziert von |
|----------|-------|-----------------|
| `roter_faden_tracker.md` | Kapiteluebergreifende Argumentationskette | preflight (P2), reviewer (R2) |
| `pruefkatalog.md` | Maschinenlesbare Compliance-Checkliste (PK-Codes) | Alle QA-Skills |
| `entscheidungsregister.md` | Kapiteluebergreifendes Decision-Register | preflight (P4), consistency (K2) |
| `entscheidungspapier.md` | Kapitel-spezifische Design-Entscheidungen | lade_manifest (pflicht) |
| `WORKFLOW_OUTPUT_SCHEMA.md` | Spezifikation aller Script/Skill-Outputs | Wartung |
| `uni_vorgaben/WORKFLOW_INTEGRATION.md` | Skill-spezifische Pruefpunkte aus Vorgaben | Alle Skills (P6, R3, K7) |
| `consistency/README_CONSISTENCY_CHECKS.md` | Konsistenz-Pruef-Template (K1–K7) | consistency |

### docs/ — Output-Templates (von Skills erzeugt)

| Template | Zweck | Erzeugt von |
|----------|-------|-------------|
| `preflight/PREFLIGHT_TEMPLATE.md` | Preflight-Protokoll (P1–P6 + Argumentationsstruktur) | thesis-preflight |
| `bewertung/BEWERTUNG_TEMPLATE.md` | Bewertungsbericht (R1–R6 Scoring) | thesis-reviewer |
| `post_session/POST_SESSION_TEMPLATE.md` | Post-Session-Verifikation (A–F Checks) | thesis-post-session |
| `Evidenz/EVIDENZ_MATRIX_TEMPLATE.md` | Quellen-Abdeckungsanalyse (3-Tier) | evidence-matrix-builder |

### chapter/ — Per-Kapitel-Artefakte

| Template | Zweck | Referenziert von |
|----------|-------|-----------------|
| `chapter_state.yaml` | Kapitel-Status, Decisions, lade_manifest | resume.py, Alle Skills |
| `project_scaffold.md` | Schritt-fuer-Schritt Setup-Anleitung | — |
