# Thesis-Writing Skills — Uebersicht

> Erstellt: 2026-03-06 | Aktualisiert: 2026-03-13 | Status: v2.1 — lade_manifest, Ein-Repo-Architektur

## Architektur

```
Session Start → thesis-session-manager (S1–S5)
                  ↓
              thesis-preflight (P1–P6)
                  ↓ User: "GO"
              thesis-writer (Absatz fuer Absatz)
                  ↓ User: "fertig"
              thesis-post-session (A–F)
                  ↓
Session Ende → thesis-session-manager (E1–E4)

Bei Bedarf:  → thesis-consistency (K1–K7)
             → thesis-reviewer (R1–R6)  ← NEU: Volltext-Bewertung
```

## 6 Skills im Detail

| # | Skill | Trigger | Pruefinstanzen | Pruefobjekt |
|---|-------|---------|---------------|-------------|
| 1 | **thesis-preflight** | "preflight", "kap X.Y schreiben", "pruef erstmal" | P1–P6 | Volltexte (DOCX) + SSOTs |
| 2 | **thesis-writer** | "GO", "FINAL", "schreib absatz", "weiter schreiben" | Absatzweise + Pruefprotokoll | DRAFT.md + Zotero + zitations-finder |
| 3 | **thesis-post-session** | "session ende", "fertig fuer heute", "save session" | A–F | Repo-Artefakte |
| 4 | **thesis-consistency** | "konsistenz pruefen", "cross-check", "terminologie check" | K1–K7 | Volltexte (DOCX) + SSOTs |
| 5 | **thesis-session-manager** | "neue session", "wo waren wir", "resume" | S1–S5 / E1–E4 | chapter_states + resume.py |
| 6 | **thesis-reviewer** | "review kapitel", "bewerte kapitel", "gutachten", "professor-check" | R1–R6 | Volltexte (DOCX) primaer |

## Primaere Pruefobjekte

- **Volltexte:** `00_workspace/Fulltext_Kapitel/*.docx` (Abgabe-Texte, SSOT fuer Fliesstext)
- **Fallback:** `{kapitel_ordner}/{N}_{M}_{thema}_DRAFT.md` (Zwischenstaende, z.B. `4_2_lifecycle_DRAFT.md`)
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

- **Source (Entwicklung):** `genaiops-thesis/.skills/` — hier werden Skills bearbeitet
- **Distribution (Plugin):** `genaiops-thesis/thesis-workflow.plugin` (ZIP)
- **Sync-Richtung:** `.skills/` → `.plugin` (bei Aenderungen Plugin neu packen)
- **Workflow-Scripts:** `genaiops-thesis/scripts/` (resume.py, save.py, reindex.py, workflow_lib.py)

## Externe Abhaengigkeiten

| Dependency | Typ | Herkunft | Benötigt von |
|------------|-----|----------|-------------|
| `zitations-finder` | Skill | Cowork Plugin | thesis-writer (P5), thesis-preflight (P5) |
| `elicit-research` | Skill | Cowork Plugin | thesis-writer (P5), thesis-preflight (P5) |
| Zotero MCP | MCP Server | Cowork Projekteinstellungen | Quellen-Lookup-Kette |
| Semantic Scholar MCP | MCP Server | Cowork Projekteinstellungen | Quellen-Lookup-Kette |

## Aenderungslog

- **v2.1 (2026-03-13):** Per-chapter lade_manifest (pflicht/kontext 2-Tier) in alle 6 Skills integriert; Zwei-Repo → Ein-Repo-Architektur korrigiert (ai-context-vault-Referenzen entfernt); Scripts aus __pycache__ nach scripts/ verschoben; REPO_ROOT in workflow_lib.py gefixed; Uni-Vorgaben (pruefkatalog.md) als universelle pflicht in allen 8 chapter_states
- **v2.0 (2026-03-08):** thesis-reviewer Skill hinzugefuegt (R1–R6); thesis-consistency K7 ergaenzt; alle Skills auf Volltext-DOCX als primaeres Pruefobjekt umgestellt; Quellen-Lookup-Kette vereinheitlicht (zitations-finder → Zotero → Elicit → SemanticScholar → Consensus); roter_faden_tracker.md + pruefkatalog.md als neue SSOTs
- **v1.0 (2026-03-06):** Initiale Version mit 5 Skills
