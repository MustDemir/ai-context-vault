# Projekt-Scaffold — Neues Projekt aufsetzen

## Schritt 1: Ordnerstruktur anlegen

```
<projekt>/
├── 00_admin/
│   ├── SOURCE_OF_TRUTH.md     ← aus templates/admin/
│   ├── WORKFLOW_PLAYBOOK.md   ← aus templates/admin/
│   ├── gliederung.md          ← aus templates/admin/
│   ├── asset_naming.md        ← aus templates/admin/
│   └── <expose>.pdf
├── 00_workspace/
│   └── Fulltext_Kapitel/
├── docs/
│   ├── uni_vorgaben/
│   │   └── pruefkatalog.md    ← aus templates/docs/
│   ├── roter_faden_tracker.md ← aus templates/docs/
│   ├── thesis_state.md        (generiert von resume.py)
│   ├── preflight/
│   ├── bewertung/
│   ├── consistency/
│   ├── post_session/
│   ├── session_summaries/
│   └── Evidenz/
├── 01_<kapitel>/
│   ├── chapter_state.yaml     ← aus templates/chapter/
│   ├── session_summaries/
│   └── images/
├── ...
├── 99_inbox_unsorted/
│   └── raw/
├── scripts/                    ← aus ai-context-vault/scripts/
├── plugins/                    ← Plugin-Dateien (.plugin)
├── .env                        (Kopie von .env.example)
├── .gitignore
└── requirements.txt
```

## Schritt 2: chapter_state.yaml pro Kapitel

Kopiere `templates/chapter/chapter_state.yaml` in jeden Kapitelordner
und passe `chapter`, `kapitel` und `lade_manifest` an.

## Schritt 3: SSOTs befuellen

1. `gliederung.md` — Kapitelstruktur und Seitenbudgets eintragen
2. `SOURCE_OF_TRUTH.md` — Primaere Quellen und Pfade definieren
3. `pruefkatalog.md` — Bewertungskriterien der Institution eintragen
4. `roter_faden_tracker.md` — Kernthesen und Bruecken je Kapitel

## Schritt 4: Plugins installieren

1. `thesis-workflow.plugin` in Claude.ai Cowork ziehen
2. Recherche-Plugins nach Bedarf: consensus-plugin, elicit-research, etc.
3. MCP-Connectors in Projekteinstellungen konfigurieren

## Schritt 5: Erster Workflow-Durchlauf

```bash
python3 scripts/resume.py          # Initialen State generieren
# In Cowork: "preflight Kap. 1.1"  # Ersten Preflight ausfuehren
# Arbeiten...
# "session ende"                    # Post-Session-Check
python3 scripts/save.py --input notes.txt --topic auto
```
