---
name: thesis-preflight
description: >
  Systematischer Pre-Flight-Check VOR dem Schreiben eines Thesis-Abschnitts. Durchläuft 6 Prüfinstanzen
  (Exposé, Kapiteltexte, Sessions/States, Entscheidungen, Quellen, Uni-Anforderungen) und erstellt ein
  Preflight-Protokoll mit Argumentationsstruktur, Inhalts-Checklist und Negativ-Checklist.
  Trigger bei: "preflight", "neuer abschnitt", "kap X.Y schreiben", "GO vorbereiten", "prüf erstmal",
  "was muss ich beachten für", "vorbereitung für kapitel", "checklist für abschnitt".
  Auch triggern wenn der User einen neuen Abschnitt beginnen will ohne explizit "preflight" zu sagen —
  jeder Schreibauftrag für einen neuen Thesis-Abschnitt sollte mit diesem Skill starten.
---

# Thesis Preflight Check

Dieser Skill stellt sicher, dass Claude VOR dem Schreiben eines Thesis-Abschnitts die gesamte
Wissensbasis systematisch durchgeht. Ohne diesen Check fehlen Inhalte, Entscheidungen werden
ignoriert, und die Konsistenz zwischen Kapiteln leidet.

## Warum das wichtig ist

Die Masterarbeit hat eine komplexe Abhängigkeitsstruktur: Entscheidungen in Kap. 4 beeinflussen
Kap. 5, das Exposé definiert den Rahmen, die Gliederung gibt Seitenbudgets vor, und
Critical Definitions müssen konsistent durchgehalten werden. Ein einziger vergessener Check
kann zu Widersprüchen führen, die später aufwändig korrigiert werden müssen.

## Referenz-Dateien laden (PFLICHT bei jedem Aufruf)

Vor dem Durchlauf der 6 Pruefinstanzen diese Referenz-Dateien lesen:
- `.skills/thesis-preflight/references/critical_definitions.md` — Critical Definitions Schnellreferenz
- `.skills/thesis-preflight/references/checklist_template.md` — Preflight-Protokoll Template

## Workflow: 6 Prüfinstanzen in Reihenfolge

Identifiziere zuerst den **Zielabschnitt** (z.B. "Kap. 2.1") aus dem User-Input oder dem
`chapter_state.yaml` des Zielkapitels (Feld `next_steps`).

Dann durchlaufe die 6 Prüfinstanzen in dieser Reihenfolge. Für jede Instanz: die angegebenen
Dateien lesen, die Prüffragen beantworten, und Ergebnisse sammeln.

### P0 — Kontext-Fokussierung via lade_manifest (VOR allen Pruefinstanzen)

Lies zuerst das `lade_manifest` aus dem Zielkapitel-`chapter_state.yaml`:

- **`pflicht`-Dateien** → als VOLLTEXT laden (DOCXs, DRAFTs, Entscheidungspapiere, Uni-Vorgaben). Diese haben hoechste Prioritaet und liefern den inhaltlichen Kontext.
- **`kontext`-Kapitel** → nur deren `chapter_state.yaml` lesen (Ueberblick, keine Volltexte). Reicht fuer Abhaengigkeitsbewusstsein.

**Universelle pflicht-Dateien** (in jedem Kapitel vorhanden):
- Kap. 3 DOCX (DSR/Forschungsdesign)
- `docs/uni_vorgaben/pruefkatalog.md` (Uni-Vorgaben)

Das lade_manifest **ergaenzt** die Dateilisten in P1–P6 — es ersetzt sie NICHT.
Wenn eine Pruefinstanz explizit eine Datei fordert, wird diese gelesen unabhaengig vom lade_manifest.

### P1 — Exposé + README

Lese diese Dateien:
- `00_admin/DMT_Demir_Exposé_2009670_final.pdf` (primäre Exposé-Quelle im Repo)
- `00_admin/README.md` (Projektübersicht und Repo-Struktur)

Beantworte:
- Steht der geplante Abschnitt im Einklang mit dem Exposé?
- Gibt es im Exposé Formulierungen/Inhalte, die übernommen werden können?
- Hat sich der Scope seit dem Exposé verändert? Wo ist die Änderung dokumentiert?

### P2 — ALLE Volltexte + ALLE SSOTs (PFLICHT — nichts ueberspringen!)

**WICHTIG:** P2 ist die umfangreichste Pruefinstanz. Du MUSST alle unten gelisteten Dateien
tatsaechlich lesen — nicht nur das Vorgaengerkapitel. Ohne vollstaendige Lektuere fehlen
Begriffe, Definitionen und Abhaengigkeiten, die zu Inkonsistenzen fuehren.

Die SOT-Hierarchie bestimmt, welche Quellen bei Widersprüchen gewinnen:
`gliederung_v3.md > Kap. 3 DOCX > Kap. 4 DOCX > Entscheidungsregister > Exposé`

#### Schritt 1: ALLE geschriebenen Volltexte lesen (PFLICHT)

Lese JEDEN Volltext der bereits existiert — nicht nur den Vorgaenger:
- `00_workspace/Fulltext_Kapitel/Kapitel 1 Einleitung.docx` (PFLICHT)
- `00_workspace/Fulltext_Kapitel/Kapitel 2 Theoretische Grundlagen.docx` (PFLICHT)
- `00_workspace/Fulltext_Kapitel/Kapitel 3 Forschungsdesign_und_Methodik.docx` (PFLICHT)
- `00_workspace/Fulltext_Kapitel/Kapitel 4 Anforderungen.docx` (PFLICHT)
- `00_workspace/Fulltext_Kapitel/Kapitel 5 Architectur Entwicklung.docx` (PFLICHT, falls vorhanden)
- Fallback wenn DOCX nicht lesbar — DRAFT-Pfad-Aufloesung (3-Stufen):
  1. `{kapitel_ordner}/arbeitsmaterial/drafts/Kap{N}_*_DRAFT.md` (primaer)
  2. `{kapitel_ordner}/KAPITEL_{N}_*_DRAFT.md` (Fallback, Root)
  3. `{kapitel_ordner}/legacy/*_DRAFT.md` (Legacy, nur lesen)

#### Schritt 2: ALLE SSOTs + Preflight-Protokolle lesen (PFLICHT)

- `docs/roter_faden_tracker.md` — Bruecken-Definitionen und Kernthesen ALLER Kapitel
- `00_admin/gliederung_v3.md` — Kapitelstruktur, Seitenbudgets
- `00_admin/SOURCE_OF_TRUTH.md` — Master-SSOT-Verzeichnis, Datei-Hierarchie
- `docs/uni_vorgaben/pruefkatalog.md` — PK-Codes fuer Uni-Anforderungen
- `{kapitel_ordner}/KONSISTENZ_UEBERBLICK_KAP{N}.md` (falls vorhanden)
- `{kapitel_ordner}/INHALTSPLAN_KAP{N}.md` (falls vorhanden)
- `{kapitel_ordner}/chapter_state.yaml` — Detaillierter Kapitel-Status (done, next_steps, decisions)
- **`docs/preflight/PREFLIGHT_KAP{N}_*.md`** — ALLE bisherigen Preflight-Protokolle des Zielkapitels UND verwandter Kapitel lesen! Diese enthalten Argumentationsstrukturen, Quellen-Zuordnungen und Negativ-Checklisten aus frueheren Preflights.

#### Schritt 3: Prueffragen beantworten

- Welche Begriffe/Definitionen aus ALLEN bereits geschriebenen Kapiteln muessen verwendet werden?
- Gibt es Forward-References? Existiert das Ziel oder ist es in der Gliederung geplant?
- Stimmt die Argumentationslinie mit der Gliederung ueberein?
- **Roter Faden rueckwaerts:** Lese den VOLLTEXT des Vorgaengerkapitels — wie endet es inhaltlich? Welche Erwartung wird geweckt? Knuepft der neue Abschnitt nahtlos an?
- **Roter Faden vorwaerts:** Was erwartet das Nachfolgerkapitel (aus chapter_state/roter_faden_tracker)? Bereitet der geplante Abschnitt darauf vor?
- **Konsistenz:** Widersprechen geplante Inhalte IRGENDEINEM bestehenden Volltext (nicht nur Vorgaenger)?
- **Redundanz:** Wurde ein Begriff/Konzept bereits in einem frueheren Kapitel definiert? Wenn ja: NICHT wiederholen, sondern verweisen.

### P3 — Session Summaries + chapter_state + relevante Dateien

Lese diese Dateien:
- `{kapitel_ordner}/chapter_state.yaml` (Zielkapitel)
- Alle relevanten `chapter_state.yaml` (abhängige Kapitel)
- `{kapitel_ordner}/session_summaries/*.yaml` (bisherige Diskussionen)
- `99_inbox_unsorted/session_summaries/*.yaml` (kapitelübergreifend)

Prüfe außerdem ob die chapter_state "Definition of Ready" erfüllt ist:
- Hat das Zielkapitel ausgefüllte Felder (done, current_focus, key_sources)?
- Wenn nicht: **WARNUNG** — chapter_state muss zuerst initialisiert werden.

Beantworte:
- Gibt es in Session Summaries Inhalte, die in diesen Abschnitt gehören?
- Sind alle chapter_state-Entscheidungen berücksichtigt?

### P4 — Entscheidungspapiere + Entscheidungsregister

Lese diese Dateien:
- `docs/thesis_state.md` — Alle D_xxx Entscheidungen, Critical Definitions
- `docs/SSOT_ROTER_FADEN_ANALYSE.md` — Cross-chapter Impact
- `docs/ENTSCHEIDUNGSPAPIER_KAP{N}.md` — Kapitelspezifische Designentscheidungen (N = Zielkapitel + Abhaengigkeiten, z.B. KAP4, KAP5)
- `00_admin/SOURCE_OF_TRUTH.md` — SOT-Hierarchie

Beantworte:
- Welche Entscheidungen (D_xxx) betreffen diesen Abschnitt direkt?
- Gibt es offene Entscheidungen, die VOR dem Schreiben geklärt werden müssen?
- Muss eine NEUE Entscheidung getroffen werden? → Dokumentieren BEVOR geschrieben wird
- Sind die Critical Definitions eingehalten? (Enforcement ≠ Dokumentation, Deployer-Scope, etc.)

### P5 — Quellen-Papers

Nutze diese Tools in dieser Reihenfolge (Fallback-Kette):
1. `zitations-finder` Skill — Belegstellen im PDF finden und verifizieren
2. `zotero_search_items` → `zotero_item_fulltext` (Zotero-Bibliothek)
3. Uploads: `/sessions/.../mnt/uploads/` (hochgeladene PDFs)
4. `elicit-research` Skill (Elicit-Suche)
5. `semanticSearch` MCP Tool (Semantic Scholar)
6. `mcp__claude_ai_Consensus__search` (Consensus API)
7. Wenn nirgends auffindbar: ❌ markieren, Alternative suchen

Beantworte:
- Welche Quellen MÜSSEN in diesem Abschnitt zitiert werden (laut Gliederung/Exposé)?
- Gibt es neue Quellen seit dem Exposé?
- Sind alle Zitate APA7 mit Seitenangabe?

### P6 — Uni-Anforderungen + DSR-Verankerung

Prüfe:
- **Seitenbudget:** gliederung_v3.md Budget vs. bisherige Wortanzahl im Kapitel
- **Formatvorgaben:** Nummerierung nur bis 2. Ebene, keine formalen Überleitungen
- **SRH-Leitfaden:** "Formales Vorgehen NICHT explizit beschreiben"
- **Zitationsdichte:** Hohe Zitationsdichte, jede Behauptung belegt
- **DSR-Phasen-Mapping:** In welcher DSR-Phase (Hevner/Peffers) befindet sich der Abschnitt?
- **Scope-Drift-Detection:** Geplanter Inhalt vs. Exposé-Erwartung — Drift vorhanden?

---

## Ausgabeformat: Preflight-Protokoll

Nach Durchlauf aller 6 Prüfinstanzen, erstelle das Protokoll in diesem Format:

```
## Preflight-Protokoll: Kap. X.Y — [Titel]

### Ergebnis P1 (Exposé): [✅ konsistent / ⚠ Abweichung: ...]
### Ergebnis P2 (Kapiteltexte): [Relevante Begriffe/Definitionen: ...]
### Ergebnis P3 (Sessions/Files): [Relevante Inhalte: ...]
### Ergebnis P4 (Entscheidungen): [Betroffene D_xxx: ...]
### Ergebnis P5 (Quellen): [Pflicht-Zitate: ...]
### Ergebnis P6 (Uni): [Seitenbudget: X Wörter / X Seiten]

### Synthese — Argumentationsstruktur für Kap. X.Y:

**Brücke von Kap. X.(Y-1):** [Wie endet der vorherige Abschnitt?]

| Absatz | Argumentativer Move | Logik | Brücke zum nächsten |
|--------|---------------------|-------|---------------------|
| 1 | [z.B. Ziel definieren] | [Schließt an Problemstellung an] | [→ leitet über zu...] |
| N | [z.B. Beitrag formulieren] | [Evaluation belegt Relevanz] | [→ Brücke zu X.(Y+1)] |

**Brücke zu Kap. X.(Y+1):** [Wie bereitet der letzte Satz den nächsten Abschnitt vor?]

### Inhalts-Checklist:
☐ Inhalt 1
☐ Inhalt 2

### Negativ-Checklist — Was darf NICHT in Kap. X.Y:
- ❌ [Inhalt der in anderes Kapitel gehört]
- ❌ [Deployer-Scope beachten: keine Provider-Perspektive (Art. 16)]

### Pflicht-Zitate:
- (Autor, Jahr) — für [Thema]

### Offene Fragen (vor Schreiben klären):
- ...

→ Bereit für "GO"
```

Speichere das Preflight-Protokoll als `docs/preflight/PREFLIGHT_KAP{X}_{Y}_{TITEL}.md`.

---

## Zusätzliche Regeln

- Kein Fließtext ohne "GO" oder "FINAL" — der Skill endet mit dem Preflight-Protokoll
- Default Output-Level: L1 (10–15 Bullets + max. 3 kritische Fragen)
- Deployer-Scope (Art. 26) — nicht Provider (Art. 16), kein Retirement
- Wenn User "bitte lese die Entscheidungspapier genau durch" sagt: P4 besonders gründlich
