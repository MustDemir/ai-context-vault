# Thesis Workflow Skills — Uebersicht

> Erstellt: 2026-03-06 | Aktualisiert: 2026-04-01 | Status: v2.3.0 — 7 Skills, Evidence-Matrix, Consensus-Integration

## Architektur

```
Session Start → thesis-session-manager (S1–S5)
                  ↓
              thesis-preflight (P1–P6)
                  ↓ User: "GO"
              thesis-evidence-support (Belegpruefung + Quellenverifikation)
                  ↓ User: "fertig"
              thesis-post-session (A–F)
                  ↓
Session Ende → thesis-session-manager (E1–E4)

Bei Bedarf:  → thesis-consistency (K1–K7)
             → thesis-reviewer (R1–R6)
             → evidence-matrix-builder (Quellen-Abdeckungsanalyse)
```

## 7 Skills im Detail

| # | Skill | Trigger | Pruefinstanzen | Pruefobjekt |
|---|-------|---------|---------------|-------------|
| 1 | **thesis-preflight** | "preflight", "kap X.Y", "pruef erstmal" | P1–P6 | Volltexte (DOCX) + SSOTs |
| 2 | **thesis-evidence-support** | "GO", "FINAL", "beleg pruefen" | Belegpruefung + Pruefprotokoll | Quellen + Zotero + zitations-finder |
| 3 | **thesis-post-session** | "session ende", "fertig fuer heute", "save session" | A–F | Repo-Artefakte |
| 4 | **thesis-consistency** | "konsistenz pruefen", "cross-check", "terminologie check" | K1–K7 | Volltexte (DOCX) + SSOTs |
| 5 | **thesis-session-manager** | "neue session", "wo waren wir", "resume" | S1–S5 / E1–E4 | chapter_states + resume.py |
| 6 | **thesis-reviewer** | "review kapitel", "bewerte kapitel", "gutachten" | R1–R6 | Volltexte (DOCX) primaer |
| 7 | **evidence-matrix-builder** | "evidenz matrix", "quellen bewerten", "source coverage" | Tier-Kategorisierung | PDF-Quellen + Forschungsfragen |

## Primaere Pruefobjekte

- **Volltexte:** `00_workspace/Fulltext_Kapitel/*.docx` (Abgabe-Texte, SSOT fuer Fliesstext)
- **Fallback:** `{kapitel_ordner}/{N}_{M}_{thema}_DRAFT.md` (Zwischenstaende)
- **Roter Faden:** `docs/roter_faden_tracker.md`
- **Uni-Vorgaben:** `docs/uni_vorgaben/pruefkatalog.md`
- **Decisions/Definitionen:** `docs/thesis_state.md`

## Quellen-Lookup-Kette (fuer alle quellenbasierten Skills)

```
1. zitations-finder Skill (Belegstellen im PDF verifizieren)
2. zotero_search_items → zotero_item_fulltext (Zotero MCP)
3. elicit-research Skill (Elicit-Suche)
4. semanticSearch MCP (Semantic Scholar)
5. mcp__claude_ai_Consensus__search (Consensus API)
```

## Status-Enum (verbindlich)

```
planned → in_progress → draft → review → final
```

## Standort & Sync-Richtung

- **Source (Entwicklung):** `ai-context-vault/skills/` + `genaiops-thesis/.skills/`
- **Distribution (Plugin):** `ai-context-vault/plugins/thesis-workflow.plugin` (ZIP)
- **Sync-Richtung:** `skills/` → `.plugin` (bei Aenderungen Plugin neu packen)
- **Workflow-Scripts:** `scripts/` (resume.py, save.py, reindex.py, workflow_lib.py)

## Externe Abhaengigkeiten

| Dependency | Typ | Herkunft | Benötigt von |
|------------|-----|----------|-------------|
| `zitations-finder` | Skill/Plugin | Cowork Plugin | evidence-support, preflight (P5) |
| `elicit-research` | Skill/Plugin | Cowork Plugin | evidence-support, preflight (P5) |
| `consensus-plugin` | Plugin | Cowork Plugin | evidence-matrix-builder, Quellen-Lookup |
| Zotero MCP | MCP Server | Cowork Projekteinstellungen | Quellen-Lookup-Kette |
| Semantic Scholar MCP | MCP Server | Cowork Projekteinstellungen | Quellen-Lookup-Kette |
| Consensus MCP | MCP Server | consensus-plugin | Quellen-Lookup-Kette |

## Aenderungslog

- **v2.3.0 (2026-04-01):** evidence-matrix-builder als 7. Skill hinzugefuegt; consensus-plugin als externe Abhaengigkeit integriert; SKILL_OVERVIEW auf 7 Skills aktualisiert; ai-context-vault als primaerer Standort fuer Source + Distribution
- **v2.1 (2026-03-13):** Per-chapter lade_manifest (pflicht/kontext 2-Tier) in alle Skills integriert; Ein-Repo-Architektur; Uni-Vorgaben als universelle pflicht
- **v2.0 (2026-03-08):** thesis-reviewer hinzugefuegt (R1–R6); Quellen-Lookup-Kette vereinheitlicht; roter_faden_tracker.md + pruefkatalog.md als neue SSOTs
- **v1.0 (2026-03-06):** Initiale Version mit 5 Skills
